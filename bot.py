import asyncio
import datetime
import logging
from configs import config
from moderator import moder_handlers
from mafia import mafia_handlers
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
# Включение логирования
logging.basicConfig(filename=f"logs/{datetime.datetime.now()}py_log.log", filemode="w")
# Переменная для перезапуска скрипта
python = sys.executable

bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)


# Главная функция активации бота
async def main():
    dp = Dispatcher()
    dp.include_routers(moder_handlers.router, mafia_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запуск проекта
if __name__ == "__main__":
    asyncio.run(main())
