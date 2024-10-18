import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from aiogram import filters

from app.c_pack.c_middlewares import OuterMiddleware, InnerMiddleware
from app.c_pack.c_states import CourierState, CourierRegistration
from app.common.message_handler import MessageHandler
from app.common.titles import get_image_title_courier
from app.common.titles import get_image_title_courier
from app.c_pack.c_kb import get_courier_kb

from app.database.requests import courier_data

from datetime import datetime

couriers_router = Router()

couriers_router.message.outer_middleware(OuterMiddleware())
couriers_router.callback_query.outer_middleware(OuterMiddleware())

couriers_router.message.middleware(InnerMiddleware())
couriers_router.callback_query.middleware(InnerMiddleware())


# ------------------------------------------------------------------------------------------------------------------- #
#                                              ⇣ Registration steps ⇣
# ------------------------------------------------------------------------------------------------------------------- #


# start
@couriers_router.message(CommandStart())
async def cmd_start_courier(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает команду /start для курьеров.

        Эта функция активируется, когда курьер отправляет команду /start.
        - Назначает курьеру начальное состояние регистрации (`CourierState.reg_state`).
        - Отправляет приветственное сообщение, в котором кратко описывается сервис.
        - Предлагает курьеру пройти процесс регистрации.

        Args:
            message (Message): Объект сообщения от пользователя, содержащий команду /start.
            state (FSMContext): Контекст состояния конечного автомата, используемый для управления состояниями пользователя.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и устанавливает состояние.
    """

    text = (
        "Добро пожаловать в Ракету — платформу, которая делает каждого курьера независимым и успешным!\n"
        "Стань частью сообщества, где ты сам управляешь своими доходами и работаешь на своих условиях.\n\n"
        "Почему Ракета?\n\n"
        "◉ **Зарабатывай больше**: \n"
        "Забудь про комиссии и скрытые платежи. Ты оплачиваешь только подписку и получаешь 100% прибыли "
        "с каждого заказа. "
        "Чем больше работаешь, тем больше зарабатываешь. Всё честно и прозрачно.\n\n"
        "◉ **Свобода выбора**: \n"
        "Твоя работа — на твоих условиях. Бери заказы в любое время и работай так, как удобно тебе. "
        "Управляй своим временем и доходами самостоятельно.\n\n"
        "◉ **Прозрачность**: \n"
        "Каждый заработанный рубль — твой. Никаких посредников, штрафов и скрытых условий. "
        "Ты строишь свой бизнес, а мы поддерживаем тебя.\n\n"
        "Присоединяйся к Ракете и начинай зарабатывать больше уже сегодня! Независимость и возможности ждут тебя."
    )


@couriers_router.callback_query(F.data == "reg")
async def data_reg_courier(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
        Обрабатывает нажатие на кнопку регистрации курьера.

        После нажатия на кнопку с идентификатором "reg":
        - Переводит пользователя в состояние регистрации (`CourierRegistration.name`).
        - Отправляет сообщение с просьбой ввести имя курьера.

        Args:
            callback_query (CallbackQuery): Объект, содержащий информацию о нажатии на кнопку.
            state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


@couriers_router.message(filters.StateFilter(CourierRegistration.name))
async def data_name_courier(message: Message, state: FSMContext) -> None:
    """
       Обрабатывает состояние курьера после отправки его имени.

       После отправки курьером своего имени:
       - Переводит пользователя в состояние регистрации (`CourierRegistration.phone_number`).
       - Сохраняет в состояние имя курьера (await state.update_data(name=message.text))
       - Отправляет сообщение с просьбой указать номер телефона с помощью KeyboardButton и никак иначе.

       Args:
           message (Message): Объект сообщения от пользователя, содержащий его имя.
           state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

       Returns:
           None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


@couriers_router.message(filters.StateFilter(CourierRegistration.phone_number))
async def data_phone_courier(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает состояние курьера после отправки его номера.

        После отправки курьером своего номера:
        - Переводит пользователя в состояние регистрации (`CourierRegistration.city`).
        - Сохраняет в состояние номер курьера (await state.update_data(phone_number=message.contact.phone_number))
        - Отправляет сообщение с просьбой указать свой город работы.

        Args:
            message (Message): Объект сообщения от пользователя, содержащий его номер телефона.
            state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


@couriers_router.message(filters.StateFilter(CourierRegistration.city))
async def data_city_courier(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает состояние курьера после отправки его города.

        После отправки курьером своего города:
        - Переводит пользователя в состояние регистрации (`CourierRegistration.accept_tou`).
        - Сохраняет в состояние город курьера (await state.update_data(city=message.text))
        - Отправляет сообщение с предложением ознакомиться и принять пользовательское соглашение.

        Args:
            message (Message): Объект сообщения от пользователя, содержащий его город.
            state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


@couriers_router.callback_query(F.data == "accept_tou")
async def courier_accept_tou(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
        Обрабатывает принятия курьером пользовательского соглашения.

        После принятия курьером пользовательского соглашения:
        - Извлекает из состояния CourierRegistration данные name, phone_number, city, accept_tou.
        - Отправляет запрос в БД для записи.
        - Переводит пользователя в состояние регистрации (`CourierState.default`).
        - Отправляет сообщение с успешной регистрацией и предложением выбрать дальнейшее действие в пункте меню.

        Args:
            callback_query (CallbackQuery): Объект, содержащий информацию о нажатии на кнопку.
            state (FSMContext): Контекст состояния конечного автомата для управления регистрацией.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


# ------------------------------------------------------------------------------------------------------------------- #
#                                                    ⇣ Bot functions ⇣
# ------------------------------------------------------------------------------------------------------------------- #

# run
@couriers_router.message(F.text == "/run")
async def cmd_run(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает команду доставить заказ /run.

        После отправки команды /run:
        - Переводит пользователя в состояние регистрации (`CourierState.location`).
        - Отправляет сообщение c просьбой поделиться локацией и KeyboardButton(send location).

        Args:
            message (Message): Объект, содержащий информацию о нажатии на кнопку.
            state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """


# Location
@couriers_router.message(F.content_type == ContentType.LOCATION)
async def get_location(message: Message, state: FSMContext) -> None:
    """
        Обрабатывает сообщение с отправкой локации курьера.

        После отправки команды локации:
        - Отправляет сообщение с заказами в радиусе 2км от курьера.

        Args:
            message (Message): Объект, содержащий информацию о текущем местомоложении(location=message.location).
            state (FSMContext): Контекст состояния конечного автомата для отслеживания положения в переходах.

        Returns:
            None: Функция не возвращает значение, только отправляет сообщение и изменяет состояние.
    """
