import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from handlers import router

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession


async def main():
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))#
    dp = Dispatcher(storage=MemoryStorage())#Сохраняем только то, что укажем сохранять
    dp.include_router(router) #подключаем роутер
    await bot.delete_webhook(drop_pending_updates=True) #не воспринимает старые сообщения, только новые
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())