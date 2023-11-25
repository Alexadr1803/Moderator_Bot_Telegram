from aiogram import F, types, Router
import random
import mafia_func
from aiogram.types import FSInputFile
import sys
import os
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import bot
# Главные переменные, я буду над ними еще работать (надо уменьшить их количество)
# Роутер - ответвление бота чисто под мафию
# sessions - все данные по активным играм
router = Router()
sessions = {}

night_art = FSInputFile("images/night_art.jpg")
day_art = FSInputFile("images/day_art.jpg")


class Player:
    def __init__(self, full_name, user_id):
        self.role = None
        self.id = user_id
        self.full_name = full_name
        self.vote_on_voting = None
        self.vote_on_role_voting = None
        self.doctor_himself = True


@router.callback_query(F.data == 'check_role')
async def check_mafia_role(call: CallbackQuery):
    if call.message.chat.id in sessions.keys():
        if call.from_user.id in sessions[call.message.chat.id]["Живые игроки"]:
            if mafia_func.count_mafia(sessions[call.message.chat.id]['Живые игроки']) != 1 and sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].role == 'Мафия':
                string = 'Мафии в игре:\n'
                for i in sessions[call.message.chat.id]['Живые игроки'].keys():
                    if sessions[call.message.chat.id]['Живые игроки'][i].role == 'Мафия':
                        string += sessions[call.message.chat.id]['Живые игроки'][i].full_name + "\n"
                await call.answer(f"Ваша роль {sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].role}\n{string}", show_alert=True)
            else:
                await call.answer(f"Ваша роль {sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].role}", show_alert=True)
        else:
            await call.answer("Вы не зарегистрировались на игру!", show_alert=True)
    else:
        await call.answer("Эта кнопка больше не действительна!", show_alert=True)


@router.callback_query(F.data == 'register')
async def registration_to_game(call: CallbackQuery):
    if call.from_user.id not in list(sessions[call.message.chat.id]['Живые игроки'].keys()):
        sessions[call.message.chat.id]['Живые игроки'][call.from_user.id] = Player(call.from_user.full_name, user_id=call.from_user.id)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Участвую",
            callback_data="register")
        )
        user_names = [i.full_name for i in list(sessions[call.message.chat.id]['Живые игроки'].values())]
        await call.message.edit_text(
            f"ℹ️ Начата регистрация на игру <b>Мафия</b>\nИгроки: {', '.join(user_names)}",
            reply_markup=builder.as_markup())
        await call.answer("Вы зарегистрированы!", show_alert=True)
    else:
        await call.answer("Вы уже зарегистрированы на игру!", show_alert=True)


@router.callback_query(lambda message: '%doctor%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    if call.from_user.id in sessions[call.message.chat.id]['Живые игроки'].keys():
        if sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].role == "Доктор":
            if int(call.data.split('|')[1]) == call.from_user.id:
                if sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].doctor_himself:
                    sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].doctor_himself = False
                    sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_role_voting = call.from_user.id
                    await call.answer(f'Вы решили эгоистично помочь себе!', show_alert=True)
                else:
                    await call.answer(f'Вы уже помогали себе в этой игре!', show_alert=True)
            else:
                sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_role_voting = int(call.data.split('|')[1])
                await call.answer(f'Вы решили помочь {sessions[call.message.chat.id]["Живые игроки"][int(call.data.split("|")[1])].full_name}!',
                                  show_alert=True)
        else:
            await call.answer(f'Вы не доктор!', show_alert=True)
    else:
        await call.answer("Вы не участвуете в игре!", show_alert=True)


@router.callback_query(lambda message: '%lover%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    if call.from_user.id in sessions[call.message.chat.id]['Живые игроки'].keys():
        if sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].role == "Любовница":
            if sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_role_voting is None:
                if int(call.data.split('|')[1]) == call.from_user.id:
                    await call.answer(f'Вы не можете ублажить себя!\nЧто за извращение?!', show_alert=True)
                else:
                    sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_role_voting = int(call.data.split('|')[1])
                    await call.answer(f'Вы решили ублажить {sessions[call.message.chat.id]["Живые игроки"][int(call.data.split("|")[1])].full_name}!',
                                      show_alert=True)
            else:
                await call.answer(f'Вы уже навестили {sessions[call.message.chat.id]["Живые игроки"][sessions[call.message.chat.id]["Живые игроки"][call.from_user.id]].full_name}!',
                                  show_alert=True)
        else:
            await call.answer(f'Вы не любовница!', show_alert=True)
    else:
        await call.answer("Вы не участвуете в игре!", show_alert=True)


@router.callback_query(lambda message: '%sheriff%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    if call.from_user.id in sessions[call.message.chat.id]['Живые игроки'].keys():
        if sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].role == "Шериф":
            if sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_role_voting is None:
                if sessions[call.message.chat.id]['Живые игроки'][int(call.data.split('|')[1])].role == "Мафия":
                    sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_role_voting = False
                    await call.answer("Это определенно плохой чувак!", show_alert=True)
                else:
                    sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_role_voting = False
                    await call.answer("Это определенно ровный типок!", show_alert=True)
            else:
                await call.answer("Ты уже выследил одного этой ночью!", show_alert=True)
        else:
            await call.answer(f'Вы не шериф!', show_alert=True)
    else:
        await call.answer("Вы не участвуете в игре!", show_alert=True)


@router.callback_query(lambda message: '%mafia%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    if call.from_user.id in sessions[call.message.chat.id]['Живые игроки']:
        if sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].role == "Мафия":
            if sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_role_voting is None:
                sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_role_voting = int(call.data.split('|')[1])
                await call.answer(f'Вы решили убить {sessions[call.message.chat.id]["Живые игроки"][int(call.data.split("|")[1])].full_name}',
                                  show_alert=True)
            else:
                await call.answer(f'Вы уже предложили убить {sessions[call.message.chat.id]["Живые игроки"][sessions[call.message.chat.id]["Живые игроки"][call.from_user.id].vote_on_role_voting]}!',
                                  show_alert=True)
        else:
            await call.answer(f'Вы не мафия!(и не клоун)\nP.S Наверное...', show_alert=True)
    else:
        await call.answer("Вы не участвуете в игре!", show_alert=True)


@router.callback_query(lambda message: '%vote%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    if call.from_user.id in sessions[call.message.chat.id]['Живые игроки']:
        if sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_voting is None:
            sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].vote_on_voting = int(call.data.split('|')[1])
            await call.answer(f'Вы решили изгнать {sessions[call.message.chat.id]["Живые игроки"][int(call.data.split("|")[1])].full_name}!',
                              show_alert=True)
            await bot.bot.send_message(chat_id=call.message.chat.id, message_thread_id=call.message.message_thread_id, text=f"{sessions[call.message.chat.id]['Живые игроки'][call.from_user.id].full_name} решил изгнать {sessions[call.message.chat.id]['Живые игроки'][int(call.data.split('|')[1])].full_name}!")
        else:
            await call.answer(
                f'Вы уже приняли участие в этом голосовании!',
                show_alert=True)
    else:
        await call.answer("Вы не участвуете в игре!", show_alert=True)


@router.message(Command('start_mafia'))
async def create_mafia_registration(msg: Message):
    global night_art, day_art, sessions
    if msg.chat.id not in sessions.keys():
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Участвую",
            callback_data="register")
        )
        sessions[msg.chat.id] = {'Живые игроки': {}, 'Мертвые игроки': {}, 'Ночь': False, 'День': 0}
        message = await msg.answer(
            f"ℹ️ Начата регистрация на игру <b>Мафия</b>!",
            reply_markup=builder.as_markup())
        await asyncio.sleep(30)
        if msg.chat.id in sessions.keys() and len(sessions[msg.chat.id]['Живые игроки']) < 4:
            sessions.pop(msg.chat.id)
            await message.delete()
            await msg.answer("Игра отменяется из-за недостатка игроков! :(")
        elif msg.chat.id in sessions.keys():
            await message.delete()
            roles = ['Доктор']
            if len(sessions[msg.chat.id]['Живые игроки'].keys()) >= 6:
                roles.append('Любовница')
                roles.append("Шериф")
            for _ in range(int(len(sessions[msg.chat.id]['Живые игроки']) / 3.5)):
                roles.append('Мафия')
            for _ in range(len(sessions[msg.chat.id]['Живые игроки']) - len(roles)):
                roles.append('Мирный')
            random.shuffle(roles)
            i = 0
            for j in list(sessions[msg.chat.id]['Живые игроки'].keys()):
                sessions[msg.chat.id]['Живые игроки'][j].role = roles[i]
                i += 1
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="Узнать роль", callback_data="check_role"))
            if msg.chat.id in sessions.keys():
                await msg.answer("🕵️ Роли выданы!\nНажмите, чтобы узнать свою:", reply_markup=builder.as_markup())
                await asyncio.sleep(10)
                sessions[msg.chat.id]['Ночь'] = True
            if msg.chat.id in sessions.keys():
                await msg.answer_photo(caption=
                                       "🌃 Наступает ночь\nНа улицы города выходят лишь самые отважные и "
                                       "бесстрашные.\nУтром попробуем "
                                       "сосчитать их головы...", photo=night_art)
                alive_players = [i.full_name for i in list(sessions[msg.chat.id]['Живые игроки'].values())]
                await msg.answer(f"😇 Живые игроки:\n<b>{'</b>, <b>'.join(alive_players)}</b>",
                                 parse_mode=ParseMode.HTML)
                await asyncio.sleep(5)
            while 0 != mafia_func.count_mafia(sessions[msg.chat.id]['Живые игроки']) < mafia_func.count_peace(sessions[msg.chat.id]['Живые игроки']) and msg.chat.id in sessions.keys():
                sessions[msg.chat.id]['День'] += 1
                mafia_voting = await msg.answer("🔫 Мафия выходит на охоту",
                                                reply_markup=mafia_func.create_prefix_keyboard(sessions[msg.chat.id]['Живые игроки'],
                                                                                               '%mafia%'))
                await asyncio.sleep(15 * mafia_func.count_mafia(sessions[msg.chat.id]['Живые игроки']))
                await mafia_voting.edit_text("🔫 Мафия сделала свой выбор (мб даже не в свою пользу)!")
                await asyncio.sleep(2)
                if msg.chat.id not in sessions.keys():
                    break
                if mafia_func.count_doctor(sessions[msg.chat.id]['Живые игроки']) != 0:
                    doctor = await msg.answer("🧑‍⚕️Доктор вышел на дежурство!\nКого же он вылечит? Ну или просто "
                                              "профилактирует...",
                                              reply_markup=mafia_func.create_prefix_keyboard(sessions[msg.chat.id]['Живые игроки'],
                                                                                             "%doctor%"))
                    await asyncio.sleep(15)
                    await doctor.edit_text("🧑‍⚕️ Доктор выбрал кому помочь...")
                else:
                    await msg.answer("🥀 К сожалению, доктор уже не сможет никому помочь...")
                if msg.chat.id not in sessions.keys():
                    break
                await asyncio.sleep(2)
                if mafia_func.count_sheriff(sessions[msg.chat.id]['Живые игроки']) != 0:
                    sheriff = await msg.answer("️🕵️‍♂️ Шериф вышел на задание, чтобы узнать, кто плохой мальчик",
                                               reply_markup=mafia_func.create_prefix_keyboard(sessions[msg.chat.id]['Живые игроки'],
                                                                                              "%sheriff%"))
                    await asyncio.sleep(2)
                    await sheriff.edit_text("🕵️‍♂️ Шериф узнал, кто плохой мальчик или не узнал (его проблемы)")
                    await asyncio.sleep(2)
                else:
                    await msg.answer("🥀 Шериф ушел в отставку...\nМафия ликует...")
                    await asyncio.sleep(2)

                if mafia_func.count_lover(sessions[msg.chat.id]['Живые игроки']) != 0:
                    loveka = await msg.answer("💃 Любовница решает, кто умр... кхм, будет спать счастливым!",
                                              reply_markup=mafia_func.create_prefix_keyboard(sessions[msg.chat.id]['Живые игроки'], "%lover%"))
                    await asyncio.sleep(15)
                    await loveka.edit_text("💃 Любовница решила, кого ублажить этой ночью, может даже "
                                           "ценою своей или чужой жизни\nP.S Может даже всеми сразу...!")
                else:
                    await msg.answer("🥀 В эту ночь жители будут грустные спать одни...")
                    await asyncio.sleep(3)
                await asyncio.sleep(3)
                killed_players = mafia_func.get_killed_players(sessions[msg.chat.id]['Живые игроки'])
                await msg.answer_photo(caption=
                                       f"☀️ <b>День {sessions[msg.chat.id]['День']}</b>\n Солнце всходит, подсушивая н"
                                       "а тротуарах пролитую ночью кровь...", parse_mode=ParseMode.HTML, photo=day_art)
                await asyncio.sleep(3)
                if killed_players and msg.chat.id in sessions.keys():
                    roles_str = '👹 Список убийств пополнился\n\nРоли жертв:\n\n'
                    for i in killed_players:
                        roles_str += (f'💀 {sessions[msg.chat.id]["Живые игроки"][i].full_name}'
                                      f' - <b>{sessions[msg.chat.id]["Живые игроки"][i].role}</b>\n')
                    await msg.answer(roles_str, parse_mode=ParseMode.HTML)
                    for i in killed_players:
                        sessions[msg.chat.id]["Мертвые игроки"][i] = sessions[msg.chat.id]["Живые игроки"][i]
                        sessions[msg.chat.id]["Живые игроки"].pop(i)
                elif not killed_players and msg.chat.id in sessions.keys():
                    await msg.answer("🤞 Этой ночью никого не убили...")

                if 0 != mafia_func.count_mafia(sessions[msg.chat.id]["Живые игроки"]) < mafia_func.count_peace(sessions[msg.chat.id]["Живые игроки"]) and msg.chat.id in sessions.keys():
                    await msg.answer(
                        f"🔎 Кто-то из них...\n\n<b>"
                        f"{'</b>, <b>'.join([i.full_name for i in list(sessions[msg.chat.id]['Живые игроки'].values())])}</b>\nКоличество "
                        f"мафий: <b>{mafia_func.count_mafia(sessions[msg.chat.id]['Живые игроки'])}</b>\n\nВам дано"
                        " время на обсуждение!", parse_mode=ParseMode.HTML)
                    sessions[msg.chat.id]['Ночь'] = False
                    await asyncio.sleep(90)
                    sessions[msg.chat.id]['Ночь'] = True
                    vote = await msg.answer("💀 Выберите того, кто по вашему мнению достоин смерти",
                                            reply_markup=mafia_func.create_prefix_keyboard(sessions[msg.chat.id]['Живые игроки'], '%vote%'))
                    await asyncio.sleep(15)
                    await vote.delete()
                    for i in sessions[msg.chat.id]["Живые игроки"].keys():
                        sessions[msg.chat.id]["Живые игроки"][i].vote_on_role_voting = None
                        sessions[msg.chat.id]["Живые игроки"][i].vote_on_voiting = None

                    k = mafia_func.get_verdict(sessions[msg.chat.id]['Живые игроки'])
                    if k[0] and k[1] is not None:
                        killed_players = [k[1]]
                        roles_str = '🩸 По итогам голосования был изгнан(а):\n'
                        for i in killed_players:
                            roles_str += f'{sessions[msg.chat.id]["Живые игроки"][i].full_name} - <b>{sessions[msg.chat.id]["Живые игроки"][i].role}</b>\n'
                        await msg.answer(roles_str, parse_mode=ParseMode.HTML)
                        for i in killed_players:
                            sessions[msg.chat.id]['Мертвые игроки'][i] = sessions[msg.chat.id]['Живые игроки'][i]
                            sessions[msg.chat.id]['Живые игроки'].pop(i)
                        for i in sessions[msg.chat.id]['Живые игроки'].keys():
                            sessions[msg.chat.id]['Живые игроки'][i].vote_on_voting = None
                        if 0 != mafia_func.count_mafia(sessions[msg.chat.id]['Живые игроки']) < mafia_func.count_peace(
                                sessions[msg.chat.id]['Живые игроки']) and msg.chat.id in sessions.keys():
                            sessions[msg.chat.id]['Ночь'] = True
                            await msg.answer_photo(caption=
                                                   "🌃 Наступает ночь\nНа улицы города выходят лишь самые отважные и "
                                                   "бесстрашные.\nУтром попробуем "
                                                   "сосчитать их головы...", photo=night_art)
                            alive_players = [i.full_name for i in list(sessions[msg.chat.id]['Живые игроки'].values())]
                            await msg.answer(f"😇 Живые игроки:\n<b>{'</b>, <b>'.join(alive_players)}</b>",
                                             parse_mode=ParseMode.HTML)
                            await asyncio.sleep(5)

                    elif k[0] and k[1] is None:
                        sessions[msg.chat.id]['Ночь'] = True
                        await msg.answer("🙄 Большинство решило воздержаться от голосования!\nНикто не изгнан!")
                        await asyncio.sleep(3)
                        if msg.chat.id in sessions.keys():
                            await msg.answer_photo(caption=
                                                   "🌃 Наступает ночь\nНа улицы города выходят лишь самые отважные и "
                                                   "бесстрашные.\nУтром "
                                                   "попробуем "
                                                   "сосчитать их головы...", photo=night_art)
                            alive_players = [i.full_name for i in list(sessions[msg.chat.id]['Живые игроки'].values())]
                            await msg.answer(f"😇 Живые игроки:\n<b>{'</b>, <b>'.join(alive_players)}</b>",
                                             parse_mode=ParseMode.HTML)
                            await asyncio.sleep(3)

                    else:
                        sessions[msg.chat.id]['Ночь'] = True
                        await msg.answer("🤓 Ответы жителей разошлись. Разошлись и сами жители.\nНикто не изгнан!")
                        await asyncio.sleep(3)
                        if msg.chat.id in sessions.keys():
                            await msg.answer_photo(caption=
                                                   "🌃 Наступает ночь\nНа улицы города выходят лишь самые отважные и "
                                                   "бесстрашные.\nУтром попробуем "
                                                   "сосчитать их головы...", photo=night_art)
                            alive_players = [i.full_name for i in list(sessions[msg.chat.id]['Живые игроки'].values())]
                            await msg.answer(f"😇 Живые игроки:\n<b>{'</b>, <b>'.join(alive_players)}</b>",
                                             parse_mode=ParseMode.HTML)
                            await asyncio.sleep(3)
                else:
                    break
            if mafia_func.count_mafia(sessions[msg.chat.id]['Живые игроки']) == 0 and msg.chat.id in sessions.keys():
                await msg.answer("Игра окончена!!")
                await asyncio.sleep(2)
                await msg.answer("Победили мирные!")
                roles_str = 'Победители:\n\n'
                for i in list(sessions[msg.chat.id]['Живые игроки'].keys()):
                    roles_str += f'🏆 {sessions[msg.chat.id]["Живые игроки"][i].full_name} - <b>{sessions[msg.chat.id]["Живые игроки"][i].role}</b>\n'
                roles_str += "\nПроигравшие или мертвые:\n\n"
                for i in sessions[msg.chat.id]['Мертвые игроки'].keys():
                    roles_str += f'❌ {sessions[msg.chat.id]["Мертвые игроки"][i].full_name} - <b>{sessions[msg.chat.id]["Мертвые игроки"][i].role}</b>\n'
                await msg.answer(roles_str)
                sessions.pop(msg.chat.id)
            elif mafia_func.count_mafia(sessions[msg.chat.id]['Живые игроки']) != 0 and msg.chat.id in sessions.keys():
                await msg.answer("Игра окончена!!")
                await asyncio.sleep(2)
                await msg.answer("Победила мафия!")
                for i in list(sessions[msg.chat.id]['Живые игроки'].keys()):
                    if sessions[msg.chat.id]['Живые игроки'][i].role != "Мафия":
                        sessions[msg.chat.id]['Мертвые игроки'][i] = sessions[msg.chat.id]['Живые игроки'][i]
                        sessions[msg.chat.id]['Живые игроки'].pop(i)
                roles_str = 'Победители:\n\n'
                for i in sessions[msg.chat.id]['Живые игроки'].keys():
                    roles_str += f'🏆 {sessions[msg.chat.id]["Живые игроки"][i].full_name} - <b>{sessions[msg.chat.id]["Живые игроки"][i].role}</b>\n'
                roles_str += "\nПроигравшие или мертвые:\n\n"
                for i in sessions[msg.chat.id]['Мертвые игроки'].keys():
                    roles_str += f'❌ {sessions[msg.chat.id]["Мертвые игроки"][i].full_name} - <b>{sessions[msg.chat.id]["Мертвые игроки"][i].role}</b>\n'
                await msg.answer(roles_str)
                sessions.pop(msg.chat.id)


@router.message(Command('end_mafia'))
async def end_game(msg: Message):
    if msg.chat.id in sessions.keys():
        roles_str = 'Роли живых игроков:\n\n'
        for i in sessions[msg.chat.id]['Живые игроки'].keys():
            roles_str += f'{sessions[msg.chat.id]["Живые игроки"][i].full_name} - <b>{sessions[msg.chat.id]["Живые игроки"][i].role}</b>\n'
        await msg.answer(roles_str, parse_mode=ParseMode.HTML)
    sessions.pop(msg.chat.id)
    await msg.answer("Игра отменена успешно!")


@router.message()
async def night_mode(msg: Message):
    try:
        if sessions[msg.chat.id]['Ночь'] and msg.from_user.id in sessions[msg.chat.id]['Живые игроки'].keys() or msg.from_user.id in sessions[msg.chat.id]['Мертвые игроки']:
            await msg.delete()
    except KeyError:
        pass

