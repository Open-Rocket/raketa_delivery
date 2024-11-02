from aiogram.fsm.state import StatesGroup, State


class CourierState(StatesGroup):
    default = State()
    location = State()
    myOrders = State()
    start_reg = State()
    pay = State()
    change_Name = State()
    change_Phone = State()
    change_City = State()



class CourierRegistration(StatesGroup):
    name = State()
    phone_number = State()
    city = State()
    accept_tou = State()
