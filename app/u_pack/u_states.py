from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    zero = State()

    reg_state = State()
    reg_Name = State()
    reg_Phone = State()

    waiting_Courier = State()
    ai_voice_order = State()

    change_Name = State()
    change_Phone = State()

    testOrders = State()
    assistant_run = State()
