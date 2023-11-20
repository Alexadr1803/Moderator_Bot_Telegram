from aiogram import F, types, Router
import random
import mafia_func
from aiogram.types import FSInputFile
import sys
import os
user_active_repeat = False
router = Router()
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from bot import python

sessies = {}
mafia_active = False
night_active = False
mafia_members = {}
mafia_dead_members = {}
days = 0
merce = 0

night_art = FSInputFile("images/night_art.jpg")
day_art = FSInputFile("images/day_art.jpg")


async def restart_script():
    global sessies
    if not sessies:
        os.execl(python, python, *sys.argv)


class Player:
    def __init__(self, full_name, user_id):
        self.role = None
        self.id = user_id
        self.full_name = full_name
        self.vote_on_voting = None
        self.vote_on_role_voting = None
        self.doctor_himself = True
        self.check = True


@router.callback_query(F.data == 'check_role')
async def check_mafia_role(call: CallbackQuery):
    if call.from_user.id in list(mafia_members.keys()):
        if mafia_func.count_mafia(mafia_members) != 1 and mafia_members[call.from_user.id].role == 'Мафия':
            string = 'Мафии в игре:\n'
            for i in mafia_members.keys():
                if mafia_members[i].role == 'Мафия':
                    string += mafia_members[i].full_name + "\n"
            await call.answer(f"Ваша роль {mafia_members[call.from_user.id].role}\n{string}", show_alert=True)
        else:
            await call.answer(f"Ваша роль {mafia_members[call.from_user.id].role}", show_alert=True)
    else:
        await call.answer("Вы не зарегистрировались на игру!", show_alert=True)


@router.callback_query(F.data == 'register')
async def registration_to_game(call: CallbackQuery):
    if call.from_user.id not in list(mafia_members.keys()):
        mafia_members[call.from_user.id] = Player(call.from_user.full_name, user_id=call.from_user.id)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Участвую",
            callback_data="register")
        )
        user_names = [i.full_name for i in list(mafia_members.values())]
        await call.message.edit_text(
            f"ℹ️ Начата регистрация на игру <b>Мафия</b>\nИгроки: {', '.join(user_names)}",
            reply_markup=builder.as_markup())
        await call.answer("Вы зарегистрированы!", show_alert=True)
    else:
        await call.answer("Вы уже зарегистрированы на игру!", show_alert=True)


@router.callback_query(lambda message: '%doctor%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    global merce
    if call.from_user.id in mafia_members.keys():
        print(mafia_members[call.from_user.id].doctor_himself)
        if mafia_members[call.from_user.id].role == "Доктор":
            if int(call.data.split('|')[1]) == call.from_user.id:
                if mafia_members[call.from_user.id].doctor_himself:
                    merce = 1
                    mafia_members[call.from_user.id].doctor_himself = False
                    mafia_members[call.from_user.id].vote_on_role_voting = call.from_user.id
                    await call.answer(f'Вы решили эгоистично помочь себе!', show_alert=True)
                elif merce == 1:
                    await call.answer(f'Вы решили эгоистично помочь себе!', show_alert=True)
                else:
                    await call.answer(f'Вы уже помогали себе в этой игре!', show_alert=True)
            else:
                if merce == 1:
                    mafia_members[call.from_user.id].doctor_himself = True
                    merce = 0
                    mafia_members[call.from_user.id].vote_on_role_voting = int(call.data.split('|')[1])
                    await call.answer(f'Вы решили помочь {mafia_members[int(call.data.split("|")[1])].full_name}!',
                                      show_alert=True)
                else:
                    mafia_members[call.from_user.id].vote_on_role_voting = int(call.data.split('|')[1])
                    await call.answer(f'Вы решили помочь {mafia_members[int(call.data.split("|")[1])].full_name}!',
                                      show_alert=True)
        else:
            await call.answer(f'Вы не доктор!', show_alert=True)
    else:
        await call.answer("Вы не учавствуете в игре!", show_alert=True)


@router.callback_query(lambda message: '%lover%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    if call.from_user.id in mafia_members.keys():
        if mafia_members[call.from_user.id].role == "Любовница":
            if int(call.data.split('|')[1]) == call.from_user.id:
                await call.answer(f'Вы не можете ублажить себя!\nЧто за извращение?!', show_alert=True)
            else:
                mafia_members[call.from_user.id].vote_on_role_voting = int(call.data.split('|')[1])
                await call.answer(f'Вы решили ублажить {mafia_members[int(call.data.split("|")[1])].full_name}!',
                                  show_alert=True)
        else:
            await call.answer(f'Вы не любовница!', show_alert=True)
    else:
        await call.answer("Вы не учавствуете в игре!", show_alert=True)


@router.callback_query(lambda message: '%sheriff%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    if call.from_user.id in mafia_members.keys():
        if mafia_members[call.from_user.id].role == "Шериф":
            if mafia_members[call.from_user.id].check and mafia_members[int(call.data.split('|')[1])].role == "Мафия":
                mafia_members[call.from_user.id].check = False
                await call.answer("Это определенно плохой чувак!", show_alert=True)
            elif mafia_members[call.from_user.id].check and mafia_members[int(call.data.split('|')[1])].role != "Мафия":
                mafia_members[call.from_user.id].check = False
                await call.answer("Это определенно ровный типок!", show_alert=True)
            else:
                await call.answer("Ты уже выследил одного этой ночью!", show_alert=True)
        else:
            await call.answer(f'Вы не шериф!', show_alert=True)
    else:
        await call.answer("Вы не учавствуете в игре!", show_alert=True)


@router.callback_query(lambda message: '%mafia%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    if call.from_user.id in mafia_members:
        if mafia_members[call.from_user.id].role == "Мафия":
            mafia_members[call.from_user.id].vote_on_role_voting = int(call.data.split('|')[1])
            await call.answer(f'Вы решили убить {mafia_members[int(call.data.split("|")[1])].full_name}',
                              show_alert=True)
        else:
            await call.answer(f'Вы не мафия!(и не клоун)\nP.S Наверное...', show_alert=True)
    else:
        await call.answer("Вы не учавствуете в игре!", show_alert=True)


@router.callback_query(lambda message: '%vote%' in message.data)
async def mafia_vote(call: types.CallbackQuery):
    if call.from_user.id in mafia_members:
        mafia_members[call.from_user.id].vote_on_voting = int(call.data.split('|')[1])
        await call.answer(f'Вы решили изгнать {mafia_members[int(call.data.split("|")[1])].full_name}!',
                          show_alert=True)
    else:
        await call.answer("Вы не учавствуете в игре!", show_alert=True)


@router.message(Command('start_mafia'))
async def create_mafia_registration(msg: Message):
    global mafia_active, mafia_members, night_active, mafia_dead_members, days, merce, night_art, day_art
    if not mafia_active:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Участвую",
            callback_data="register")
        )
        mafia_active = True
        user_names = [i.full_name for i in list(mafia_members.values())]
        message = await msg.answer(
            f"ℹ️ Начата регистрация на игру <b>Мафия</b>\nИгроки: {', '.join(user_names)}",
            reply_markup=builder.as_markup())
        await asyncio.sleep(30)
        if len(mafia_members) < 4 and mafia_active:
            mafia_members = {}
            mafia_active = False
            await message.delete()
            await msg.answer("Игра отменяется из-за недостатка игроков! :(")
        elif mafia_active:
            await message.delete()
            roles = ['Доктор']
            if len(mafia_members.keys()) >= 6:
                roles.append('Любовница')
                roles.append("Шериф")
            for _ in range(int(len(mafia_members) / 3.5)):
                roles.append('Мафия')
            for _ in range(len(mafia_members) - len(roles)):
                roles.append('Мирный')
            random.shuffle(roles)
            i = 0
            for j in list(mafia_members.keys()):
                mafia_members[j].role = roles[i]
                i += 1
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                text="Узнать роль",
                callback_data="check_role")
            )
            if mafia_active:
                await msg.answer("🕵️ Роли выданы!\nНажмите, чтобы узнать свою:", reply_markup=builder.as_markup())
                await asyncio.sleep(10)
                night_active = True
            if mafia_active:
                await msg.answer_photo(caption=
                                       "🌃 Наступает ночь\nНа улицы города выходят лишь самые отважные и "
                                       "бесстрашные.\nУтром попробуем"
                                       "сосчитать их головы...", photo=night_art)
                alive_players = [i.full_name for i in list(mafia_members.values())]
                await msg.answer(f"😇 Живые игроки:\n<b>{'</b>, <b>'.join(alive_players)}</b>",
                                 parse_mode=ParseMode.HTML)
                await asyncio.sleep(5)
            while 0 != mafia_func.count_mafia(mafia_members) < mafia_func.count_peace(mafia_members) and mafia_active:
                days += 1
                mafia_voting = await msg.answer("🔫 Мафия выходит на охоту",
                                                reply_markup=mafia_func.create_prefix_keyboard(mafia_members,
                                                                                               '%mafia%'))
                await asyncio.sleep(10 * mafia_func.count_mafia(mafia_members))
                await mafia_voting.edit_text("🔫 Мафия сделала свой выбор (мб даже не в свою пользу)!")
                await asyncio.sleep(2)
                if not mafia_active:
                    break
                if mafia_func.count_doctor(mafia_members) != 0:
                    doctor = await msg.answer("🧑‍⚕️Доктор вышел на дежурство!\nКого же он вылечит? Ну или просто "
                                              "профилактирует...",
                                              reply_markup=mafia_func.create_prefix_keyboard(mafia_members,
                                                                                             "%doctor%"))
                    await asyncio.sleep(10)
                    await doctor.edit_text("🧑‍⚕️ Доктор выбрал кому помочь...")
                else:
                    await msg.answer("🥀 К сожалению, доктор уже не сможет никому помочь...")

                merce = 0
                if not mafia_active:
                    break
                await asyncio.sleep(2)
                if mafia_func.count_sheriff(mafia_members) != 0:
                    sheriff = await msg.answer("️🕵️‍♂️ Шериф вышел на задание, чтобы узнать, кто плохой мальчик",
                                               reply_markup=mafia_func.create_prefix_keyboard(mafia_members,
                                                                                              "%sheriff%"))
                    await asyncio.sleep(2)
                    await sheriff.edit_text("🕵️‍♂️ Шериф узнал, кто плохой мальчик или не узнал (его проблемы)")
                    await asyncio.sleep(2)
                else:
                    await msg.answer("🥀 Шериф ушел в отставку...\nМафия ликует...")
                    await asyncio.sleep(2)

                if mafia_func.count_lover(mafia_members) != 0:
                    loveka = await msg.answer("💃 Любовница решает, кто умр... кхм, будет спать счастливым!",
                                              reply_markup=mafia_func.create_prefix_keyboard(mafia_members, "%lover%"))
                    await asyncio.sleep(10)
                    await loveka.edit_text("💃 Любовница решила, кого ублажить этой ночью, может даже "
                                           "ценою своей или чужой жизни\nP.S Может даже всеми сразу...!")
                else:
                    await msg.answer("🥀 В эту ночь жители буду грустные спать одни...")
                    await asyncio.sleep(3)
                await asyncio.sleep(3)
                killed_players = mafia_func.get_killed_players(mafia_members)
                await msg.answer_photo(caption=
                                       f"☀️ <b>День {days}</b>\n Солнце всходит, подсушивая на тротуарах пролитую ночью "
                                       f"кровь...", parse_mode=ParseMode.HTML, photo=day_art)
                await asyncio.sleep(3)
                print(killed_players)
                if killed_players and mafia_active:
                    roles_str = '👹 Список убийств пополнился\n\nРоли жертв:\n\n'
                    for i in killed_players:
                        roles_str += f'💀 {mafia_members[i].full_name} - <b>{mafia_members[i].role}</b>\n'
                    await msg.answer(roles_str, parse_mode=ParseMode.HTML)
                    for i in killed_players:
                        mafia_dead_members[i] = mafia_members[i]
                        mafia_members.pop(i)
                elif not killed_players and mafia_active:
                    await msg.answer("🤞 Этой ночью никого не убили...")
                for i in mafia_members.keys():
                    mafia_members[i].vote_on_role_voting = None
                    mafia_members[i].check = True
                if 0 != mafia_func.count_mafia(mafia_members) < mafia_func.count_peace(mafia_members) and mafia_active:
                    alive_players = [i.full_name for i in list(mafia_members.values())]
                    await msg.answer(
                        f"🔎 Кто-то из них...\n\n<b>{'</b>, <b>'.join(alive_players)}</b>\n\nКоличество мафий: {mafia_func.count_mafia(mafia_members)}\n\nВам дано время на обсуждение!",
                        parse_mode=ParseMode.HTML)
                    night_active = False
                    await asyncio.sleep(60)
                    night_active = True
                    vote = await msg.answer("💀 Выберите того, кто по вашему мнению достоин смерти",
                                            reply_markup=mafia_func.create_prefix_keyboard(mafia_members, '%vote%'))
                    await asyncio.sleep(20)
                    await vote.delete()
                    k = mafia_func.get_verdict(mafia_members)
                    if k[0] and k[1] is not None:
                        killed_players = [k[1]]
                        roles_str = '🩸 По итогам голосования был изгнан(а):\n'
                        for i in killed_players:
                            roles_str += f'{mafia_members[i].full_name} - <b>{mafia_members[i].role}</b>\n'
                        await msg.answer(roles_str, parse_mode=ParseMode.HTML)
                        for i in killed_players:
                            mafia_dead_members[i] = mafia_members[i]
                            mafia_members.pop(i)
                        for i in mafia_members.keys():
                            mafia_members[i].vote_on_voting = None
                        if 0 != mafia_func.count_mafia(mafia_members) < mafia_func.count_peace(
                                mafia_members) and mafia_active:
                            night_active = True
                            await msg.answer_photo(caption=
                                                   "🌃 Наступает ночь\nНа улицы города выходят лишь самые отважные и "
                                                   "бесстрашные.\nУтром попробуем"
                                                   "сосчитать их головы...", photo=night_art)
                            alive_players = [i.full_name for i in list(mafia_members.values())]
                            await msg.answer(f"😇 Живые игроки:\n<b>{'</b>, <b>'.join(alive_players)}</b>",
                                             parse_mode=ParseMode.HTML)
                            await asyncio.sleep(5)

                    elif k[0] and k[1] is None:
                        night_active = True
                        await msg.answer("🙄 Большинство решило воздержаться от голосования!\nНикто не изгнан!")
                        await asyncio.sleep(3)
                        if mafia_active:
                            await msg.answer_photo(caption=
                                                    "🌃 Наступает ночь\nНа улицы города выходят лишь самые отважные и "
                                                    "бесстрашные.\nУтром"
                                                    "попробуем"
                                                    "сосчитать их головы...", photo=night_art)
                            alive_players = [i.full_name for i in list(mafia_members.values())]
                            await msg.answer(f"😇 Живые игроки:\n<b>{'</b>, <b>'.join(alive_players)}</b>",
                                            parse_mode=ParseMode.HTML)
                            await asyncio.sleep(3)

                    else:
                        night_active = True
                        await msg.answer("🤓 Ответы жителей разошлись. Разошлись и сами жители.\nНикто не изгнан!")
                        await asyncio.sleep(3)
                        if mafia_active:
                            await msg.answer_photo(caption=
                                                   "🌃 Наступает ночь\nНа улицы города выходят лишь самые отважные и "
                                                   "бесстрашные.\nУтром попробуем"
                                                   "сосчитать их головы...", photo=night_art)
                            alive_players = [i.full_name for i in list(mafia_members.values())]
                            await msg.answer(f"😇 Живые игроки:\n<b>{'</b>, <b>'.join(alive_players)}</b>",
                                             parse_mode=ParseMode.HTML)
                            await asyncio.sleep(3)
                else:
                    break
            if mafia_func.count_mafia(mafia_members) == 0 and mafia_active:
                await msg.answer("Игра окончена!!")
                await msg.answer("Победили мирные!")
                roles_str = 'Победители:\n\n'
                for i in list(mafia_members.keys()):
                    roles_str += f'🏆 {mafia_members[i].full_name} - <b>{mafia_members[i].role}</b>\n'
                roles_str += "\nПроигравшие или мертвые:\n\n"
                for i in mafia_dead_members.keys():
                    roles_str += f'❌ {mafia_dead_members[i].full_name} - <b>{mafia_dead_members[i].role}</b>\n'
                await msg.answer(roles_str)
                mafia_active = False
                night_active = False
                mafia_members = {}
                mafia_dead_members = {}
                days = 0
            elif mafia_func.count_mafia(mafia_members) != 0 and mafia_active:
                await msg.answer("Игра окончена!!")
                await msg.answer("Победила мафия!")
                for i in list(mafia_members.keys()):
                    if mafia_members[i].role != "Мафия":
                        mafia_dead_members[i] = mafia_members[i]
                        mafia_members.pop(i)
                roles_str = 'Победители:\n\n'
                for i in mafia_members.keys():
                    roles_str += f'🏆 {mafia_members[i].full_name} - <b>{mafia_members[i].role}</b>\n'
                roles_str += "\nПроигравшие или мертвые:\n\n"
                for i in mafia_dead_members.keys():
                    roles_str += f'❌ {mafia_dead_members[i].full_name} - <b>{mafia_dead_members[i].role}</b>\n'
                await msg.answer(roles_str)
                mafia_active = False
                night_active = False
                mafia_members = {}
                mafia_dead_members = {}
                days = 0


@router.message(Command('end_mafia'))
async def end_game(msg: Message):
    global mafia_active, night_active, mafia_members, mafia_dead_members, days
    if mafia_active:
        mafia_active = False
        night_active = False
        if mafia_members != {}:
            roles_str = 'Роли живых игроков:\n\n'
            for i in mafia_members.keys():
                roles_str += f'{mafia_members[i].full_name} - <b>{mafia_members[i].role}</b>\n'
            await msg.answer(roles_str, parse_mode=ParseMode.HTML)
        mafia_members = {}
        mafia_dead_members = {}
        days = 0
        await msg.answer("Игра отменена успешно!")


@router.message()
async def night_mode(msg: Message):
    global night_active, mafia_members
    if night_active and msg.from_user.id in list(mafia_members.keys()) or msg.from_user.id in mafia_dead_members:
        await msg.delete()
