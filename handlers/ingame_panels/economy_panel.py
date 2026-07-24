from services.bot import bot
from services.constants import BASE_INCOME, get_player, get_date_move
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from services.math.economy_math import get_tax_income, get_buildings_income, get_prod_units, get_loan_spending, \
    get_pops_invest_spending, get_army_spending

ECOMOMY_KB = InlineKeyboardMarkup()
ECOMOMY_KB.add(InlineKeyboardButton("Доходы", callback_data = "economy:income:open"), InlineKeyboardButton("Расходы", callback_data = "economy:spending:open"),
               InlineKeyboardButton("Долги", callback_data = "economy:loan:open"), InlineKeyboardButton("Назад", callback_data = "state:open"))
INCOME_KB = InlineKeyboardMarkup()
INCOME_KB.add(InlineKeyboardButton("Повысить налоги", callback_data= "economy:income:rise:open"), InlineKeyboardButton("Снизить налоги", callback_data= "economy:income:down:open"),
              InlineKeyboardButton("Вернуться", callback_data="economy:base:open"))
LOAN_KB = InlineKeyboardMarkup()
LOAN_KB.add(InlineKeyboardButton("Взять долг", callback_data="economy:loan:take:open"), InlineKeyboardButton("Вернуть долг", callback_data="economy:loan:repay:open"),
            InlineKeyboardButton("Вернуться", callback_data="economy:base:open"))

# Базовая панель экономики.
def open_economy_panel(user, chat_id, message_id):
    player = get_player(user)
    prod_units = get_prod_units(player)
    income = BASE_INCOME + get_tax_income(player) + get_buildings_income(player)
    spending = get_loan_spending(player) + get_pops_invest_spending(player) + get_army_spending(player)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Казна: {player['money']:.2f} монет"
            "\n\n"
            f"Доходы: {income:.2f} монет в ход\n"
            f"Расходы: {spending:.2f} монет в ход \n"
            f"Баланс: {income - spending:.2f} монет в ход"
            "\n\n"
            f"Единиц производства: {prod_units} шт.\n"
            f"Потребление армией ед. производства: 0 шт.\n"
            f"Баланс производства: {prod_units} шт.\n"
            f"Штраф/Бонус к армии: ?")

    bot.edit_message_text(
        text,
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = ECOMOMY_KB
    )

# Панель подробных доходов (также можно менять налоги).
def open_income_panel(user, chat_id, message_id):
    player = get_player(user)
    tax_income = get_tax_income(player)
    prod_income = get_buildings_income(player)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Базовый доход: {BASE_INCOME} монет в ход\n"
            f"Налоги: {tax_income:.2f} монет в ход\n"
            f"От зданий: {prod_income:.2f} монет в ход\n"
            f"Общий доход: {tax_income + prod_income + BASE_INCOME:.2f}"
            f"\n\n"
            f"Налоговая ставка: {player['taxes']*100:.2f}%")
    bot.edit_message_text(
        text,
        chat_id= chat_id,
        message_id= message_id,
        reply_markup=INCOME_KB
    )

# Панель подробных расходов.
def open_spending_panel(user, message):
    pass

# Панель займов.
def open_loan_panel(user, chat_id, message_id):
    player = get_player(user)
    text = (f"{get_date_move(player)}"
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