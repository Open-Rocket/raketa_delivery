import asyncio
from app.u_pack.u_ai_assistant import assistant_censure

message = ("Здравствуйте! Забрать заказ нужно в Москве, на проспекте Вернадского, дом 106. "
           "Отправить на улицу Крымский Вал, дом 30. В сумке находятся лекарства. Получатель — Наталья, "
           "её номер 89997766554. Важно доставить до 18:00. Если что, звоните.")

async def print_answer(msg):
    answer = await assistant_censure(msg)
    print(answer)

# Запуск асинхронной функции через asyncio.run()
asyncio.run(print_answer(message))