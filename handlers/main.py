import asyncio
import datetime

from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, KeyboardButton, \
    CallbackQuery, LabeledPrice, PreCheckoutQuery, ContentTypes
from asyncio import sleep

from aiogram.utils.callback_data import CallbackData

import keyboards
from aiogram import types
from aiogram.dispatcher import FSMContext

import states
from states import NewItem, Mailing, NewReview, Find, Support, Purchase, NewVacancy, EditItem, EditVacancy
from database.database import Item, User, Reviews, Vacancy

from database.database import DBCommands
from loader import dp, bot


db = DBCommands()
#900230063 or 735318801 = [900230063, 735318801]
pay_token = '390540012:LIVE:15874'

remove_item = CallbackData("remove", "item_id")
add_review_item = CallbackData("add_review", "item_id")
see_review_item = CallbackData("see_review", "item_id")
remove_vacan = CallbackData("remove_vacan", "item_id")
edit_item = CallbackData("edit_item", "item_id")
edit_vacan = CallbackData("edit_vacan", "item_id")
rezume = [
    types.LabeledPrice(label='Публикация резюме', amount=7000)
]
vacancy = [
    types.LabeledPrice(label='Публикация вакансии', amount=15000)
]

@dp.message_handler(CommandStart())
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    user = await db.add_new_user()
    id = user.id
    count_users = await db.count_users()
    text = ("""
    Добро пожаловать в чат по поиску специалистов и вакансий в сфере инфобизнеса! Моя задача - помогать вам на всех этапах поиска!
Я умею создавать, редактировать резюме и вакансии, показывать контакты работодателей.
Поиск специалиста по никнейму /find.
    \nСправка по использованию бота и обратная связь /help.
    """)
    if message.from_user.id == 900230063 or 735318801:
        text += ("\n<b>Админка</b>\n"
                 f"В базе сейчас {count_users} пользователя(ей) бота\n"
                 "Рассылка пользователям бота: /tell_everyone")
    await bot.send_message(chat_id, text, reply_markup=keyboards.main_kb)


################  Проверить
@dp.message_handler(text='Мои публикации')
async def message_text_handler(message: types.Message):
    my_public_rez = await Item.query.where(Item.username == message.from_user.username).gino.all()
    if not my_public_rez:
        await message.answer("<i>Ваших опубликованных резюме не найдено.</i>")
    else:
        await message.answer("<i>Отправляю ваши опубликованные резюме.</i>")
        for num, item in enumerate(my_public_rez):
                text = ("<b>Сфера деятельности: </b>\t{name}\n"
                        "<b>Описание: </b>{desc}\n"
                        "<b>Instagram: </b>https://instagram.com/{contact}")
                    #markup = InlineKeyboardMarkup()

                    #sendBtn = InlineKeyboardButton("Редактировать", callback_data=edit_item.new(item_id=item.id))
                    #markup.add(sendBtn)
                    #reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                    #markup.add(reviewBtn)
                markup = InlineKeyboardMarkup(
                    inline_keyboard=
                        [
                            [
                                InlineKeyboardButton(text=("Редактировать"),
                                                     callback_data=edit_item.new(item_id=item.id)),
                                InlineKeyboardButton(text="Удалить резюме",
                                                     callback_data=remove_item.new(item_id=item.id))
                            ],
                        ]
                    )
                await message.answer(
                            text.format(
                        item_id=item.id,
                        name=item.name,
                        desc=item.desc,
                        username=item.username,
                        contact=item.contactInst), reply_markup=markup)
                await asyncio.sleep(0.3)

    my_public_vac = await Vacancy.query.where(Vacancy.username == message.from_user.username).gino.all()
    if not my_public_vac:
        await message.answer("<i>Ваших опубликованных вакансий не найдено.</i>")
    else:
        await message.answer("<i>Отправляю ваши опубликованные вакансии.</i>")
        for num, vacan in enumerate(my_public_vac):
                    text = ("<b>Требуется: </b>\t{name}\n"
                        "<b>Описание: </b>{desc}\n"
                        "<b>Instagram: </b>https://instagram.com/{contact}")
                    #markup = InlineKeyboardMarkup()

                    #sendBtn = InlineKeyboardButton("Редактировать", callback_data=edit_item.new(item_id=item.id))
                    #markup.add(sendBtn)
                    #reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                    #markup.add(reviewBtn)
                    markup = InlineKeyboardMarkup(
                        inline_keyboard=
                        [
                            [
                                InlineKeyboardButton(text=("Редактировать"),
                                                     callback_data=edit_vacan.new(item_id=vacan.id)),
                                InlineKeyboardButton(text="Удалить вакансию",
                                                     callback_data=remove_vacan.new(item_id=vacan.id))
                            ],
                        ]
                    )
                    await message.answer(
                            text.format(
                        item_id=vacan.id,
                        name=vacan.name,
                        desc=vacan.desc,
                        username=vacan.username,
                        contact=vacan.contactInst), reply_markup=markup)
                    await asyncio.sleep(0.3)


#<a href="https://www.fkwallet.ru"><img src="https://www.fkwallet.ru/assets/2017/images/btns/iconsmall_wallet9.png" title="Прием криптовалют"></a>


@dp.callback_query_handler(edit_vacan.filter())
async def editing_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))

    # Достаем информацию о товаре из базы данных
    vacan = await Vacancy.get(item_id)
    #review = await Reviews.query.where(Reviews.review_id == item_id).gino.all()
    if not vacan:
        await call.message.answer("<i>Такой публикации не существует</i>", reply_markup=keyboards.menuKb)
        return
    else:
        await call.message.answer("<i>Выберите сферу деятельности:</i>", reply_markup=keyboards.change_spec)
        await EditVacancy.Name.set()
        await state.update_data(vacan=vacan)

@dp.callback_query_handler(edit_item.filter())
async def editing_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))

    # Достаем информацию о товаре из базы данных
    item = await Item.get(item_id)
    #review = await Reviews.query.where(Reviews.review_id == item_id).gino.all()
    if not item:
        await call.message.answer("<i>Такой публикации не существует</i>", reply_markup=keyboards.menuKb)
        return
    else:
        await call.message.answer("<i>Выберите сферу деятельности:</i>", reply_markup=keyboards.change_spec)
        await EditItem.Name.set()
        await state.update_data(item=item)

@dp.message_handler(commands=["cancel"], state=EditVacancy)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("<i>Редактирование вакансии отменено.</i>", reply_markup=keyboards.menuKb)
    await state.reset_state()

@dp.message_handler(state=EditVacancy.Name)
async def enter_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    vacan: Vacancy = data.get("vacan")
    name = message.text
    vacan.name = name

    await message.answer(('<b>Требуется:</b> {name}'
        '\n\n<i>Отправьте мне описание:</i>'
        '\nДля отмены нажмите /cancel').format(name=name))

    await EditVacancy.Desc.set()
    await state.update_data(vacan=vacan)

@dp.message_handler(state=EditVacancy.Desc)
async def enter_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    vacan: Vacancy = data.get("vacan")
    desc = message.text
    vacan.desc = desc
    await  message.answer(('<b>Требуется:</b> {name}'
                           '\n<b>Описание:</b> {desc}'
                           '\n\n<i>Отправьте мне свой никнейм (без@) в Instagram:</i>'
                           '\nДля отмены нажмите /cancel').format(name=vacan.name, desc=vacan.desc))
    await EditVacancy.Contact.set()
    await state.update_data(vacan=vacan)

@dp.message_handler(state=EditVacancy.Contact)
async def enter_contactIn(message: types.Message, state: FSMContext):
    data = await state.get_data()
    vacan: Vacancy = data.get("vacan")
    contactInst = message.text
    vacan.contactInst = contactInst
    if not message.from_user.username:
        pass
    else:
        vacan.username = message.from_user.username
    #item.review_id = item.id
    #await item.create()
    #await item.update(id=item.id).apply()
    await vacan.update(name=vacan.name,
                      desc=vacan.desc,
                      contactInst=vacan.contactInst,
                      username=vacan.username,
                      payment=True).apply()
    #await item.update(desc=item.desc).apply()
    #await item.update(contactInst=item.contactInst).apply()
    #await item.update(username=item.username).apply()
    #await item.update(review_id=item.id).apply()
    #await item.update(payment=True).apply()
    await state.reset_state()
    await message.answer("<i>Ваша вакансия отредактирована.</i>", reply_markup=keyboards.menuKb)

@dp.message_handler(commands=["cancel"], state=EditItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("<i>Редактирование резюме отменено.</i>", reply_markup=keyboards.menuKb)
    await state.reset_state()

@dp.message_handler(state=EditItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    name = message.text
    item.name = name

    await message.answer(('<b>Сфера деятельности:</b> {name}'
        '\n\n<i>Отправьте мне описание:</i>'
        '\nДля отмены нажмите /cancel').format(name=name))

    await EditItem.Desc.set()
    await state.update_data(item=item)

@dp.message_handler(state=EditItem.Desc)
async def enter_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    desc = message.text
    item.desc = desc
    await message.answer(('<b>Сфера деятельности:</b> {name}'
                           '\n<b>Описание:</b> {desc}'
                           '\n\n<i>Отправьте мне свой никнейм (без@) в Instagram:</i>'
                           '\nДля отмены нажмите /cancel').format(name=item.name, desc=item.desc))
    await EditItem.Contact.set()
    await state.update_data(item=item)

@dp.message_handler(state=EditItem.Contact)
async def enter_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    contactInst = message.text
    item.contactInst = contactInst
    if not message.from_user.username:
        pass
    else:
        item.username = message.from_user.username
    #item.review_id = item.id
    #await item.create()
    #await item.update(id=item.id).apply()
    await item.update(name=item.name,
                      desc=item.desc,
                      contactInst=item.contactInst,
                      username=item.username,
                      review_id=item.id,
                      payment=True).apply()
    #await item.update(desc=item.desc).apply()
    #await item.update(contactInst=item.contactInst).apply()
    #await item.update(username=item.username).apply()
    #await item.update(review_id=item.id).apply()
    #await item.update(payment=True).apply()
    await state.reset_state()
    await message.answer("<i>Ваше резюме отредактировано.</i>", reply_markup=keyboards.menuKb)

@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    text = "Для поиска резюме по никнейму воспользуйтесь командой /find." \
           "\nЧтобы написать обращение администратору нажмите /support."
    await message.answer(text, reply_markup=keyboards.menuKb)

@dp.message_handler(commands=['support'])
async def send_support(message: types.Message):
    text = "<i>Введите ваше сообщение для администратора:</i>"
    await message.answer(text)
    await Support.SupportMessage.set()

@dp.message_handler(state=Support.SupportMessage)
async def sup_mess(message: types.Message, state: FSMContext):
    support_message = message.text
    await bot.send_message(900230063 or 735318801, support_message)
    await message.answer("<i>Ваше обращение отправлено администратору.</i>", reply_markup=keyboards.menuKb)
    await state.reset_state()

@dp.callback_query_handler(lambda call: call.data == 'find_spec')
async def callback_message(callback_query: types.CallbackQuery):
    text = 'Отлично! Выбери какой специалист тебе требуется:'
    await bot.send_message(callback_query.from_user.id, text, reply_markup=keyboards.change_spec)

@dp.message_handler(text='Продюсер')
async def message_text_handler(message: types.Message):
    all_producers = await db.show_producers()
    if not all_producers:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(all_producers):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)


@dp.callback_query_handler(see_review_item.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))
    await call.message.edit_reply_markup()

    # Достаем информацию о товаре из базы данных
    contact = await Item.get(item_id)
    reviews = await db.show_reviews(item_id)
    if not reviews:
        await call.message.answer("<i>Отзывов нет</i>", reply_markup=keyboards.menuKb)
        return
    else:
        await call.message.answer("<i>Отправляю отзывы специалиста:</i>")
        for num, review in enumerate(reviews):
            text = ("<b>Отзывы о</b> @{contact}\n"
                    "<b>От: @{from_us}</b>\n\n"
                    "<i>{review_text}</i>")
            await call.message.answer(text.format(
                id=item_id,
                review_id=review.review_id,
                review_text=review.review_text,
                contact=contact.username,
                from_us=review.from_us
            ), reply_markup=keyboards.menuKb)


@dp.callback_query_handler(remove_item.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))

    # Достаем информацию о товаре из базы данных
    item = await Item.get(item_id)
    #review = await Reviews.query.where(Reviews.review_id == item_id).gino.all()
    if not item:
        await call.message.answer("<i>Такого резюме не существует</i>", reply_markup=keyboards.menuKb)
        return
    else:
        await Reviews.delete.where(Reviews.review_id == item_id).gino.status()
        await item.delete()
    text = "<i>Вы удалили резюме.</i>"
    await call.message.answer(text, reply_markup=keyboards.menuKb)

@dp.message_handler(commands=['find'])
async def find_message(message: types.Message):
    await message.answer("Введите никнейм специалиста (никнейм в Telegram), которого хотите найти (например, petr_p)")
    await Find.Find.set()

@dp.message_handler(state=Find.Find)
async def enter_nick(message: types.Message, state: FSMContext):
    contact = message.text
    get_contact = await Item.query.where(Item.username == contact).gino.first()
    if not get_contact:
        await message.answer("Специалиста с таким никнеймом не найдено.", reply_markup=keyboards.menuKb)
    else:
        text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text=("Добавить отзыв"),
                                         callback_data=add_review_item.new(item_id=get_contact.id)),
                    InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=get_contact.id))
                ],
            ]
        )
        sendBtn = InlineKeyboardButton(text="Написать специалисту",
                                       url=('t.me/{contact}').format(contact=get_contact.username))
        markup.add(sendBtn)
        if message.from_user.id == 900230063 or 735318801:
            reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=get_contact.id))
            markup.add(reviewBtn)

        await message.answer(
                text.format(
            item_id=get_contact.id,
            name=get_contact.name,
            desc=get_contact.desc,
            username=get_contact.username,
            contact=get_contact.contactInst), reply_markup=markup)
        await asyncio.sleep(0.3)
    await state.reset_state()

@dp.callback_query_handler(add_review_item.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))

    # Достаем информацию о товаре из базы данных
    item = await Item.get(item_id)

    if call.from_user.username == item.username:
        await call.message.answer("<i>Вы не можете добавить отзыв самому себе.</i>", reply_markup=keyboards.menuKb)

    else:
        if not item:
            await call.message.answer("<i>Такого резюме не существует</i>", reply_markup=keyboards.menuKb)
            return
        else:
            await call.message.answer("<i>Напишите свой отзыв специалисту:</i>\nДля отмены нажмите /cancel")
        await NewReview.Review.set()
        await state.update_data(
            item=item,
                review=Reviews(
                    review_id=item_id
                )
        )

@dp.message_handler(commands=["cancel"], state=NewReview)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("<i>Добавление отзыва отменено.</i>", reply_markup=keyboards.menuKb)
    await state.reset_state()

@dp.message_handler(state=NewReview.Review)
async def enter_contact(message: types.Message, state: FSMContext):
    review_text = message.text
    async with state.proxy() as data:  # Работаем с данными из ФСМ
        data["review"].review_text = review_text

    data = await state.get_data()
    review: Reviews = data.get("review")
    review.from_us = message.from_user.username
    await review.create()
    await message.answer("<i>Ваш отзыв добавлен</i>", reply_markup=keyboards.menuKb)
    await state.reset_state()

@dp.message_handler(text='Эксперт')
async def message_text_handler(message: types.Message):
    all_experts = await db.show_experts()
    if not all_experts:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(all_experts):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Таргетолог')
async def message_text_handler(message: types.Message):
    targ = await db.targ()
    if not targ:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(targ):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Сторизмейкер')
async def message_text_handler(message: types.Message):
    storiz = await db.storiz()
    if not storiz:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(storiz):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='SMM-специалист')
async def message_text_handler(message: types.Message):
    smm = await db.smm()
    if not smm:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(smm):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Методолог')
async def message_text_handler(message: types.Message):
    metod = await db.metod()
    if not metod:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(metod):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Технический специалист')
async def message_text_handler(message: types.Message):
    tech = await db.tech()
    if not tech:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(tech):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Дизайнер')
async def message_text_handler(message: types.Message):
    dis = await db.dis()
    if not dis:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(dis):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Копирайтер')
async def message_text_handler(message: types.Message):
    copy = await db.copy()
    if not copy:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(copy):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Сценарист')
async def message_text_handler(message: types.Message):
    scen = await db.scen()
    if not scen:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(scen):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Монтажер видео')
async def message_text_handler(message: types.Message):
    mont = await db.mont()
    if not mont:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(mont):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Ассистент')
async def message_text_handler(message: types.Message):
    ass = await db.ass()
    if not ass:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(ass):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Специалист по визуалу')
async def message_text_handler(message: types.Message):
    vis = await db.vis()
    if not vis:
        await message.answer("<i>Специалистов не найдено</i>", reply_markup=keyboards.menuKb)
    else:
        for num, item in enumerate(vis):
            text = ("<b>Сфера деятельности: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")
            markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text=("Добавить отзыв"),
                                             callback_data=add_review_item.new(item_id=item.id)),
                        InlineKeyboardButton(text="Посмотреть отзывы", callback_data=see_review_item.new(item_id=item.id))
                    ],
                ]
            )
            sendBtn = InlineKeyboardButton(text="Написать специалисту", url=('t.me/{contact}').format(contact=item.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить резюме", callback_data=remove_item.new(item_id=item.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=item.id,
                name=item.name,
                desc=item.desc,
                username=item.username,
                contact=item.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Найти специалиста🔍')
async def message_text_handler(message: types.Message):
    text = 'Выбери какой специалист тебе требуется:'
    await bot.send_message(message.from_user.id, text, reply_markup=keyboards.change_spec)

@dp.message_handler(text='Опубликовать резюме🧾')
async def message_text_handler(message: types.Message):
    await bot.send_message(message.chat.id,
                           "Оплатите публикацию резюме", parse_mode='Markdown')
    await bot.send_invoice(message.chat.id, title='Публикация резюме',
                           description='После оплаты публикации, необходимо оформить резюме. Не переживай, я тебе во всем помогу!',
                           provider_token=pay_token,
                           currency='rub',
                           #need_email=True,
                           need_phone_number=True,
                           send_phone_number_to_provider=True,
                           #send_email_to_provider=True,
                           is_flexible=False,  # True If you need to set up Shipping Fee
                           prices=rezume,
                           #provider_data=True,
                           start_parameter='time-machine-example',
                           payload='HAPPY FRIDAYS COUPON')

@dp.message_handler(text='Опубликовать вакансию💼')
async def message_text_handler(message: types.Message):
    await bot.send_message(message.chat.id,
                           "Оплатите публикацию вакансии", parse_mode='Markdown')
    await bot.send_invoice(message.chat.id, title='Публикация вакансии',
                           description='После оплаты публикации, необходимо оформить резюме. Не переживай, я тебе во всем помогу!',
                           provider_token=pay_token,
                           currency='rub',
                           need_phone_number=True,
                           send_phone_number_to_provider=True,
                           is_flexible=False,  # True If you need to set up Shipping Fee
                           prices=vacancy,
                           start_parameter='time-machine-example',
                           payload='HAPPY FRIDAYS COUPON')

@dp.callback_query_handler(lambda call: call.data == 'see_vacancy')
async def callback_message(callback_query: types.CallbackQuery):
    all_vacancies = await db.show_vacancies()
    if not all_vacancies:
        await callback_query.message.answer("<i>Вакансий не найдено.</i>")
    else:
        for num, vacan in enumerate(all_vacancies):
            text = ("<b>Требуется: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")

            markup = InlineKeyboardMarkup()
            sendBtn = InlineKeyboardButton(text="Написать работодателю",
                                           url=('t.me/{contact}').format(contact=vacan.username))
            markup.add(sendBtn)
            if callback_query.message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить вакансию", callback_data=remove_vacan.new(item_id=vacan.id))
                markup.add(reviewBtn)

            await callback_query.message.answer(
                    text.format(
                item_id=vacan.id,
                name=vacan.name,
                desc=vacan.desc,
                username=vacan.username,
                contact=vacan.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.message_handler(text='Посмотреть вакансии')
async def message_text_handler(message: types.Message):
    all_vacancies = await db.show_vacancies()
    if not all_vacancies:
        await message.answer("<i>Вакансий не найдено.</i>")
    else:
        for num, vacan in enumerate(all_vacancies):
            text = ("<b>Требуется: </b>\t{name}\n"
                "<b>Описание: </b>{desc}\n"
                "<b>Instagram: </b>https://instagram.com/{contact}")

            markup = InlineKeyboardMarkup()
            sendBtn = InlineKeyboardButton(text="Написать работодателю",
                                           url=('t.me/{contact}').format(contact=vacan.username))
            markup.add(sendBtn)
            if message.from_user.id == 900230063 or 735318801:
                reviewBtn = InlineKeyboardButton("Удалить вакансию", callback_data=remove_vacan.new(item_id=vacan.id))
                markup.add(reviewBtn)

            await message.answer(
                    text.format(
                item_id=vacan.id,
                name=vacan.name,
                desc=vacan.desc,
                username=vacan.username,
                contact=vacan.contactInst), reply_markup=markup)
            await asyncio.sleep(0.3)

@dp.callback_query_handler(remove_vacan.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    vacan_id = int(callback_data.get("item_id"))
    await call.message.edit_reply_markup()

    # Достаем информацию о товаре из базы данных
    vacan = await Vacancy.get(vacan_id)
    #review = await Reviews.query.where(Reviews.review_id == item_id).gino.all()
    if not vacan:
        await call.message.answer("<i>Такой вакансии не существует</i>", reply_markup=keyboards.menuKb)
        return
    else:
        await Vacancy.delete.where(Reviews.review_id == vacan_id).gino.status()
        await vacan.delete()
    text = "<i>Вы удалили вакансию.</i>"
    await call.message.answer(text, reply_markup=keyboards.menuKb)

@dp.callback_query_handler(lambda call: call.data == 'add_rezume')
async def callback_message(callback_query: types.CallbackQuery):

    await bot.send_message(callback_query.message.chat.id,
                           "Оплатите публикацию резюме", parse_mode='Markdown')
    await bot.send_invoice(callback_query.message.chat.id, title='Публикация резюме',
                           description='После оплаты публикации, необходимо оформить резюме. Не переживай, я тебе во всем помогу!',
                           provider_token=pay_token,
                           currency='rub',
                           need_phone_number=True,
                           send_phone_number_to_provider=True,
                           is_flexible=False,  # True If you need to set up Shipping Fee
                           prices=rezume,
                           start_parameter='time-machine-example',
                           payload='HAPPY FRIDAYS COUPON')

@dp.callback_query_handler(lambda call: call.data == 'add_vacancy')
async def callback_message(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.message.chat.id,
                           "Опатите публикацию вакансии", parse_mode='Markdown')
    await bot.send_invoice(callback_query.message.chat.id, title='Публикация вакансии',
                           description='После оплаты публикации, необходимо оформить резюме. Не переживай, я тебе во всем помогу!',
                           provider_token=pay_token,
                           currency='rub',
                           need_phone_number=True,
                           send_phone_number_to_provider=True,
                           is_flexible=False,  # True If you need to set up Shipping Fee
                           prices=vacancy,
                           start_parameter='time-machine-example',
                           payload='HAPPY FRIDAYS COUPON')

@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message="Извините, платежи на данный момент не принимаются!")


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message):
    await bot.send_message(message.chat.id,
                           'Спасибо за оплату! Платеж `{} {}` успешно проведен!'
                           'Теперь давайте приступим к оформлению!'.format(
                               message.successful_payment.total_amount / 100, message.successful_payment.currency),
                           parse_mode='Markdown')
    if message.successful_payment.total_amount == 7000:
        await message.answer("<i>Выберите наименование сферы деятельности</i>", reply_markup=keyboards.change_spec)
        await NewItem.Name.set()
    if message.successful_payment.total_amount == 15000:
        await message.answer("<i>Какого специалиста Вы ищите?</i>", reply_markup=keyboards.change_spec)
        await NewVacancy.Name.set()


@dp.message_handler(commands=["cancel"], state=NewItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Вы отменили публикацию резюме.", reply_markup=keyboards.menuKb)
    await state.reset_state()

@dp.message_handler(state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name

    await message.answer(('<b>Сфера деятельности:</b> {name}'
        '\n\n<i>Отправьте мне описание:</i>').format(name=name))

    await NewItem.Desc.set()
    await state.update_data(item=item)

@dp.message_handler(state=NewItem.Desc)
async def enter_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    desc = message.text
    item.desc = desc
    await  message.answer(('<b>Сфера деятельности:</b> {name}'
                           '\n<b>Описание:</b> {desc}'
                           '\n\n<i>Отправьте мне свой никнейм (без@) в Instagram:</i>').format(name=item.name, desc=item.desc))
    await NewItem.Contact.set()
    await state.update_data(item=item)

@dp.message_handler(state=NewItem.Contact)
async def enter_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    contact = message.text
    item.contactInst = contact
    if not message.from_user.username:
        pass
    else:
        item.username = message.from_user.username
    #item.review_id = item.id
    await item.create()
    await item.update(review_id=item.id).apply()
    await item.update(payment=True).apply()
    await state.reset_state()

    await message.answer("<i>Ваше резюме удачно опубликовано.</i>", reply_markup=keyboards.menuKb)

@dp.message_handler(commands=["cancel"], state=NewVacancy)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Вы отменили публикацию вакансии", reply_markup=keyboards.menuKb)
    await state.reset_state()

@dp.message_handler(state=NewVacancy.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    vacan = Vacancy()
    vacan.name = name

    await message.answer(('<b>Требуется:</b> {name}'
        '\n\n<i>Отправьте мне описание вакансии:</i>').format(name=name))

    await NewVacancy.Desc.set()
    await state.update_data(vacan=vacan)

@dp.message_handler(state=NewVacancy.Desc)
async def enter_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    vacan: Vacancy = data.get("vacan")
    desc = message.text
    vacan.desc = desc
    await  message.answer(('<b>Требуется:</b> {name}'
                           '\n<b>Описание:</b> {desc}'
                           '\n\n<i>Отправьте мне свой никнейм (без@) в Instagram:</i>').format(name=vacan.name, desc=vacan.desc))
    await NewVacancy.Contact.set()
    await state.update_data(vacan=vacan)

@dp.message_handler(state=NewVacancy.Contact)
async def enter_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    vacan: Vacancy = data.get("vacan")
    contact = message.text
    vacan.contactInst = contact
    if not message.from_user.username:
        pass
    else:
        vacan.username = message.from_user.username
    #item.review_id = item.id
    await vacan.create()
    await vacan.update(payment=True).apply()
    await state.reset_state()

    await message.answer("<i>Ваша вакансия удачно опубликована.</i>", reply_markup=keyboards.menuKb)

# Фича для рассылки по юзерам (учитывая их язык)
@dp.message_handler(user_id=[900230063, 735318801], commands=["tell_everyone"])
async def mailing(message: types.Message):
    await message.answer("<i>Пришлите текст рассылки</i>")
    await Mailing.Text.set()


@dp.message_handler(user_id=[900230063, 735318801], state=Mailing.Text)
async def mailing(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Отправить", callback_data="send")],
            [InlineKeyboardButton(text="Редактировать", callback_data="edit")],
        ]
    )
    await message.answer(("<i>Отправляем?</i>\n\n"
                           "Текст:\n"
                           "{text}").format(text=text),
                         reply_markup=markup)
    await Mailing.Confirm.set()


@dp.callback_query_handler(user_id=[900230063, 735318801], state=Mailing.Confirm)
async def mailing_start(call: types.CallbackQuery, state: FSMContext):
    if call.data == "send":
        data = await state.get_data()
        text = data.get("text")

        await state.reset_state()
        await call.message.edit_reply_markup()

        users = await User.query.gino.all()
        for user in users:
            try:
                await bot.send_message(chat_id=user.user_id,
                                       text=text)
                await sleep(0.3)
            except Exception:
                pass
        await call.message.answer("<i>Рассылка выполнена.</i>", reply_markup=keyboards.menuKb)
    if call.data == "edit":
        await call.message.answer("<i>Введите текст рассылки еще раз.</i>")
        await Mailing.Text.set()
