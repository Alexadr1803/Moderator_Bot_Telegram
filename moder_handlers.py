from aiogram import types, Router
import random
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
import re
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
import states_file

user_active_repeat = False
router = Router()


# Самописный фильтр, он так заебывает
class ChatCensureFilter(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        if msg.text is None:
            return False
        if msg.message_thread_id is None:
            text = re.sub(r'[^\w\s]', ' ', msg.text.lower())
            with open("mats.txt", 'r') as file:
                if set([''.join(i.split('\n')) for i in file.readlines()]) & set(text.split()):
                    return True
                else:
                    return False
        else:
            return False


# Обработчик сообщений
@router.message(ChatCensureFilter())
async def start(msg: Message):
    await msg.answer(text=f"Не матерись <b>{msg.from_user.full_name}</b>!\nЯ все вижу!", parse_mode=ParseMode.HTML)
    await msg.delete()


# Отключает добавление матов
@router.message(Command("cancel_add"))
async def cancel_add_mat(msg: Message, state: FSMContext):
    await state.clear()
    await msg.reply("Добавление матов выключено!")


# Добавление мата в список
@router.message(StateFilter(states_file.Mats.add_matuk))
async def food_chosen_incorrectly(msg: Message):
    with open("bot_test/mats.txt", "a") as file:
        file.write(msg.text + '\n')
        await msg.reply("Добавлено!")


# Активирует добавление матов только у меня в личке
@router.message(Command('add_mat'))
async def set_state_mats(msg: Message, state=FSMContext):
    if msg.chat.id in [1701296589]:
        await msg.answer("Каждое написанное слово будет добавлено в банлист!")
        await state.set_state(states_file.Mats.add_matuk)

