import aiogram
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class Mats(StatesGroup):
    add_matuk = State()

