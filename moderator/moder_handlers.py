from aiogram import Router
import re
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
user_active_repeat = False
router = Router()
stemmer = SnowballStemmer("russian")
# Фильтр матов
class ChatCensureFilter(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        if msg.text is None:
            return False
        text = re.sub(r'[^\w\s]', ' ', msg.text.lower())
        with open("moderator/mats.txt", 'r', encoding='utf-8') as file:
            if set([stemmer.stem(word) for word in [''.join(i.split('\n')).lower() for i in file.readlines()]]) & set([stemmer.stem(word) for word in text.split()]):
                print([stemmer.stem(word) for word in text.split()])
                return True
            else:
                print([stemmer.stem(word) for word in text.split()])
                return False


# Обработчик сообщений
@router.message(ChatCensureFilter())
async def start(msg: Message):
    await msg.answer(text=f"Не матерись <b>{msg.from_user.full_name}</b>!\nЯ все вижу!", parse_mode=ParseMode.HTML)
    await msg.delete()
