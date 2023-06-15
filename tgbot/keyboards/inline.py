from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.misc.texter import texter


class UserInlineKeyboard:
    """Клавиатуры пользователей"""

    @classmethod
    def get_role_kb(cls, role, username, user_id):
        accept_data = f'dec:a|uid:{user_id}|un:{username}|r:{role}'
        refuse_data = f'dec:r|uid:{user_id}|un:{username}|r:{role}'
        keyboard = [
            [InlineKeyboardButton(text="🟢 Принять", callback_data=accept_data)],
            [InlineKeyboardButton(text="🔴 Отклонить", callback_data=refuse_data)],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def first_instr_kb(cls, text_list: list):
        a_text = texter(text_list, 'branch_A')
        b_text = texter(text_list, 'branch_B')
        keyboard = [
            [InlineKeyboardButton(text=a_text, callback_data="branch_A")],
            [InlineKeyboardButton(text=b_text, callback_data="branch_B")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def second_instr_kb(cls, text_list: list):
        yes_text = texter(text_list, 'button_yes')
        no_text = texter(text_list, 'button_no')
        keyboard = [
            [InlineKeyboardButton(text=yes_text, callback_data="personal:yes")],
            [InlineKeyboardButton(text=no_text, callback_data="personal:no")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def level_1_kb(cls, text_list: list):
        button_1_text = texter(text_list, 'button_1')
        button_2_text = texter(text_list, 'button_2')
        button_3_text = texter(text_list, 'button_3')
        button_return_text = texter(text_list, 'return')
        keyboard = [
            [InlineKeyboardButton(text=button_1_text, callback_data=f'level_1:{button_1_text}')],
            [InlineKeyboardButton(text=button_2_text, callback_data=f'level_1:{button_2_text}')],
            [InlineKeyboardButton(text=button_3_text, callback_data=f'level_1:{button_3_text}')],
            [InlineKeyboardButton(text=button_return_text, callback_data="branch_A")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def level_2_kb(cls, text_list: list, branch: str):
        button_1_text = texter(text_list, 'button_1')
        button_2_text = texter(text_list, 'button_2')
        button_3_text = texter(text_list, 'button_3')
        button_4_text = texter(text_list, 'button_4')
        button_5_text = texter(text_list, 'button_5')
        button_return_text = texter(text_list, 'return')
        keyboard = [
            [InlineKeyboardButton(text=button_1_text, callback_data=f'level_2:{button_1_text}')],
            [InlineKeyboardButton(text=button_2_text, callback_data=f'level_2:{button_2_text}')],
            [InlineKeyboardButton(text=button_3_text, callback_data=f'level_2:{button_3_text}')],
            [InlineKeyboardButton(text=button_4_text, callback_data=f'level_2:{button_4_text}')],
            [InlineKeyboardButton(text=button_5_text, callback_data=f'level_2:{button_5_text}')],
        ]
        if branch == "A":
            keyboard.append([InlineKeyboardButton(text=button_return_text, callback_data="branch_A")])
        else:
            keyboard.append([InlineKeyboardButton(text=button_return_text, callback_data="start")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def request_photo_kb(cls, text_list: list, branch: str):
        yes_text = texter(text_list, 'button_yes')
        no_text = texter(text_list, 'button_no')
        button_return_text = texter(text_list, 'return')
        keyboard = [
            [InlineKeyboardButton(text=yes_text, callback_data="photo:yes")],
            [InlineKeyboardButton(text=no_text, callback_data="photo:no")],
        ]
        if branch == "A":
            keyboard.append([InlineKeyboardButton(text=button_return_text, callback_data="branch_A")])
        else:
            keyboard.append([InlineKeyboardButton(text=button_return_text, callback_data="start")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def restart_a_kb(cls, text_list: list):
        button_return_text = texter(text_list, 'return')
        keyboard = [
            [InlineKeyboardButton(text=button_return_text, callback_data="branch_A")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def restart_b_kb(cls, text_list: list):
        button_return_text = texter(text_list, 'return')
        keyboard = [
            [InlineKeyboardButton(text=button_return_text, callback_data="start")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def admin_answer_kb(cls, user_id: int):
        keyboard = [
            [InlineKeyboardButton(text='📞 Ответить клиенту', callback_data=f'dialog:{user_id}')],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class AdminInlineKeyboard(InlineKeyboardMarkup):
    """Клавиатуры админа"""

    @classmethod
    def home_kb(cls) -> InlineKeyboardMarkup:
        keyboard = [[InlineKeyboardButton(text='🏠 На главный экран', callback_data='home')]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def main_menu_kb(cls, role: str):
        keyboard = [
            [InlineKeyboardButton(text="📋 Список админов", callback_data="list:admin")],
            [InlineKeyboardButton(text="📋 Список модераторов", callback_data="list:moderator")],
            [InlineKeyboardButton(text="🖊 Редактура текстов", callback_data="edition")],
            [InlineKeyboardButton(text="📨 Рассылка", callback_data="mailing:start")],
            [InlineKeyboardButton(text="🗄 Запросить БД", callback_data="db:start")],
            [InlineKeyboardButton(text="🔎 Найти обращение", callback_data="ticket")],
        ]
        if role == "root":
            return InlineKeyboardMarkup(inline_keyboard=keyboard)
        elif role == "admin":
            return InlineKeyboardMarkup(inline_keyboard=keyboard[2:])
        else:
            return InlineKeyboardMarkup(inline_keyboard=keyboard[4:])

    @classmethod
    def roles_list_kb(cls, role: str, users: list):
        keyboard = []
        for username in users:
            button = [InlineKeyboardButton(text=f"@{username}", callback_data=f"{role}:{username}")]
            keyboard.append(button)
        keyboard.append([InlineKeyboardButton(text="🏠 На главный экран", callback_data="home")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def profile_kb(cls, user_id: str, role: str):
        keyboard = [
            [InlineKeyboardButton(text='❌ Удалить сотрудника', callback_data=f'delete:{role}|user_id:{user_id}')],
            [InlineKeyboardButton(text="🏠 На главный экран", callback_data="home")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def accept_deleting_kb(cls, username: str, role: str):
        keyboard = [
            [InlineKeyboardButton(text='👍 Подтверждаю', callback_data=f'accept_deleting:{role}|user_id:{username}')],
            [InlineKeyboardButton(text="🏠 На главный экран", callback_data="home")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def edition_lvl_1(cls):
        keyboard = [
            [InlineKeyboardButton(text='Первая инструкция', callback_data='edit:lvl_2|br:X|ch:1_instr')],
            [InlineKeyboardButton(text='Ветка А', callback_data='edit:lvl_1|br:A')],
            [InlineKeyboardButton(text='Ветка B', callback_data='edit:lvl_1|br:B')],
            [InlineKeyboardButton(text='Напоминание', callback_data='edit:lvl_2|br:X|chapter:remind')],
            [InlineKeyboardButton(text='Переписка с пользователем', callback_data='edit:lvl_2|br:X|chapter:dialog')],
            [InlineKeyboardButton(text="🏠 На главный экран", callback_data="home")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def edition_lvl_2(cls, branch: str):
        keyboard = []
        keys = {
            "A": {
                'Вторая инструкция': '2_instr',
                'Отказ от ОПД': 'ref_pers',
                'Запрос ФИО': 'req_name',
                'Метод ввода телефона': 'req_phone',
                'Ручной ввод телефона': 'manual_phone',
                'Уровень 1': 'level_1',
                'Уровень 2': 'level_2',
                'Просьба обращения': 'petition',
                'Запрос фото': 'req_photo',
                'Принятие фото': 'accept_photo',
                'Благодарность': 'gratitude',
            },
            "B": {
                'Уровень 2': 'level_2',
                'Просьба обращения': 'petition',
                'Запрос фото': 'req_photo',
                'Принятие фото': 'accept_photo',
                'Благодарность': 'gratitude',
            }
        }
        chapter_dict = keys[branch]
        for c in chapter_dict.keys():
            kb_button = [InlineKeyboardButton(
                text=c,
                callback_data=f'edit:lvl_2|br:{branch}|ch:{chapter_dict[c]}'
            )]
            keyboard.append(kb_button)
        keyboard.append([InlineKeyboardButton(text='📃 Меню редактуры', callback_data='edition')])
        keyboard.append([InlineKeyboardButton(text='🏠 На главный экран', callback_data='home')])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def edition_lvl_3(cls, branch: str, chapter: str):
        keyboard = []
        subjects = {
            '1_instr': {
                'Сообщение': 'message',
                'Кн. Ветка А': 'branch_A',
                'Кн. Ветка В': 'branch_B',
            },
            '2_instr': {
                'Сообщение': 'message',
                'Кнопка ДА': 'button_yes',
                'Кнопка НЕТ': 'button_no'
            },
            'ref_pers': {
                'Сообщение': 'message',
                'Кнопка ВОЗВРАТ': 'return'
            },
            'req_name': {
                'Сообщение': 'message'
            },
            'req_phone': {
                'Сообщение': 'message'
            },
            'manual_phone': {
                'Сообщение': 'message'
            },
            'level_1': {
                'Сообщение': 'message',
                'Кнопка 1': 'button_1',
                'Кнопка 2': 'button_2',
                'Кнопка 3': 'button_3',
                'Кн. ВОЗВРАТ': 'return'
            },
            'level_2': {
                'Сообщение': 'message',
                'Кнопка 1': 'button_1',
                'Кнопка 2': 'button_2',
                'Кнопка 3': 'button_3',
                'Кнопка 4': 'button_4',
                'Кнопка 5': 'button_5',
                'Кн. ВОЗВРАТ': 'return'
            },
            'petition': {
                'Сообщение': 'message'
            },
            'req_photo': {
                'Сообщение': 'message',
                'Кнопка ДА': 'button_yes',
                'Кнопка НЕТ': 'button_no',
                'Кн. ВОЗВРАТ': 'return'
            },
            'accept_photo': {
                'Сообщение': 'message',
                'Кн. ВОЗВРАТ': 'return'
            },
            'gratitude': {
                'Сообщение': 'message',
                'Кн. ВОЗВРАТ': 'return'
            },
            'remind': {
                'Сообщение': 'message',
                'Кн. ВОЗВРАТ': 'return'
            },
            'dialog': {
                'Сообщение': 'message',
                'Кн. ОТВЕТИТЬ': 'button_answer'
            }
        }
        chapter_dict = subjects[chapter]
        for c in chapter_dict.keys():
            kb_button = [InlineKeyboardButton(
                text=c,
                callback_data=f'edit:lvl_3|branch:{branch}|chapter:{chapter}|subject:{chapter_dict[c]}'
            )]
            keyboard.append(kb_button)
        keyboard.append([InlineKeyboardButton(text='📃 Меню редактуры', callback_data='edition')])
        keyboard.append([InlineKeyboardButton(text='🏠 На главный экран', callback_data='home')])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def edition_kb(cls):
        keyboard = [
            [InlineKeyboardButton(text='📃 Меню редактуры', callback_data='edition')],
            [InlineKeyboardButton(text='🏠 На главный экран', callback_data='home')],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def ticket_kb(cls, user_id: str):
        keyboard = [
            [
                InlineKeyboardButton(text='📞 Написать клиенту', callback_data=f'dialog:{user_id}'),
                InlineKeyboardButton(text='🏠 На главный экран', callback_data='home'),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def mailing_group_kb(cls):
        keyboard = [
            [InlineKeyboardButton(text='Ветка А', callback_data='mailing:A')],
            [InlineKeyboardButton(text='Ветка B', callback_data='mailing:B')],
            [InlineKeyboardButton(text='Все пользователи', callback_data='mailing:all')],
            [InlineKeyboardButton(text='🏠 На главный экран', callback_data='home')],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def db_branch_kb(cls):
        keyboard = [
            [InlineKeyboardButton(text='Ветка А', callback_data='db:branch|branch:A')],
            [InlineKeyboardButton(text='Ветка B', callback_data='db:branch|branch:B')],
            [InlineKeyboardButton(text='Все обращения', callback_data='db:branch|branch:all')],
            [InlineKeyboardButton(text='🏠 На главный экран', callback_data='home')],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def db_period_kb(cls, branch: str):
        keyboard = [
            [InlineKeyboardButton(text='1 Неделя', callback_data=f'db:period|branch:{branch}|period:week')],
            [InlineKeyboardButton(text='1 Месяц', callback_data=f'db:period|branch:{branch}|period:month')],
            [InlineKeyboardButton(text='За всё время', callback_data=f'db:period|branch:{branch}|period:infinity')],
            [InlineKeyboardButton(text='🏠 На главный экран', callback_data='home')],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def user_answer_kb(cls, text_list: list, admin_id: int):
        answer_text = texter(text_list, 'button_answer')
        keyboard = [
            [InlineKeyboardButton(text=answer_text, callback_data=f'answer_admin:{admin_id}')],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


