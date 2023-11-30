from aiogram import Router
import re
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
user_active_repeat = False
router = Router()


# Самописный фильтр, он так заебывает
class ChatCensureFilter(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        if msg.text is None:
            return False
        text = re.sub(r'[^\w\s]', ' ', msg.text.lower())
        with open("moderator/mats.txt", 'r', encoding='utf-8') as file:
            if set([''.join(i.split('\n')) for i in file.readlines()]) & set(text.split()):
                return True
            else:
                return False


# Обработчик сообщений
@router.message(ChatCensureFilter())
async def start(msg: Message):
    await msg.answer(text=f"Не матерись <b>{msg.from_user.full_name}</b>!\nЯ все вижу!", parse_mode=ParseMode.HTML)
    await msg.delete()
