from aiogram.fsm.state import StatesGroup, State


class CustomerState(StatesGroup):

    default = State()

    set_seed_key = State()

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

    set_seed_key = State()

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

    change_subscription_price = State()
    change_standard_order_price = State()
    change_max_order_price = State()
    change_distance_coefficient_less_5 = State()
    change_distance_coefficient_5_10 = State()
    change_distance_coefficient_10_20 = State()
    change_distance_coefficient_more_20 = State()
    change_time_coefficient_00_06 = State()
    change_time_coefficient_06_12 = State()
    change_time_coefficient_12_18 = State()
    change_time_coefficient_18_21 = State()
    change_time_coefficient_21_00 = State()
    change_big_cities_coefficient = State()
    change_small_cities_coefficient = State()
    change_subscription_discount = State()
    change_first_order_discount = State()
    change_free_period = State()
    change_refund_percent = State()

    change_base_order_XP = State()
    change_distance_XP = State()
    change_speed_XP = State()

    choose_order = State()

    full_speed_report_by_date = State()
    full_speed_report_by_period = State()
    full_financial_report_by_date = State()
    full_financial_report_by_period = State()

    full_distance_report_by_date = State()
    full_distance_report_by_period = State()

    full_orders_report_by_date = State()
    full_orders_report_by_period = State()

    full_earned_report_by_date = State()
    full_earned_report_by_period = State()

    change_min_refund_amount = State()
    change_max_refund_amount = State()

    process_request = State()

    set_new_admin = State()
    del_admin = State()

    change_interval = State()
    change_support_link = State()
    change_radius_km = State()

    reg_adminPhone = State()


class PartnerState(StatesGroup):

    default = State()

    reg_state = State()
    reg_Name = State()
    reg_Phone = State()
    reg_City = State()
    generate_seed_key = State()


class OrdersState(StatesGroup):

    default = State()


__all__ = [
    "CustomerState",
    "CourierState",
    "AdminState",
    "PartnerState",
    "OrdersState",
]
