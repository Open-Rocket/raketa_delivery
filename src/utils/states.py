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
    myOrders_pending = State()
    myOrders_completed = State()
    myOrders_active = State()
    myOrders_canceled = State()


class CourierState(StatesGroup):

    default = State()

    reg_state = State()
    reg_Name = State()
    reg_Phone = State()
    reg_City = State()
    reg_tou = State()

    change_Name = State()
    change_Phone = State()
    change_City = State()

    location = State()
    nearby_Orders = State()
    city_Orders = State()
    myOrders = State()
    myOrders_active = State()
    myOrders_completed = State()
    pay = State()


class AdminState(StatesGroup):

    default = State()

    password = State()


__all__ = ["CustomerState", "CourierState", "AdminState"]
