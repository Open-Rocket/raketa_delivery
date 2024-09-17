import asyncio
from app.u_pack.u_ai_assistant import assistant_run

message = "Что ты умеешь"

async def print_answer(msg):
    answer = await assistant_run(msg)
    print(answer)

# Запуск асинхронной функции через asyncio.run()
asyncio.run(print_answer(message))