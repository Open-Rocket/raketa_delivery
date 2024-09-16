from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    testOrders = State()

    regstate = State()
    set_Name = State()
    set_Phone = State()
    zero = State()

    waiting_Courier = ()

    ai_voice_order = State()
