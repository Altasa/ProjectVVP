from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ContextTypes, ConversationHandler
from proreceip import findreceip
from random import randint
from time import sleep
from telegram import InputMediaPhoto
# Содержит словари названий и адресов рецептов
import proreceip
# Создать базу данных по открытым рецептам пользователей
chatids={}

# Возвращаемые значения асинхронных функций, которые передаются в ConversationHandler.
CHOOSING_CATEGORY, CATEGORY, COOKING = range(0, 3)

# Названия категорий и подкатегорий.
from gen_buttons import buttons

# Функция создаёт встроенную клавиатуру с категориями и подкатегориями.
def category_markups(category: str = "default") -> InlineKeyboardMarkup:
    # Сокращаем код. Подфункция создаёт массив с кнопками...
    def algorithm(index: int) -> list:
        category_keyboard = []
        # Если количество кнопок чётное:
        if len(buttons[index]) % 2 == 0:
                for i in range(0, len(buttons[index]), 2):
                    category_keyboard.append([InlineKeyboardButton(buttons[index][i], callback_data = buttons[index][i]),
                                InlineKeyboardButton(buttons[index][i+1], callback_data = buttons[index][i+1])])
                # Если НЕ главное меню (с категориями), добавить кнопку "Главная", т.е. возврат к списку категорий.
                if index != 0:
                    category_keyboard.append([InlineKeyboardButton("Главная", callback_data="Main")])
                return category_keyboard
        # Если количество кнопок нечётное:
        else:
            for i in range(0, len(buttons[index])-1, 2):
                category_keyboard.append([InlineKeyboardButton(buttons[index][i], callback_data = buttons[index][i]),
                            InlineKeyboardButton(buttons[index][i+1], callback_data = buttons[index][i+1])])
            category_keyboard.append([InlineKeyboardButton(buttons[index][len(buttons[index])-1], callback_data = buttons[index][len(buttons[index])-1])])
            if index != 0:
                category_keyboard.append([InlineKeyboardButton("Главная", callback_data="Main")])
            return category_keyboard
    keyboard = list()
    # ...в зависимости от переданного значения в основную функцию, вызывается соответствующая подфункция.
    match category:
        case "default":
            keyboard = algorithm(0)
        case "Бульоны и супы":
            keyboard = algorithm(1)
        case "Горячие блюда":
            keyboard = algorithm(2)
        case "Вторые блюда":
            keyboard = algorithm(3)
        case "Салаты":
            keyboard = algorithm(4)
        case "Консервы":
            keyboard = algorithm(5)
        case "Закуски":
            keyboard = algorithm(6)
        case "Соусы":
            keyboard = algorithm(7)
        case "Выпечка":
            keyboard = algorithm(8)
        case "Десерты":
            keyboard = algorithm(9)
        case "Напитки":
            keyboard = algorithm(10)
        case "Каши":
            keyboard = algorithm(11)
        case "Украшения":
            keyboard = algorithm(12)
        case "В пароварке":
            keyboard = algorithm(13)
        case "Молочные продукты":
            keyboard = algorithm(14)
        case "Маринад, панировка":
            keyboard = algorithm(15)
    # Возвращает объект 'InlineKeyboardMarkup', который является самой встроенной клавиатурой.
    category_markup = InlineKeyboardMarkup(keyboard)
    return category_markup

# Аналогично встроенные клавиатуры для страниц с рецептами в подкатегории.
def subcategory_markups(subcategory: str) -> list:
    subcategory_keyboards = []
    for i in range(len(proreceip.subcategories[subcategory])):
        subcategory_keyboard = []
        for j in range(0,len(proreceip.subcategories[subcategory][i])):
            subcategory_keyboard.append([InlineKeyboardButton(proreceip.subcategories[subcategory][i][j],
                                                    callback_data=f"start.{subcategory}.{i}.{j}")])
        if len(proreceip.subcategories[subcategory]) == 1:
            subcategory_keyboard.append([InlineKeyboardButton("Главная", callback_data="Main")])
        elif i == 0:
            subcategory_keyboard.append([InlineKeyboardButton("Главная", callback_data="Main"),
                                                    InlineKeyboardButton("-->", callback_data="Next")])
        elif i == len(proreceip.subcategories[subcategory]) - 1:
            subcategory_keyboard.append([InlineKeyboardButton("<--", callback_data="Prev"),
                                                    InlineKeyboardButton("Главная", callback_data="Main")])
        else:
            subcategory_keyboard.append([InlineKeyboardButton("<--", callback_data="Prev"),
                                                    InlineKeyboardButton("Главная", callback_data="Main"),
                                                    InlineKeyboardButton("-->", callback_data="Next")])
        subcategory_keyboards.append(subcategory_keyboard)
    subcategory_markups = []
    for i in range(len(subcategory_keyboards)):
        subcategory_markups.append(InlineKeyboardMarkup(subcategory_keyboards[i]))
    return subcategory_markups

# Создаёт кнопки для самого рецепта. Без этой функции не получится посмотреть ингредиенты и шаги приготовления.
def recipe_markups(flag: str, step: int = None, length: int = None) -> list:
    keyboard = []
    match flag:
        case "start" | "start_random":
            keyboard.append([InlineKeyboardButton("Посмотреть ингредиенты", callback_data = "ingredient")])
            markup = InlineKeyboardMarkup(keyboard)
            return markup
        case "ingredient" | "step":
            keyboard.append([InlineKeyboardButton(f"Перейти к шагу {step} из {length}", callback_data = "step")])
            markup = InlineKeyboardMarkup(keyboard)
            return markup

# Функция входа в диалог. Выдаёт перечень категорий.
async def default(update, _):
    await update.message.reply_text("Выберите категорию", reply_markup = category_markups())
    return CHOOSING_CATEGORY

# Информирует о выбранной категории и выдаёт клавиатуру с подкатегориями.
async def choice(update, _):
    query = update.callback_query
    variant = query.data
    await query.answer()
    await query.edit_message_text(text = f"Вы выбрали категорию «{variant}».\nВыберите подкатегорию:",
                                    reply_markup = category_markups(variant))
    return CATEGORY

# Временные переменные для рецепта.
active_subcategory = list()
active_page = 0
active_variant = ""
cooking_flag = ""
current_step = 1
ingredient_triggered = False
data = dict()

# Подсказки для пользователя.
FINAL_MESSAGE = "\n\nНа этом всё... Приятного аппетита!"
HINT = "\n\n💡 Подсказка: Используйте /stop чтобы прекратить выполнение рецепта"
HINT_END = "💡 Подсказка: Используйте /begin для открытия каталога рецептов"

# Вызывается после выбора рецепта или по нажатии кнопки "Случайный рецепт" в списке категорий.
async def cooking(update, context):
    query = update.callback_query
    recipe = query.data.split('.')
    await query.answer()
    # "Импорт" временных переменных.
    global active_page, active_subcategory, active_variant
    global cooking_flag, current_step, ingredient_triggered, data
    # Ставим флаг в зависимости от того, выбран рецепт случайно или вручную.
    if recipe[0] == "Случайный рецепт":
        cooking_flag = "start_random"
    else:
        cooking_flag = recipe[0]
    match cooking_flag:
        # Если кнопкой вернулось это значение, сбросить временные переменные и вернуться к списку категорий.
        case "Main":
            active_subcategory.clear()
            active_variant = ""
            cooking_flag = ""
            current_step = 1
            active_page = 0
            ingredient_triggered = False
            data.clear()
            await query.edit_message_text(text = "Выберите категорию:", reply_markup = category_markups())
            return CHOOSING_CATEGORY
        # Открывает предыдущую страницу рецептов.
        case "Prev":
            active_page -= 1
            recipes = f"Рецепты в подкатегории «{active_variant}»\n\nСтраница {active_page+1} из {len(active_subcategory)}"
            await query.edit_message_text(text = recipes, reply_markup = active_subcategory[active_page])
            return COOKING
        # Открывает следующую страницу рецептов.
        case "Next":
            active_page += 1
            recipes = f"Рецепты в подкатегории «{active_variant}»\n\nСтраница {active_page+1} из {len(active_subcategory)}"
            await query.edit_message_text(text = recipes, reply_markup = active_subcategory[active_page])
            return COOKING
        # Срабатывает при выборе рецепта.
        case "start":
            await context.bot.send_chat_action(chat_id = update.effective_chat.id, action = constants.ChatAction.UPLOAD_PHOTO)
            rm = recipe_markups(cooking_flag)
            # Импортирует URL рецепта из словаря 'urlreceip'. Аргументы: подкатегория, страница рецепта, номер рецепта на странице.
            receip = proreceip.urlreceip[recipe[1]][int(recipe[2])][int(recipe[3])]
            # Скачать рецепт с сайта
            try:
                data = findreceip(receip)
            except:
                context.bot.send_message(chat_id = update.effective_chat.id, message = "Что-то пошло не так. Попробуйте ещё раз или свяжитесь с администратором бота.")
                return CHOOSING_CATEGORY
            # Сохранить открытый рецепт в базу данных
            chatids[update.effective_chat.id]=data
            # Создать сообщение с описанием рецепта
            title       = chatids[update.effective_chat.id]['title'].split(': ')
            description = chatids[update.effective_chat.id]['description']
            source      = chatids[update.effective_chat.id]['resource']
            message = "Описание:\n" + description + "\n\nИсточник: " + source
            # Вывод в консоль названия выбранных рецепта и подкатегории (для отладки).
            print(title[0] + ": " + title[1] + ". Подкатегория: " + recipe[1])
            # Вывод пользователю картинки готового блюда, названия и краткого описания, а также ссылки на сайт.
            if chatids[update.effective_chat.id]['image'] is not None:
                await context.bot.send_photo(chat_id = update.effective_chat.id,
                                             photo = chatids[update.effective_chat.id]['image'],
                                             caption = title[1])
            else:
                message=title[1]+"\n\n"+message   
            await context.bot.send_message( chat_id = update.effective_chat.id,
                                            text = message,
                                            reply_markup = rm)
            return COOKING
        # Срабатывает при нажатии "Случайный рецепт"
        case "start_random":
            await context.bot.send_chat_action(chat_id = update.effective_chat.id, action = constants.ChatAction.UPLOAD_PHOTO)
            rm = recipe_markups(cooking_flag)
            # Аналогично 'start', только значения подбираются рандомно.
            subcat = proreceip.keys[randint(0, len(proreceip.subcategories)-1)]
            recpage = randint(0, len(proreceip.subcategories[subcat])-1)
            recnumber = randint(0, len(proreceip.subcategories[subcat][recpage])-1)
            receip = proreceip.urlreceip[subcat][recpage][recnumber]
            # Скачать рецепт с сайта
            try:
                data = findreceip(receip)
            except:
                context.bot.send_message(chat_id = update.effective_chat.id, message = "Что-то пошло не так. Попробуйте ещё раз или свяжитесь с администратором бота.")
                return CHOOSING_CATEGORY
            # Сохранить открытый рецепт в базу данных
            chatids[update.effective_chat.id]=data
            # Создать сообщение с описанием рецепта
            title       = chatids[update.effective_chat.id]['title'].split(': ')
            description = chatids[update.effective_chat.id]['description']
            source      = chatids[update.effective_chat.id]['resource']
            message = "Описание:\n" + description + "\n\nИсточник: " + source
            # Вывод в консоль названия выбранных рецепта и подкатегории (для отладки).
            print(title[0] + ": " + title[1] + ". Подкатегория: " + subcat)
            if chatids[update.effective_chat.id]['image'] is not None:
                await context.bot.send_photo(chat_id = update.effective_chat.id,
                                             photo = chatids[update.effective_chat.id]['image'],
                                             caption = title[1])
            else:
                message=title[1]+"\n\n"+message   
            await context.bot.send_message( chat_id = update.effective_chat.id,
                                            text = message,
                                            reply_markup = rm)
            return COOKING
        # Выводит пользователю список ингредиентов. Блокирует повторное нажатие кнопки "Посмотреть ингредиенты".
        case "ingredient":
            if ingredient_triggered is False:
                await context.bot.send_chat_action(chat_id = update.effective_chat.id, action = constants.ChatAction.TYPING)
                rm = recipe_markups(cooking_flag, chatids[update.effective_chat.id]['current_step'], len(chatids[update.effective_chat.id]) - 6)
                # Получить ингредиенты из базы данных по id чата
                ingredients = chatids[update.effective_chat.id]['ingredients'].split("\n")
                # Создать сообщение с ингредиентами
                message = "Ингредиенты:\n"
                for i in range(len(ingredients)):
                    message += f"{i+1}. " + ingredients[i] + "\n"
                message += HINT
                await context.bot.send_message(chat_id = update.effective_chat.id,
                                                text = message,
                                                reply_markup = rm)
                # Блокировка повторного нажатия на ингредиенты 
                # В текущем режиме влияет на работу кнопки у всех пользователей
                # Нужно просто удалять эту кнопку, чтобы не было вопроса к интерфейсу
                # ingredient_triggered = True
                return COOKING
            return COOKING
        # Выводит пользователю шаги выполнения по одному.
        case "step":
            # Загрузка из базы данных номера текущего шага этого пользователя
            current_step_local = chatids[update.effective_chat.id]['current_step']
            # Сброс переменных на последнем шаге и завершение диалога.
            if current_step_local == len(chatids[update.effective_chat.id]) - 6:
                #Отправка последнего шага
                step_images = chatids[update.effective_chat.id][f"step{current_step_local}"][0]
                step_text = chatids[update.effective_chat.id][f"step{current_step_local}"][1] + FINAL_MESSAGE
                #Разбор количества фотографий в рецепте
                if len(step_images)==1 and step_images[0]!=None:
                    await context.bot.send_chat_action(chat_id = update.effective_chat.id, action = constants.ChatAction.UPLOAD_PHOTO)
                    await context.bot.send_photo(chat_id = update.effective_chat.id,
                                                    photo = step_images[0])
                elif len(step_images)>1:
                    await context.bot.send_chat_action(chat_id = update.effective_chat.id, action = constants.ChatAction.UPLOAD_PHOTO)
                    images_to_send=[]
                    for img in step_images:
                        images_to_send.append(InputMediaPhoto(media = img))
                    await context.bot.send_media_group(chat_id = update.effective_chat.id,
                                                        media=images_to_send)
                #Отправка текста шага + заверение диалога
                await context.bot.send_chat_action(chat_id = update.effective_chat.id, action = constants.ChatAction.TYPING)
                step_text = f"Шаг {current_step_local}\n\n" + step_text
                await context.bot.send_message(chat_id = update.effective_chat.id,
                                                text = step_text)
                sleep(0.5)
                await context.bot.send_message(chat_id = update.effective_chat.id,
                                                text = HINT_END)
                active_subcategory.clear()
                active_variant = ""
                cooking_flag = ""
                current_step = 1
                active_page = 0
                ingredient_triggered = False
                return ConversationHandler.END
            else:
                rm = recipe_markups(cooking_flag, current_step_local+1, len(chatids[update.effective_chat.id]) - 6)
                # Получает шаги по id чата
                step_images = chatids[update.effective_chat.id][f"step{current_step_local}"][0]
                step_text = chatids[update.effective_chat.id][f"step{current_step_local}"][1]
                #Разбор количества фотографий в рецепте
                #Одно фото
                if len(step_images)==1 and step_images[0]!=None:
                    await context.bot.send_chat_action(chat_id = update.effective_chat.id, action = constants.ChatAction.UPLOAD_PHOTO)
                    await context.bot.send_photo(chat_id = update.effective_chat.id,
                                                        photo = step_images[0])
                #Несколько фото
                elif len(step_images)>1:
                    await context.bot.send_chat_action(chat_id = update.effective_chat.id, action = constants.ChatAction.UPLOAD_PHOTO)
                    images_to_send=[]
                    for img in step_images:
                        images_to_send.append(InputMediaPhoto(media = img))
                    await context.bot.send_media_group(chat_id = update.effective_chat.id,
                                                        media=images_to_send)
                await context.bot.send_chat_action(chat_id = update.effective_chat.id, action = constants.ChatAction.TYPING)
                #Отправка текста шага + кнопки следующего шага
                step_text = f"Шаг {current_step_local}\n\n" + step_text
                await context.bot.send_message(chat_id = update.effective_chat.id,
                                                text = step_text,
                                                reply_markup = rm)
                # Увеличить счетчик и записать в базу данных
                chatids[update.effective_chat.id]['current_step'] += 1
                return COOKING

# Выводит список подкатегорий. Игнорируется, если было выбрано "Случайный рецепт".
async def category(update, _) -> int:
    query = update.callback_query
    variant = query.data
    await query.answer()
    global active_page, active_subcategory, active_variant
    match variant:
        case "Main":
            await query.edit_message_text(text = "Выберите категорию:", reply_markup = category_markups())
            return CHOOSING_CATEGORY
        case _:
            active_variant = variant
            active_subcategory = subcategory_markups(active_variant)
            message = f"Рецепты в подкатегории «{active_variant}»\n\nСтраница {active_page+1} из {len(active_subcategory)}"
            await query.edit_message_text(text = message, reply_markup = active_subcategory[active_page])
            return COOKING

# Принудительное завершение диалога и сброс временных переменных.
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global active_page, active_subcategory, active_variant
    global cooking_flag, current_step, ingredient_triggered
    active_subcategory.clear()
    active_variant = ""
    cooking_flag = ""
    current_step = 1
    active_page = 0
    ingredient_triggered = False
    data.clear()
    message = "✅ Выполнение рецепта прервано\n\n" + HINT_END
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return ConversationHandler.END
