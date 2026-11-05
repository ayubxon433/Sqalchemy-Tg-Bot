import asyncio
import logging

from aiogram import Dispatcher
from handlers import router
from baza_qilish import Base, engine
from admin import admin_router
from config import bot


dp = Dispatcher()

async def main():
    dp.include_router(router)
    dp.include_router(admin_router)

    Base.metadata.create_all(bind=engine)
    print('u aaaa ua aua a8a auanaua')
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())