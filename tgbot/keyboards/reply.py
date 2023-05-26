from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class UserReplyKeyboard:
    """Клавиатура юзера для передачи телефона"""

    @classmethod
    def phone_keyboard(cls):
        kb = [
            [
                KeyboardButton(text='Поделиться телефоном автоматически', request_contact=True),
                KeyboardButton(text='Ввести телефон вручную')
            ],
            [KeyboardButton(text='В начало')],
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        return keyboard
