from aiogram import Router
import re
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
from nltk.stem.snowball import SnowballStemmer
import sqlite3
from aiogram.filters import Command
user_active_repeat = False
router = Router()
stemmer = SnowballStemmer("russian")


def update_stats(userId, chatId, badWord=0, messag=1, userName='Bacon'):
    connection = sqlite3.connect('moderator/statistics')
    cursor = connection.cursor()
    if cursor.execute("SELECT message_count FROM messages_stats WHERE id = ? AND group_id = ?", (userId, chatId)).fetchall():
        bad_words = cursor.execute("SELECT bad_messages_count FROM messages_stats WHERE id = ? AND group_id = ?", (userId, chatId)).fetchall()[0][0]
        messages_count = cursor.execute("SELECT message_count FROM messages_stats WHERE id = ? AND group_id = ?", (userId, chatId)).fetchall()[0][0]
        cursor.execute('UPDATE messages_stats SET (bad_messages_count, message_count, user_name) = (?, ?, ?) WHERE id = ? AND group_id = ?', (bad_words + badWord, messages_count + messag, userName, userId, chatId))
        connection.commit()
    else:
        cursor.execute("INSERT INTO messages_stats (id, group_id, message_count, bad_messages_count, user_name) VALUES (?, ?, "
                       "?, ?, ?)", (userId, chatId, messag, badWord, userName))
        connection.commit()
    connection.close()

# Фильтр матов
class ChatCensureFilter(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        if msg.text is None:
            return False
        text = re.sub(r'[^\w\s]', ' ', msg.text.lower())
        with open("moderator/mats.txt", 'r', encoding='utf-8') as file:
            if set([stemmer.stem(word) for word in [''.join(i.split('\n')).lower() for i in file.readlines()]]) & set([stemmer.stem(word) for word in text.split()]):
                return True
            else:
                return False


# Обработчик сообщений
@router.message(ChatCensureFilter())
async def start(msg: Message):
    await msg.answer(text=f"Не матерись <b>{msg.from_user.full_name}</b>!\nЯ все вижу!", parse_mode=ParseMode.HTML)
    await msg.delete()
    update_stats(userId=msg.from_user.id, chatId=msg.chat.id, badWord=1, messag=1, userName=msg.from_user.full_name)


@router.message(Command('mes_stats'))
async def mes_stats(msg: Message):
    connection = sqlite3.connect('moderator/statistics')
    cursor = connection.cursor()
    users = cursor.execute("SELECT user_name, message_count FROM messages_stats WHERE group_id = ?", (str(msg.chat.id), )).fetchall()
    if users:
        users.sort(key=lambda x: x[1], reverse=True)
        text = f"Топ по сообщениям:\n 🏆 1. <b>{users[0][0]}</b> - {users[0][1]}\n"
        for i in range(1, len(users)):
            text += f" 👤 {i+1}. <b>{users[i][0]}</b> - {users[i][1]}\n"
        await msg.answer(text=text, parse_mode=ParseMode.HTML)
    else:
        await msg.answer(text="Никто еще не писал в этот чат(", parse_mode=ParseMode.HTML)
    connection.close()


@router.message(Command('bad_stats'))
async def mes_stats(msg: Message):
    connection = sqlite3.connect('moderator/statistics')
    cursor = connection.cursor()
    users = cursor.execute("SELECT user_name, bad_messages_count FROM messages_stats WHERE group_id = ?", (str(msg.chat.id), )).fetchall()
    if users:
        users.sort(key=lambda x: x[1], reverse=True)
        text = f"Топ по матам:\n 🥀 1. <b>{users[0][0]}</b> - {users[0][1]}\n"
        for i in range(1, len(users)):
            text += f" 👤 {i+1}. <b>{users[i][0]}</b> - {users[i][1]}\n"
        await msg.answer(text=text, parse_mode=ParseMode.HTML)
    else:
        await msg.answer(text="Никто еще не писал в этот чат(", parse_mode=ParseMode.HTML)
    connection.close()
