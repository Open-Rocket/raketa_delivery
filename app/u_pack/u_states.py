from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    default = State()

    reg_state = State()
    reg_Name = State()
    reg_Phone = State()
    reg_City = State()

    waiting_Courier = State()
    ai_voice_order = State()

    change_Name = State()
    change_Phone = State()
    change_City = State()

    testOrders = State()
    myOrders = State()
    assistant_run = State()
