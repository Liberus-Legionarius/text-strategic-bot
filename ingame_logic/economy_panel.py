from bot import db, bot
from constants import NUMBER_TO_MONTH, BASE_INCOME
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

ECOMOMY_KB = InlineKeyboardMarkup()
ECOMOMY_KB.add(InlineKeyboardButton("Доходы", callback_data = "economy:income:open"), InlineKeyboardButton("Расходы", callback_data = "economy:spending:open"),
               InlineKeyboardButton("Долги", callback_data = "economy:loan:open"), InlineKeyboardButton("Производство", callback_data = "economy:prod_units:open"),
               InlineKeyboardButton("Стройка", callback_data= "economy:build:open"), InlineKeyboardButton("Назад", callback_data = "state:open"))
INCOME_KB = InlineKeyboardMarkup()
INCOME_KB.add(InlineKeyboardButton("Повысить налоги", callback_data= "economy:income:rise:open"), InlineKeyboardButton("Снизить налоги", callback_data= "economy:income:down:open"),
              InlineKeyboardButton("Вернуться", callback_data="economy:base:open"))
LOAN_KB = InlineKeyboardMarkup()
LOAN_KB.add(InlineKeyboardButton("Взять долг", callback_data="economy:loan:take:open"), InlineKeyboardButton("Вернуть долг", callback_data="economy:loan:repay:open"),
            InlineKeyboardButton("Вернуться", callback_data="economy:base:open"))

# Базовая панель экономики.
def open_economy_panel(user, chat_id, message_id):
    player = db.players.find_one({"tg_id":user.id})
    prod_units = 0
    income = BASE_INCOME
    for city in player["cities"]:
        income += city["population"] * player["taxes"] / 120
        for building in city["buildings"]:
            income += building["income_per_pop"] * city["population"]
            if building.get("prod_unit_inc"): prod_units += building["prod_unit_inc"]
    spending = player['loans']*player['interest']/12

    text = (f"{NUMBER_TO_MONTH[player['date'].month]}, год {player['date'].year}, шаг {player['step']}"
            "\n\n"
            f"Казна: {player['money']:.2f} монет"
            "\n\n"
            f"Доходы: {income:.2f} монет в ход\n"
            f"Расходы: {spending:.2f} монет в ход \n"
            f"Баланс: {income - spending:.2f} монет в ход"
            "\n\n"
            f"Единиц производства: {prod_units}")

    bot.edit_message_text(
        text,
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = ECOMOMY_KB
    )

# Панель подробных доходов (также можно менять налоги)
def open_income_panel(user, chat_id, message_id):
    player = db.players.find_one({"tg_id": user.id})
    tax_income = 0
    prod_income = 0
    for city in player["cities"]:
        tax_income += city["population"] * player["taxes"] / 120
        for building in city["buildings"]:
            prod_income += building["income_per_pop"] * city["population"]

    text = (f"{NUMBER_TO_MONTH[player['date'].month]}, год {player['date'].year}, шаг {player['step']}"
            "\n\n"
            f"Базовый доход: {BASE_INCOME} монет в ход\n"
            f"Налоги: {tax_income:.2f} монет в ход\n"
            f"От зданий: {prod_income:.2f} монет в ход\n"
            f"\n\n"
            f"Налоговая ставка: {player['taxes']*100:.2f}%")
    bot.edit_message_text(
        text,
        chat_id= chat_id,
        message_id= message_id,
        reply_markup=INCOME_KB
    )

# Панель подробных расходов
def open_spending_panel(user, message):
    pass

# Панель займов
def open_loan_panel(user, chat_id, message_id):
    player = db.players.find_one({"tg_id": user.id})
    text = (f"{NUMBER_TO_MONTH[player['date'].month]}, год {player['date'].year}, шаг {player['step']}"
            "\n\n"
            f"Взято в заём: {player['loans']} монет\n"
            f"Процентная ставка: {player['interest']*100:.2f}% в год"
            "\n\n"
            f"Ежемесячные расходы на погашение займов: {player['loans']*player['interest']/12:.2f}")
    bot.edit_message_text(
        text,
        chat_id= chat_id,
        message_id= message_id,
        reply_markup=LOAN_KB
    )