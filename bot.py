import asyncio
import datetime
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode

logging.basicConfig(filename=f"logs/{datetime.datetime.now()}py_log.log", filemode="w")
import config
import moder_handlers
import mafia_handlers

import sys
python = sys.executable

bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)


async def main():
    dp = Dispatcher()
    dp.include_routers(moder_handlers.router, mafia_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
