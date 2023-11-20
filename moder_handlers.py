from aiogram import types, Router
import random
user_active_repeat = False
router = Router()
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
import re
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import ParseMode
import states_file
exception_words = ['оскарблять']


class ChatCensureFilter(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        if msg.text is None:
            return False
        if msg.message_thread_id is None:
            txte = re.sub(r'[^\w\s]', ' ', msg.text.lower())
            with open("mats.txt", 'r') as file:
                if set([''.join(i.split('\n')) for i in file.readlines()]) & set(txte.split()):
                    return True
                else:
                    return False
        else:
            return False


@router.message(ChatCensureFilter())
async def start(msg: Message):
    await msg.answer(text=f"Не матерись <b>{msg.from_user.full_name}</b>!\nЯ все вижу!", parse_mode=ParseMode.HTML)
    await msg.delete()


@router.message(Command("cancel_add"))
async def cancell_add_mat(msg: Message, state: FSMContext):
    await state.clear()
    await msg.reply("Добавление матов выключено!")


@router.message(StateFilter(states_file.Mats.add_matuk))
async def food_chosen_incorrectly(msg: Message):
    with open("bot_test/mats.txt", "a") as file:
        file.write(msg.text + '\n')
        await msg.reply("Добавлено!")


@router.message(Command('kto_segodnia'))
async def cmd_all_members(msg: types.Message):
    args = " ".join(msg.text.split()[1:])
    if len(args) != 0:
        members = ["Саша", "Катя", "Ростик", "Миша", "Ярик Морозов", "Ярик Аношков", "Ярик Тарасов",
                   "Егор Сапронов", "Егор Чвыков", "Андрей Бышов", "Андрей Спичак", "Ксюша Власенко",
                   "Ксюша Клыкова", "Настя Масалова", "Настя Клевцова", "Маша Сидорова",
                   "Машка Волкова", "Вова", "Кирилл", "Глеб", "Авдей", "Витя", "Никита Черкасов",
                   "Никита Онуфриенко", "Даня Хорхордин", "Даня Мищенко", "Лера", "Федя", "Максим", "Богдан"]
        await msg.reply(text=f"<b>{random.choice(members)}</b> {''.join(args.split('?'))} сегодня!", parse_mode=ParseMode.HTML)
    else:
        await msg.reply(text="Формат ввода: /kto_segodnia <описание>", parse_mode=None)


@router.message(Command('skazi_pravdu'))
async def Return(m: types.Message):
    args = " ".join(m.text.split()[1:])
    if len(args) == 0:
        await m.reply(text="Напишите: /skazi_pravdu <вопрос>", parse_mode=None)
    else:
        await m.reply(text=random.choice(["Да ;)", "Нет :(", "Наверное :/", "Cкорее да, чем нет! :|", "Скорее нет, чем да! :0"]))

@router.message(Command('skazi_pravdu'))
async def Return(m: types.Message):
    args = " ".join(m.text.split()[1:])
    if len(args) == 0:
        await m.reply(text="Напишите: /skazi_pravdu <вопрос>", parse_mode=None)
    else:
        await m.reply(text=random.choice(["Да ;)", "Нет :(", "Наверное :/", "Cкорее да, чем нет! :|", "Скорее нет, чем да! :0"]))


@router.message(Command('add_mat'))
async def set_state_mats(msg: Message, state=FSMContext):
    if msg.chat.id in [1701296589]:
        await msg.answer("Каждое написанное слово будет добавлено в банлист!")
        await state.set_state(states_file.Mats.add_matuk)

