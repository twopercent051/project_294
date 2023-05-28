import os
from datetime import datetime, timedelta

from aiogram.types import FSInputFile

from create_bot import config, bot, logger, scheduler
from tgbot.keyboards.inline import AdminInlineKeyboard, UserInlineKeyboard
from tgbot.misc.list_create import create_excel
from tgbot.misc.texter import texter
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import TicketsDAO, RemindsDAO, TextsDAO

root_id = config.tg_bot.root_ids


async def daily_db():
    start_period = datetime.utcnow() - timedelta(days=7)
    tickets = await TicketsDAO.get_db(branch="all", period=start_period)
    await create_excel(tickets, 'daily')
    doc_path = f'{os.getcwd()}/daily_tickets.xlsx'
    admin_list = await RedisConnector.get_role_redis("admin")
    print(admin_list)
    moderator_list = await RedisConnector.get_role_redis("moderator")
    print(moderator_list)
    admin_list.extend(moderator_list)
    admin_list.extend(root_id)
    kb = AdminInlineKeyboard.home_kb()
    for admin in admin_list:
        try:
            file = FSInputFile(path=doc_path, filename=f"daily_tickets.xlsx")
            await bot.send_document(chat_id=admin, document=file, reply_markup=kb)
        # except ChatNotFound:
        #     logger.info(f"Bot deleted by admin {admin['username']}")
        # except BotBlocked:
        #     logger.info(f'Bot blocked by admin {admin["username"]}')
        except Exception as ex:
            logger.info(f'Bot blocked by admin {admin}')
    # for root in root_id:
    #     try:
    #         await bot.send_document(chat_id=root, document=open(doc_path, 'rb'), reply_markup=kb)
    #     except ChatNotFound:
    #         logger.info(f"Bot deleted by root {root_id}")
    #     except BotBlocked:
    #         logger.info(f'Bot blocked by root {root_id}')


async def reminder():
    reminds = await RemindsDAO.get_many()
    text_list = await TextsDAO.get_user_texts(branch="X", chapter="remind")
    text = texter(text_list, 'message')
    kb = UserInlineKeyboard.restart_branch_kb(text_list)
    for remind in reminds:
        day = remind['day']
        user_id = remind['user_id']
        if day % 5 == 0:
            try:
                await bot.send_message(user_id, text, reply_markup=kb)
            except Exception as ex:
                logger.info(f'Bot blocked || {ex}')
    await RemindsDAO.update_reminds()


async def scheduler_register():
    await daily_db()
    await reminder()


def scheduler_jobs():
    scheduler.add_job(scheduler_register, "cron", hour=9, minute=0, timezone='Europe/Moscow')
