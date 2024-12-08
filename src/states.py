from aiogram.fsm.state import State, StatesGroup


class RegisterAuto(StatesGroup):
    BRAND = State()
    MODEL = State()
    YEAR = State()
    COLOR = State()
    LICENSE_PLATE = State()


class SendMessageAdmin(StatesGroup):
    admin_message = State()
