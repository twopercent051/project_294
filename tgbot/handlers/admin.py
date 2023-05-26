from datetime import timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router, types

from create_bot import bot
from tgbot.filters.admin import RootFilter, AdminFilter, ModeratorFilter
from tgbot.keyboards.inline import AdminInlineKeyboard as inline_kb
from tgbot.misc.file_sender import file_sender
from tgbot.misc.states import AdminFSM
from tgbot.models.redis_connector import RedisConnector as rds
from tgbot.models.sql_connector import UserDAO, TextsDAO, TicketsDAO

root_router = Router()
admin_router = Router()
moderator_router = Router()

root_router.message.filter(RootFilter())
admin_router.message.filter(AdminFilter())
moderator_router.message.filter(ModeratorFilter())

root_router.callback_query.filter(RootFilter())
admin_router.callback_query.filter(AdminFilter())
moderator_router.callback_query.filter(ModeratorFilter())


@root_router.callback_query(F.data.split(":")[0] == "dec")
async def roles_decision(callback: CallbackQuery):
    decision = callback.data.split("|")[0].split(":")[1]
    user_id = callback.data.split("|")[1].split(":")[1]
    username = callback.data.split("|")[2].split(":")[1]
    role = callback.data.split("|")[3].split(":")[1]
    if role == 'moderator':
        text_role = 'модераторов'
    else:
        text_role = 'администраторов'
    if decision == 'a':
        current_role_list = await rds.get_role_redis(role)
        if user_id in current_role_list:
            admin_text = f'Пользователь @{username} уже добавлен в список {text_role}'
            kb = inline_kb.home_kb()
            await callback.message.answer(admin_text, reply_markup=kb)
            await bot.answer_callback_query(callback.id)
            return
        else:
            admin_text = f'Пользователь @{username} успешно добавлен в список {text_role}'
            user_text = f'⚠️<b> Сообщение от администрации</b>\n\n Вы теперь в списке {text_role}! Нажмите ' \
                        'кнопку под этим  сообщением 👇'
        await rds.create_role_redis(user_id, role)
    else:
        admin_text = f'Пользователю @{username} отказано в получении статуса'
        user_text = '⚠️<b> Сообщение от администрации</b>\n\n Вам отказано в получении статуса. Нажмите кнопку под ' \
                    'этим сообщением 👇'
    kb = inline_kb.home_kb()
    await bot.send_message(user_id, user_text, reply_markup=kb)
    await callback.message.answer(admin_text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@root_router.message(Command("start"))
async def main_menu(message: Message, state: FSMContext):
    text = "Здравствуйте! Вы вошли как супер-администратор"
    kb = inline_kb.main_menu_kb('root')
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@root_router.callback_query(F.data == "home")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    text = "Здравствуйте! Вы вошли как супер-администратор"
    kb = inline_kb.main_menu_kb('root')
    await state.set_state(AdminFSM.home)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@admin_router.message(Command("start"))
async def main_menu(message: Message, state: FSMContext):
    text = "Здравствуйте! Вы вошли как администратор"
    kb = inline_kb.main_menu_kb('admin')
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@admin_router.callback_query(F.data == "home")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    text = "Здравствуйте! Вы вошли как администратор"
    kb = inline_kb.main_menu_kb('admin')
    await state.set_state(AdminFSM.home)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@moderator_router.message(Command("start"))
async def main_menu(message: Message, state: FSMContext):
    text = "Здравствуйте! Вы вошли как модератор"
    kb = inline_kb.main_menu_kb('moderator')
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@moderator_router.callback_query(F.data == "home")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    text = "Здравствуйте! Вы вошли как модератор"
    kb = inline_kb.main_menu_kb('moderator')
    await state.set_state(AdminFSM.home)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@root_router.callback_query(F.data.split(":")[0] == "list")
async def roles_list(callback: CallbackQuery):
    role = callback.data.split(":")[1]
    admin_ids = await rds.get_role_redis(role)
    admin_usernames = []
    for admin_id in admin_ids:
        admin = await UserDAO.get_one_or_none(user_id=str(admin_id))
        admin_usernames.append(admin["username"])
    if role == 'moderator':
        text_role = 'модераторов'
    else:
        text_role = 'админов'
    text = f'Список действующих {text_role}:'
    kb = inline_kb.roles_list_kb(role=role, users=admin_usernames)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@root_router.callback_query(F.data.split(":")[0] == "admin")
@root_router.callback_query(F.data.split(":")[0] == "moderator")
async def profile_user(callback: CallbackQuery):
    role = callback.data.split(":")[0]
    username = callback.data.split(":")[1]
    profile = await UserDAO.get_one_or_none(username=username)
    text = f'<b>Роль:</b> {role}\n<b>Username:</b> @{username}'
    kb = inline_kb.profile_kb(user_id=profile["username"], role=role)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@root_router.callback_query(F.data.split(":")[0] == "delete")
async def delete_user(callback: CallbackQuery):
    role = callback.data.split("|")[0].split(":")[1]
    username = callback.data.split("|")[1].split(":")[1]
    text = f'Вы действительно хотите удалить {username}?'
    kb = inline_kb.accept_deleting_kb(username=username, role=role)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@root_router.callback_query(F.data.split(":")[0] == "accept_deleting")
async def accept_delete(callback: CallbackQuery):
    role = callback.data.split("|")[0].split(":")[1]
    username = callback.data.split("|")[1].split(":")[1]
    profile = await UserDAO.get_one_or_none(username=username)
    text = f'@{username} успешно удалён'
    kb = inline_kb.home_kb()
    await rds.delete_role_redis(user_id=profile["user_id"], role=role)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@admin_router.callback_query(F.data == "edition")
async def edition_text(callback: CallbackQuery, state: FSMContext):
    text = 'Выберите ветку'
    kb = inline_kb.edition_lvl_1()
    await state.set_state(AdminFSM.home)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@admin_router.callback_query(F.data.split(":")[0] == "edit")
async def edition_text(callback: CallbackQuery, state: FSMContext):
    lvl = callback.data.split('|')[0].split(':')[1]
    branch = callback.data.split('|')[1].split(':')[1]
    if lvl == 'lvl_1':
        text = 'Выберите раздел редактирования'
        kb = inline_kb.edition_lvl_2(branch)
    elif lvl == "lvl_2":
        chapter = callback.data.split('|')[2].split(':')[1]
        text = "Выберите объект"
        kb = inline_kb.edition_lvl_3(branch=branch, chapter=chapter)
    else:
        subject = callback.data.split('|')[3].split(':')[1]
        chapter = callback.data.split('|')[2].split(':')[1]
        obj_in_table = f"branch:{branch}|chapter:{chapter}|subject:{subject}"
        current_text = await TextsDAO.get_one_or_none(subject=obj_in_table)
        if current_text is None:
            text = 'Пустое значение. Введите новое значение'
        else:
            text = f'Сейчас текст такой:\n\n{current_text["text"]}\n\nВведите новый текст или вернитесь на главную'
        kb = inline_kb.edition_kb()
        await state.update_data(
            branch=branch,
            chapter=chapter,
            subject=subject,
            current_text=current_text,
        )
        await state.set_state(AdminFSM.edit_text)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@admin_router.message(F.text, AdminFSM.edit_text)
async def edition_finish(message: Message, state: FSMContext):
    state_data = await state.get_data()
    branch = state_data["branch"]
    chapter = state_data["chapter"]
    subject = state_data["subject"]
    current_text = state_data["current_text"]
    obj_in_table = f"branch:{branch}|chapter:{chapter}|subject:{subject}"
    text = 'Данные обновлены'
    kb = inline_kb.edition_kb()
    if subject == 'message':
        new_text = message.html_text
    else:
        new_text = message.text
    if current_text is None:
        await TextsDAO.create(subject=obj_in_table, text=new_text)
    else:
        await TextsDAO.update(cond_dict={"object": obj_in_table}, text=new_text)
    await message.answer(text, reply_markup=kb)


@admin_router.callback_query(F.data.split(":")[0] == "mailing")
async def mailing(callback: CallbackQuery):
    mailing_group = callback.data.split(":")[1]
    if mailing_group == "start":
        text = "Выберите адресатов рассылки"


##################################################################################




@moderator_router.callback_query(F.data == "ticket")
async def get_ticket_start(callback: CallbackQuery, state: FSMContext):
    text = 'Введите номер обращения'
    kb = inline_kb.home_kb()
    await state.set_state(AdminFSM.ticket_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@moderator_router.message(F.text, AdminFSM.ticket_id)
async def get_ticket_finish(message: Message):
    if message.text.isdigit():
        ticket_id = int(message.text)
        ticket = await TicketsDAO.get_one_or_none(id=ticket_id)
        if ticket is None:
            kb = inline_kb.home_kb()
            text = 'Ничего не найдено'
        else:
            media_list = ticket["media"]
            ticket_date = (ticket["create_timestamp"] + timedelta(hours=3)).strftime('%d-%m-%Y %H:%M')
            if ticket['phone_method'] == 'auto':
                phone_method = 'Автоматический ввод'
            elif ticket["phone_method"] == "manual":
                phone_method = 'Ручной ввод'
            else:
                phone_method = "---"
            if ticket['username'] is None:
                username = ''
            else:
                username = f"@{ticket['username']}"
            text = [
                f"Обращение <i>{ticket['id']}</i> от <i>{ticket_date}</i>",
                f"<b>Ветка:</b> <i>{ticket['branch']}</i>",
                f"<b>Клиент:</b> <i>{ticket['full_name']}</i> {username}",
                f"<b>Телефон:</b> <i>{ticket['phone_number']}</i> [{phone_method}]",
                f"<b>Вопрос 1:</b> <i>{ticket['level_1']}</i>",
                f"<b>Вопрос 2:</b> <i>{ticket['level_2']}</i>\n",
                f"<b>Обращение:</b> <i>{ticket['petition']}</i>"
            ]
            if len(media_list) == 0:
                text = '\n'.join(text)
            elif len(media_list) == 1:
                file_id = media_list[0]['file_id']
                file_type = media_list[0]['type_obj']
                await file_sender(file_id=file_id, file_type=file_type, chat_id=message.from_user.id)
                text = '\n'.join(text)
            else:
                media_group = []
                for file in media_list:
                    file_id = file['file_id']
                    file_type = file['type_obj']
                    media_group.append({"media": file_id, "type": file_type})
                await message.answer_media_group(media_group)
                text = '\n'.join(text)
            kb = inline_kb.ticket_kb(user_id=ticket['user_id'])
    else:
        text = 'Вы ввели не id обращения.'
        kb = inline_kb.home_kb()
    await message.answer(text, reply_markup=kb)
