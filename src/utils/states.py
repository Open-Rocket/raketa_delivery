from aiogram.fsm.state import StatesGroup, State


class CustomerState(StatesGroup):
    default = State()

    reg_state = State()
    reg_Name = State()
    reg_Phone = State()
    reg_City = State()
    reg_tou = State()

    ai_voice_order = State()
    assistant_run = State()

    change_Name = State()
    change_Phone = State()
    change_City = State()

    myOrders = State()


class CourierState(StatesGroup):
    default = State()
    location = State()
    myOrders = State()
    myOrders_active = State()
    myOrders_completed = State()
    start_reg = State()
    pay = State()
    change_Name = State()
    change_Phone = State()
    change_City = State()

    name = State()
    phone_number = State()
    city = State()
    accept_tou = State()


__all__ = ["CustomerState", "CourierState"]
