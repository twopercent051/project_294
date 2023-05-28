from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    edit_text = State()
    ticket_id = State()
    mailing = State()
    dialog = State()


class UserFSM(StatesGroup):
    home = State()
    full_name = State()
    phone_method = State()
    manual_phone = State()
    petition = State()
    photo = State()
    dialog = State()
