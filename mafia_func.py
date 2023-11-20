"""
    Технические функции для игры в мафию
    Тут бы все оптимизировать, если кто шарит можете помочь?
"""

from aiogram import types


# Счетчики персонажей в игре
def count_mafia(mafia_members):
    k = 0
    for i in list(mafia_members.keys()):
        if mafia_members[i].role == 'Мафия':
            k += 1
    return k


def count_peace(mafia_members):
    k = 0
    for i in list(mafia_members.keys()):
        if mafia_members[i].role != 'Мафия':
            k += 1
    return k


def count_lover(mafia_members):
    k = 0
    for i in list(mafia_members.keys()):
        if mafia_members[i].role == 'Любовница':
            k += 1
    return k


def count_doctor(mafia_members):
    k = 0
    for i in list(mafia_members.keys()):
        if mafia_members[i].role == 'Доктор':
            k += 1
    return k


def count_sheriff(mafia_members):
    k = 0
    for i in list(mafia_members.keys()):
        if mafia_members[i].role == 'Шериф':
            k += 1
    return k


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
    verdict = []
    k = 0
    votes = [None]
    for i in mafia_members.keys():
        verdict.append(mafia_members[i].vote_on_voting)
    for i in list(set(verdict)):
        g = verdict.count(i)
        if g > k:
            votes = [i]
            k = g
        elif g == k:
            votes.append(i)
    if len(votes) > 1:
        return [False, None]
    elif votes[0] is None:
        return [True, None]
    else:
        return [True, votes[0]]


# Возращает список умерших игроков, соблюдая все условия (Доктор, Любовница, Житель не голосовал за свою роль?)
def get_killed_players(mafia_members: dict):
    killed_players = set()
    mafias_voting = []
    # Проверка голосов мафии
    for i in list(mafia_members.keys()):
        if mafia_members[i].role == 'Мафия':
            if mafia_members[i].vote_on_role_voting is None:
                killed_players.add(mafia_members[i].id)
            else:
                mafias_voting.append(mafia_members[i].vote_on_role_voting)

    # Подведение итогов голосования мафии
    k = 0
    s = None
    for i in list(set(mafias_voting)):
        if mafias_voting.count(i) >= k:
            k = mafias_voting.count(i)
            s = i

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
