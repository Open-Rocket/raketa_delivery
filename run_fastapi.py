# import asyncio
# from fastapi import FastAPI, Request, Response
# from aiogram.types import Update
# from aiogram import Dispatcher


# from aiogram.fsm.storage.redis import RedisStorage
# from src.confredis import rediska, redis_main, RedisService
# from src.app.customer import customer_r, customer_fallback
# from src.app.courier import courier_r, courier_fallback, payment_r
# from src.app.admin import admin_r, admin_fallback
# from src.app.partner import partner_r, partner_fallback
# from src.tasks.worker import main_worker
# from src.middlewares import (
#     CustomerOuterMiddleware,
#     CourierOuterMiddleware,
#     AdminOuterMiddleware,
#     AgentOuterMiddleware,
# )
# from src.config import (
#     customer_bot,
#     courier_bot,
#     admin_bot,
#     partner_bot,
#     customer_dp,
#     courier_dp,
#     admin_dp,
#     partner_dp,
#     log,
#     customer_bot_secret,
#     courier_bot_secret,
#     admin_bot_secret,
#     partner_bot_secret,
# )

# # === Lifespan FastAPI App ===


# async def lifespan(app: FastAPI):

#     log.debug("Инициализация Redis")
#     try:
#         rediska = await redis_main()
#         log.info("✅ Redis инициализирован")
#     except Exception as e:
#         log.error(f"Ошибка инициализации Redis: {e}")
#         raise

#     setup_dispatchers(rediska)
#     await set_webhooks()
#     app.state.worker_task = asyncio.create_task(main_worker())
#     yield
#     log.info("Shutting down...")
#     app.state.worker_task.cancel()
#     try:
#         await app.state.worker_task
#     except asyncio.CancelledError:
#         pass
#     await rediska.redis.aclose()
#     log.info("Resources cleaned up.")


# app = FastAPI(lifespan=lifespan)


# # === Setup ===


# def setup_dispatchers(rediska_arg: RedisService):
#     # Создаём хранилища с Redis
#     redis_storage_customer = RedisStorage(rediska_arg)
#     redis_storage_courier = RedisStorage(rediska_arg)
#     redis_storage_admin = RedisStorage(rediska_arg)
#     redis_storage_partner = RedisStorage(rediska_arg)

#     global customer_dp, courier_dp, admin_dp, partner_dp

#     customer_dp = Dispatcher(storage=redis_storage_customer)
#     courier_dp = Dispatcher(storage=redis_storage_courier)
#     admin_dp = Dispatcher(storage=redis_storage_admin)
#     partner_dp = Dispatcher(storage=redis_storage_partner)

#     customer_dp["bot"] = customer_bot
#     customer_dp["redis"] = redis_storage_customer
#     customer_dp.message.middleware(CustomerOuterMiddleware(rediska_arg))
#     customer_dp.callback_query.middleware(CustomerOuterMiddleware(rediska_arg))
#     customer_dp.include_routers(customer_r, customer_fallback)

#     courier_dp["bot"] = courier_bot
#     courier_dp["redis"] = redis_storage_courier
#     courier_dp.message.middleware(CourierOuterMiddleware(rediska_arg))
#     courier_dp.callback_query.middleware(CourierOuterMiddleware(rediska_arg))
#     courier_dp.include_routers(courier_r, payment_r, courier_fallback)

#     admin_dp["bot"] = admin_bot
#     admin_dp["redis"] = redis_storage_admin
#     admin_dp.message.middleware(AdminOuterMiddleware(rediska_arg))
#     admin_dp.callback_query.middleware(AdminOuterMiddleware(rediska_arg))
#     admin_dp.include_routers(admin_r, admin_fallback)

#     partner_dp["bot"] = partner_bot
#     partner_dp["redis"] = redis_storage_partner
#     partner_dp.message.middleware(AgentOuterMiddleware(rediska_arg))
#     partner_dp.callback_query.middleware(AgentOuterMiddleware(rediska_arg))
#     partner_dp.include_routers(partner_r, partner_fallback)


# async def set_webhooks():
#     webhooks = [
#         (customer_bot, "customer", customer_bot_secret),
#         (courier_bot, "courier", courier_bot_secret),
#         (admin_bot, "admin", admin_bot_secret),
#         (partner_bot, "partner", partner_bot_secret),
#     ]
#     for bot, name, secret in webhooks:
#         await bot.set_webhook(
#             f"https://{name}.raketago.ru/{name}",
#             secret_token=secret,
#             drop_pending_updates=True,
#         )
#         log.info(f"Webhook set for {name}")


# @app.post("/{bot_name}")
# async def handle_webhook(request: Request, bot_name: str):
#     try:
#         update = Update.model_validate(await request.json())
#         log.debug(f"Update for {bot_name}: {update}")

#         if bot_name == "customer":
#             await customer_dp.feed_update(
#                 customer_bot,
#                 update,
#             )
#         elif bot_name == "courier":
#             await courier_dp.feed_update(
#                 courier_bot,
#                 update,
#             )
#         elif bot_name == "admin":
#             await admin_dp.feed_update(
#                 admin_bot,
#                 update,
#             )
#         elif bot_name == "partner":
#             await partner_dp.feed_update(
#                 partner_bot,
#                 update,
#             )
#         else:
#             return Response(status_code=404)

#         return Response(status_code=200)
#     except Exception as e:
#         log.error(f"Error handling update for {bot_name}: {e}")
#         return Response(status_code=500)
