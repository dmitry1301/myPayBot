from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup,KeyboardButton

main_kb = InlineKeyboardMarkup()
find_specBtn = InlineKeyboardButton('Найти специалиста🔍', callback_data='find_spec')
add_rezumeBtn = InlineKeyboardButton('Опубликовать резюме🧾', callback_data='add_rezume')
add_vacancyBtn = InlineKeyboardButton('Опубликовать вакансию💼', callback_data='add_vacancy')
see_vacancyBtn = InlineKeyboardButton('Посмотреть вакансии', callback_data='see_vacancy')
main_kb.add(find_specBtn)
main_kb.add(see_vacancyBtn)
main_kb.add(add_rezumeBtn)
main_kb.add(add_vacancyBtn)

change_spec = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
producerBtn = KeyboardButton('Продюсер')
expertBtn = KeyboardButton('Эксперт', callback_data='expert')
targetBtn = KeyboardButton('Таргетолог', callback_data='target')
storiesBtn = KeyboardButton('Сторизмейкер', callback_data='stories')
smmBtn = KeyboardButton('SMM-специалист', callback_data='smm')
metodologBtn = KeyboardButton('Методолог', callback_data='metodolog')
techBtn = KeyboardButton('Технический специалист', callback_data='tech')
designBtn = KeyboardButton('Дизайнер', callback_data='design')
copyrightBtn = KeyboardButton('Копирайтер', callback_data='copyright')
montBtn = KeyboardButton('Монтажер видео', callback_data='mont')
scenarBtn = KeyboardButton('Сценарист', callback_data='scenar')
assistBtn = KeyboardButton('Ассистент', callback_data='assist')
visualBtn = KeyboardButton('Специалист по визуалу', callback_data='visual')
change_spec.add(producerBtn,expertBtn, targetBtn)
change_spec.add(storiesBtn, smmBtn)
change_spec.add(metodologBtn,techBtn)
change_spec.add(designBtn, copyrightBtn, scenarBtn)
change_spec.add(montBtn, assistBtn)
change_spec.add(visualBtn)

menuKb = ReplyKeyboardMarkup(resize_keyboard=True)
vacanBtn = KeyboardButton('Посмотреть вакансии')
findBtn = KeyboardButton('Найти специалиста🔍')
add_rezBtn = KeyboardButton('Опубликовать резюме🧾')
add_vacanBtn = KeyboardButton('Опубликовать вакансию💼')
my_pubBtn = KeyboardButton('Мои публикации')
menuKb.add(vacanBtn, findBtn)
menuKb.add(add_rezBtn)
menuKb.add(add_vacanBtn)
menuKb.add(my_pubBtn)