from aiogram.fsm.state import StatesGroup, State


class CourierState(StatesGroup):
    default = State()
    location = State()


class CourierRegistration(StatesGroup):
    name = State()
    phone_number = State()
    city = State()
    accept_tou = State()
