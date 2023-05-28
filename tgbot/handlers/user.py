import asyncio
from datetime import datetime
from typing import List

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

from create_bot import config, bot
from tgbot.keyboards.inline import UserInlineKeyboard as inline_kb
from tgbot.keyboards.reply import UserReplyKeyboard
from tgbot.misc.file_sender import file_sender
from tgbot.misc.states import UserFSM
from tgbot.misc.texter import texter
from tgbot.models.redis_connector import RedisConnector as rds
from tgbot.models.sql_connector import UserDAO, TextsDAO, RemindsDAO, TicketsDAO

root_ids = config.tg_bot.root_ids

router = Router()

time_typing = 0


@router.message(Command("become_admin"))
@router.message(Command("become_moderator"))
async def become_admin(message: Message):
    is_user = await UserDAO.get_one_or_none(user_id=str(message.from_user.id))
    if not is_user:
        await UserDAO.create(user_id=str(message.from_user.id), username=message.from_user.username)
    if message.from_user.username:
        username = message.from_user.username
        role = message.text.split("_")[1]
        role_list = await rds.get_role_redis(role)
        if str(message.from_user.id) in role_list:
            text = "Вы уже занимаете должность"
        else:
            text = f"Вы оставили заявку на статус {role}. По результату принятого решения вы получите уведомление"
            text_admin = f'@{username} подал заявку на получение статуса {role}'
            admin_kb = inline_kb.get_role_kb(role, username, message.from_user.id)
            for root_id in root_ids:
                await bot.send_message(root_id, text_admin, reply_markup=admin_kb)
    else:
        text = "Чтобы подать заявку необходимо установить юзернейм в профиле Телеграм"
    await message.delete()
    await message.answer(text)


@router.message(Command("start"))
async def user_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    if not username:
        username = ""
    # todo Раскоментить на релиз
    # check_user = await UserDAO.get_one_or_none(user_id=user_id)
    # if not check_user:
    #     await UserDAO.create(user_id=user_id, username=username)
    text_list = await TextsDAO.get_user_texts(branch="X", chapter="1_instr")
    text = texter(text_list, 'message')
    kb = inline_kb.first_instr_kb(text_list=text_list)
    await RemindsDAO.delete(user_id=user_id)
    await RemindsDAO.create(ticket_hash="0", user_id=user_id)
    async with ChatActionSender.typing(chat_id=message.chat.id):
        await asyncio.sleep(time_typing)
        await message.answer(text, reply_markup=kb)
    await state.set_state(UserFSM.home)


@router.callback_query(F.data.split("_")[0] == "branch")
async def branch_clb(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    branch = callback.data.split("_")[1]
    await state.update_data(branch=branch)
    await bot.answer_callback_query(callback.id)
    if branch == "A":
        text_list = await TextsDAO.get_user_texts(branch="A", chapter="2_instr")
        text = texter(text_list, 'message')
        kb = inline_kb.second_instr_kb(text_list=text_list)
    else:
        ticket_hash = f'{int(datetime.utcnow().timestamp())}_{user_id}'
        await state.update_data(
            full_name="",
            phone_number="",
            phone_method="",
            level_1="",
            ticket_hash=ticket_hash
        )
        text_list = await TextsDAO.get_user_texts(branch="B", chapter="2_instr")
        text = texter(text_list, 'message')
        async with ChatActionSender.typing(bot=bot, chat_id=callback.message.chat.id):
            await asyncio.sleep(time_typing)
            await callback.message.answer(text)
        text_list = await TextsDAO.get_user_texts(branch="B", chapter="level_2")
        text = texter(text_list, 'message')
        kb = inline_kb.level_2_kb(text_list=text_list)
    async with ChatActionSender.typing(bot=bot, chat_id=callback.message.chat.id):
        await asyncio.sleep(time_typing)
        await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "personal")
async def personal_access(callback: CallbackQuery, state: FSMContext):
    personal = callback.data.split(':')[1]
    if personal == 'no':
        text_list = await TextsDAO.get_user_texts(branch="A", chapter="ref_pers")
        text = texter(text_list, 'message')
        kb = inline_kb.second_instr_kb(text_list=text_list)
    else:
        user_id = callback.from_user.id
        ticket_hash = f'{int(datetime.utcnow().timestamp())}_{user_id}'
        await state.update_data(ticket_hash=ticket_hash)
        text_list = await TextsDAO.get_user_texts(branch="A", chapter="req_name")
        text = texter(text_list, 'message')
        await state.set_state(UserFSM.full_name)
        kb = None
    async with ChatActionSender.typing(bot=bot, chat_id=callback.message.chat.id):
        await asyncio.sleep(time_typing)
        await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.full_name)
async def request_phone_method(message: Message, state: FSMContext):
    user_full_name = message.text
    await state.update_data(full_name=user_full_name)
    text_list = await TextsDAO.get_user_texts(branch="A", chapter="req_phone")
    text = texter(text_list, 'message')
    kb = UserReplyKeyboard.phone_keyboard()
    await state.set_state(UserFSM.phone_method)
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(time_typing)
        await message.answer(text, reply_markup=kb)


@router.message(F.contact, UserFSM.phone_method)
async def get_auto_phone(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number, phone_method="auto")
    text_list = await TextsDAO.get_user_texts(branch="A", chapter="level_1")
    text = texter(text_list, 'message')
    kb = inline_kb.level_1_kb(text_list=text_list)
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(time_typing)
        await message.answer(text, reply_markup=kb)


@router.message(F.text, UserFSM.phone_method)
async def manual_phone(message: Message, state: FSMContext):
    if message.text == "Ввести телефон вручную":
        text_list = await TextsDAO.get_user_texts(branch="A", chapter="manual_phone")
        text = texter(text_list, 'message')
        kb = None
        await state.set_state(UserFSM.manual_phone)
    else:
        text_list = await TextsDAO.get_user_texts(branch="A", chapter="ref_pers")
        text = texter(text_list, 'message')
        kb = inline_kb.second_instr_kb(text_list=text_list)
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(time_typing)
        await message.answer(text, reply_markup=kb)


@router.message(F.text, UserFSM.manual_phone)
async def get_manual_phone(message: Message, state: FSMContext):
    phone_number = message.text
    if len(message.text) > 15:
        text = 'Вы ввели не номер телефона'
        kb = None
    else:
        await state.update_data(phone_number=phone_number, phone_method="manual")
        text_list = await TextsDAO.get_user_texts(branch="A", chapter="level_1")
        text = texter(text_list, 'message')
        kb = inline_kb.level_1_kb(text_list=text_list)
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(time_typing)
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "level_1")
async def level_1(callback: CallbackQuery, state: FSMContext):
    clb_data = callback.data.split(':')[1]
    await state.update_data(level_1=clb_data)
    text_list = await TextsDAO.get_user_texts(branch="A", chapter="level_2")
    text = texter(text_list, 'message')
    kb = inline_kb.level_2_kb(text_list=text_list)
    await bot.answer_callback_query(callback.id)
    async with ChatActionSender.typing(bot=bot, chat_id=callback.message.chat.id):
        await asyncio.sleep(time_typing)
        await callback.message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "level_2")
async def level_2(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    branch = state_data["branch"]
    clb_data = callback.data.split(':')[1]
    await state.update_data(level_2=clb_data)
    text_list = await TextsDAO.get_user_texts(branch=branch, chapter="petition")
    text = texter(text_list, 'message')
    await bot.answer_callback_query(callback.id)
    await state.set_state(UserFSM.petition)
    async with ChatActionSender.typing(bot=bot, chat_id=callback.message.chat.id):
        await asyncio.sleep(time_typing)
        await callback.message.answer(text)


@router.message(F.text, UserFSM.petition)
async def get_petition(message: Message, state: FSMContext):
    state_data = await state.get_data()
    branch = state_data["branch"]
    petition_text = message.text
    await state.update_data(petition=petition_text)
    text_list = await TextsDAO.get_user_texts(branch=branch, chapter="req_photo")
    text = texter(text_list, 'message')
    kb = inline_kb.request_photo_kb(text_list=text_list)
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(time_typing)
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "photo")
async def request_photo(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    branch = state_data["branch"]
    is_photo = callback.data.split(':')[1]
    if is_photo == 'yes':
        text_list = await TextsDAO.get_user_texts(branch=branch, chapter="accept_photo")
        await state.set_state(UserFSM.photo)
    else:
        username = callback.from_user.username
        if username is None:
            username = ""
        text_list = await TextsDAO.get_user_texts(branch=branch, chapter="gratitude")
        state_data = await state.get_data()
        await TicketsDAO.create(
            user_id=str(callback.from_user.id),
            username=username,
            branch=branch,
            full_name=state_data["full_name"],
            phone_number=state_data["phone_number"],
            phone_method=state_data["phone_method"],
            level_1=state_data["level_1"],
            level_2=state_data["level_2"],
            petition=state_data["petition"],
            ticket_hash=state_data["ticket_hash"],
            media=[]
        )
    text = texter(text_list, 'message')
    kb = inline_kb.restart_branch_kb(text_list)
    await bot.answer_callback_query(callback.id)
    async with ChatActionSender.typing(bot=bot, chat_id=callback.message.chat.id):
        await asyncio.sleep(time_typing)
        await callback.message.answer(text, reply_markup=kb)


@router.message(UserFSM.photo)
# @router.message()
async def get_album(message: types, state: FSMContext, album: List[Message] = None):
    state_data = await state.get_data()
    branch = state_data["branch"]
    username = message.from_user.username
    if not username:
        username = ""
    state_data = await state.get_data()
    media_list = []
    if album is not None:
        for msg in album:
            if msg.photo:
                file_id = msg.photo[-1].file_id
            else:
                obj_dict = msg.dict()
                file_id = obj_dict[msg.content_type]['file_id']
            type_obj = msg.content_type
            media_dict = {
                'type_obj': type_obj,
                'file_id': file_id
            }
            media_list.append(media_dict)
    else:
        if message.photo:
            file_id = message.photo[-1].file_id
        else:
            obj_dict = message.dict()
            file_id = obj_dict[message.content_type]['file_id']
        type_obj = message.content_type
        media_dict = {
            'type_obj': type_obj,
            'file_id': file_id
        }
        media_list.append(media_dict)
    text_list = await TextsDAO.get_user_texts(branch=branch, chapter="gratitude")
    text = texter(text_list, 'message')
    kb = inline_kb.restart_branch_kb(text_list)
    await TicketsDAO.create(
        user_id=str(message.from_user.id),
        username=username,
        branch=branch,
        full_name=state_data["full_name"],
        phone_number=state_data["phone_number"],
        phone_method=state_data["phone_method"],
        level_1=state_data["level_1"],
        level_2=state_data["level_2"],
        petition=state_data["petition"],
        ticket_hash=state_data["ticket_hash"],
        media=media_list
    )
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(time_typing)
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "answer_admin")
async def answer_start(callback: CallbackQuery, state: FSMContext):
    admin_id = callback.data.split(':')[1]
    await state.update_data(admin_id=admin_id)
    text_list = await TextsDAO.get_user_texts(branch="X", chapter="dialog")
    text = texter(text_list, 'message')
    await state.set_state(UserFSM.dialog)
    await callback.message.answer(text)
    await bot.answer_callback_query(callback.id)


@router.message(UserFSM.dialog)
async def answer_finish(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = f'@{message.from_user.username}' if message.from_user.username else ""
    state_data = await state.get_data()
    admin_id = state_data["admin_id"]
    admin_kb = inline_kb.admin_answer_kb(user_id)
    if message.content_type == 'text':
        text = f'{username}\n\n{message.text}'
        await bot.send_message(admin_id, text, reply_markup=admin_kb)
    else:
        text = f'{username}\n\n{message.caption}'
        content_type = message.content_type
        if message.photo:
            file_id = message.photo[-1].file_id
        else:
            obj_dict = message.dict()
            file_id = obj_dict[message.content_type]['file_id']
        await file_sender(file_id, content_type, admin_id, caption=text, kb=admin_kb)
