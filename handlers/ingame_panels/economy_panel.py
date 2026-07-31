from services.bot import bot
from services.constants import get_player, get_date_move, get_modifier, get_country
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from services.math.economy_math import (get_tax_income, get_buildings_income, get_prod_units,
                                        get_prod_units_consumption, get_total_spending, get_total_income)
from services.math.army_math import get_prod_units_debuff

ECOMOMY_KB = InlineKeyboardMarkup(row_width=3)
ECOMOMY_KB.add(InlineKeyboardButton("Доходы", callback_data = "economy:income:open"), InlineKeyboardButton("Расходы", callback_data = "spending:base:open"),
               InlineKeyboardButton("Долги", callback_data = "economy:loan:open"), InlineKeyboardButton("Назад", callback_data = "state:open"))
INCOME_KB = InlineKeyboardMarkup(row_width=2)
INCOME_KB.add(InlineKeyboardButton("Повысить налоги", callback_data= "economy:income:rise:open"), InlineKeyboardButton("Снизить налоги", callback_data= "economy:income:down:open"),
              InlineKeyboardButton("Вернуться", callback_data="economy:base:open"))
LOAN_KB = InlineKeyboardMarkup(row_width=2)
LOAN_KB.add(InlineKeyboardButton("Взять долг", callback_data="economy:loan:take:open"), InlineKeyboardButton("Вернуть долг", callback_data="economy:loan:repay:open"),
            InlineKeyboardButton("Вернуться", callback_data="economy:base:open"))


# Базовая панель экономики.
def open_economy_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)
    prod_units = get_prod_units(player, 0)
    prod_units_cons = get_prod_units_consumption(player_country)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Казна: {player_country['money']:.2f} монет"
            "\n\n"
            f"Доходы: {get_total_income(player, player_country):.2f} монет в ход\n"
            f"Расходы: {get_total_spending(player, player_country):.2f} монет в ход \n"
            f"Баланс: {get_total_income(player, player_country) - get_total_spending(player, player_country):.2f} монет в ход"
            "\n\n"
            f"Единиц производства: {prod_units} шт.\n"
            f"Потребление армией ед. производства: {prod_units_cons} шт.\n"
            f"Баланс производства: {prod_units - prod_units_cons} шт.\n"
            f"Штраф/Бонус к армии: {get_prod_units_debuff(player, player_country) * 100:.2f}%")

    bot.edit_message_text(
        text,
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = ECOMOMY_KB
    )

# Панель подробных доходов (также можно менять налоги).
def open_income_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)
    tax_income = get_tax_income(player, player_country)
    prod_income = get_buildings_income(player, player_country)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Налоги: {tax_income:.2f} монет в ход\n"
            f"От зданий: {prod_income:.2f} монет в ход\n"
            f"Общий доход: {get_total_income(player,player_country):.2f}"
            f"\n\n"
            f"Налоговая ставка: {get_modifier(player_country, 'tax_rate')*100:.2f}%")
    bot.edit_message_text(
        text,
        chat_id= chat_id,
        message_id= message_id,
        reply_markup=INCOME_KB
    )

# Панель займов.
def open_loan_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Взято в заём: {player_country['loans']} монет\n"
            f"Процентная ставка: {player_country['interest']*100:.2f}% в год"
            "\n\n"
            f"Ежемесячные расходы на погашение займов: {player_country['loans']*player_country['interest']/12:.2f}")
    bot.edit_message_text(
        text,
        chat_id= chat_id,
        message_id= message_id,
        reply_markup=LOAN_KB
    )
