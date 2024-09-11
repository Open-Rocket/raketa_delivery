from aiogram.fsm.state import StatesGroup, State


class CourierState(StatesGroup):

    order_state = State()
    run_state = State()

    state_Name = State()
    state_email = State()
    state_Phone = State()

    state_Profile = State()

    zero = State()

    start_position = State()
    admins_password = State()
    driver_mode = State()
    passenger_mode = State()
    choose_lang = State()
    ai_voice_order = State()