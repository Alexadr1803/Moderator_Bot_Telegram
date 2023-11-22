"""
    Технические функции для игры в мафию
    Тут бы все оптимизировать, если кто шарит можете помочь?
"""
import random
from aiogram import types

# Счетчики персонажей в игре
from operator import attrgetter
from collections import Counter


def count_mafia(mafia_members):
    return list(map(attrgetter('role'), mafia_members.values())).count('Мафия')


def count_peace(mafia_members):
    return len(list(map(attrgetter('role'), mafia_members.values()))) - count_mafia(mafia_members)


def count_lover(mafia_members):
    return list(map(attrgetter('role'), mafia_members.values())).count('Любовница')


def count_doctor(mafia_members):
    return list(map(attrgetter('role'), mafia_members.values())).count('Доктор')


def count_sheriff(mafia_members):
    return list(map(attrgetter('role'), mafia_members.values())).count('Шериф')


# Создает специальную клавиатуру для голосований с префиксом, чтобы отличать разные колбэки друг от друга
def create_prefix_keyboard(mafia_members: dict, prefix: str):
    buttons = [
        [types.InlineKeyboardButton(text=f"{mafia_members[i].full_name}", callback_data=f"{prefix}|{i}")] for i in
        list(mafia_members.keys())
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


"""Тут точно можно все оптимизировать! Сократите код """


# Возращает список с двумя значениями [Есть вердикт? : bool, Кто будет исключен? : int or None]
def get_verdict(mafia_members: dict):
    c = Counter(list(map(attrgetter('vote_on_voting'), mafia_members.values()))).most_common(2)
    if len(c) > 1:
        if c[0][1] == c[1][1]:
            return [False, None]
        else:
            return [True, c[0][0]]
    else:
        return [True, c[0][0]]


# Возращает список умерших игроков, соблюдая все условия (Доктор, Любовница, Житель не голосовал за свою роль?)
def get_killed_players(mafia_members: dict):
    killed_players = set()
    mafias_voting = []
    # Проверка голосов мафии
    for i in list(mafia_members.keys()):
        if mafia_members[i].role == 'Мафия':
            if mafia_members[i].vote_on_role_voting is None:
                killed_players.add(mafia_members[i].id)
                mafias_voting.append(None)
            else:
                mafias_voting.append(mafia_members[i].vote_on_role_voting)
    # Подведение итогов голосования мафии
    c = Counter(mafias_voting).most_common(2)
    if len(c) > 0:
        if c[0][1] == c[1][1]:
            s = random.choice([c[0][0], c[1][0]])
        else:
            s = c[0][0]
    else:
        s = c[0][0]
    # Хилл Доктором и приход Любовницы обрабатывают список убитых игроков
    doctors_heal = 0
    if s is not None:
        killed_players.add(s)
    for i in list(mafia_members.keys()):
        if mafia_members[i].role == 'Доктор':
            if mafia_members[i].vote_on_role_voting is None:
                killed_players.add(mafia_members[i].id)
            else:
                if mafia_members[i].vote_on_role_voting in killed_players:
                    killed_players.remove(mafia_members[i].vote_on_role_voting)
                    doctors_heal = mafia_members[i].vote_on_role_voting
    # Обработка Любовницы, если док полечил убитую любовницу никто не умирает
    # Если док вылечил убитого любовницей любовница умирает, а чел нет
    for i in list(mafia_members.keys()):
        if mafia_members[i].role == 'Любовница':
            if mafia_members[i].vote_on_role_voting is None:
                killed_players.add(mafia_members[i].id)
            else:
                if mafia_members[i].id in killed_players:
                    if mafia_members[i].vote_on_role_voting != doctors_heal:
                        killed_players.add(i)
                        killed_players.add(mafia_members[i].vote_on_role_voting)
                    else:
                        killed_players.add(i)
                else:
                    if mafia_members[i].vote_on_role_voting in killed_players:
                        killed_players.remove(mafia_members[i].vote_on_role_voting)
    return list(killed_players)
