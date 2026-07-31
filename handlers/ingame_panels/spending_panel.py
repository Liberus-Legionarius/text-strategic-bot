from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from services.bot import bot
from services.constants import get_player, get_date_move, get_country
from services.math.army_math import get_total_army
from services.math.economy_math import get_total_spending, get_loan_spending
from services.math.spending_math import *
from services.math.territory_math import get_total_population, get_next_step_growth, get_percent_pop_growth

SPENDING_KB = InlineKeyboardMarkup(row_width = 3)
SPENDING_KB.add(InlineKeyboardButton("Население", callback_data="spending:pops:open"),
                InlineKeyboardButton("Армия", callback_data="spending:army:open"),
                InlineKeyboardButton("Дипломатия", callback_data="spending:diplomacy:open"),
                InlineKeyboardButton("Стабильность", callback_data="spending:stability:open"),
                InlineKeyboardButton("Милитаризация", callback_data="spending:militarization:open"))
SPENDING_KB.row(InlineKeyboardButton("Вернуться", callback_data = "economy:base:open"))
POPS_KB = InlineKeyboardMarkup(row_width=3)
POPS_KB.add(InlineKeyboardButton("-5%", callback_data = "spending:pops:-0.05"), InlineKeyboardButton("-2%", callback_data = "spending:pops:-0.02"),
            InlineKeyboardButton("-1%", callback_data = "spending:pops:-0.01"),InlineKeyboardButton("1%", callback_data = "spending:pops:0.01"),
            InlineKeyboardButton("2%", callback_data = "spending:pops:0.02"),InlineKeyboardButton("5%", callback_data = "spending:pops:0.05"),
            InlineKeyboardButton("Вернуться", callback_data="spending:base:open"))
ARMY_KB = InlineKeyboardMarkup(row_width=3)
ARMY_KB.add(InlineKeyboardButton("-25%", callback_data = "spending:army:-0.25"), InlineKeyboardButton("-10%", callback_data = "spending:army:-0.1"),
            InlineKeyboardButton("-5%", callback_data = "spending:army:-0.05"),InlineKeyboardButton("5%", callback_data = "spending:army:0.05"),
            InlineKeyboardButton("10%", callback_data = "spending:army:0.1"),InlineKeyboardButton("25%", callback_data = "spending:army:0.25"),
            InlineKeyboardButton("Вернуться", callback_data="spending:base:open"))
STABILITY_KB = InlineKeyboardMarkup(row_width=3)
STABILITY_KB.add(InlineKeyboardButton("-0.5%", callback_data = "spending:stability:-0.005"), InlineKeyboardButton("-0.2%", callback_data = "spending:stability:-0.002"),
            InlineKeyboardButton("-0.1%", callback_data = "spending:stability:-0.001"),InlineKeyboardButton("0.1%", callback_data = "spending:stability:0.001"),
            InlineKeyboardButton("0.2%", callback_data = "spending:stability:0.002"),InlineKeyboardButton("0.5%", callback_data = "spending:stability:0.005"),
            InlineKeyboardButton("Вернуться", callback_data="spending:base:open"))
MILITARIZATION_KB = InlineKeyboardMarkup(row_width=3)
MILITARIZATION_KB.add(InlineKeyboardButton("-0.5%", callback_data = "spending:militarization:-0.005"), InlineKeyboardButton("-0.2%", callback_data = "spending:militarization:-0.002"),
            InlineKeyboardButton("-0.1%", callback_data = "spending:militarization:-0.001"),InlineKeyboardButton("0.1%", callback_data = "spending:militarization:0.001"),
            InlineKeyboardButton("0.2%", callback_data = "spending:militarization:0.002"),InlineKeyboardButton("0.5%", callback_data = "spending:militarization:0.005"),
            InlineKeyboardButton("Вернуться", callback_data="spending:base:open"))

# Панель подробных расходов.
def open_spending_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Вложения в рост населения: {get_pops_invest_spending(player, player_country):.2f}\n"
            f"Расходы на армию: {get_army_spending(player_country):.2f}\n"
            f"Расходы на дипломатию: {get_diplomacy_spending():.2f}\n"
            f"Вложения в рост стабильности: {get_stability_invest_spending(player, player_country):.2f}\n"
            f"Вложения в рост милитаризации: {get_militarization_invest_spending(player, player_country):.2f}\n"
            f"Выплата процентов по займам: {get_loan_spending(player_country):.2f}"
            "\n\n"
            f"Общие расходы: {get_total_spending(player, player_country):.2f}")
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=SPENDING_KB
    )

def open_pops_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Общее население: {get_total_population(player, 0)}\n"
            f"Рост населения в следующем ходе: {get_next_step_growth(player, player_country):.0f}\n"
            f"Ежемесячный рост населения: {get_percent_pop_growth(player_country)*100:.2f}%"
            "\n\n"
            f"Расходы на рост населения: {get_pops_invest_spending(player, player_country):.2f} монет в ход")

    bot.edit_message_text(
        text,
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = POPS_KB
    )

def open_army_spending_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Общее количество юнитов: {get_total_army(player_country)}"
            "\n\n"
            f"Влияние вложений на атаку: {get_army_buff_spending(player_country, 'attack_modifier')*100:.2f}%\n"
            f"Влияние вложений на оборону: {get_army_buff_spending(player_country, 'defense_modifier')*100:.2f}%\n"
            f"Влияние вложений на боевой дух: {get_army_buff_spending(player_country, 'morale_modifier')*100:.2f}%\n"
            f"Влияние вложений на HP: {get_army_buff_spending(player_country, 'hp_modifier')*100:.2f}%"
            "\n\n"
            f"Процент обеспечения: {get_army_buff_spending(player_country, 'army_maintenance')*100:.2f}%\n"
            f"Расходы на обеспечение армии: {get_army_spending(player_country):.2f} монет в ход")

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=ARMY_KB
    )

def open_stability_invest_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Текущая стабильность: {get_modifier(player_country, 'stability')*100:.2f}\n"
            f"Ожидаемый рост: {get_stability_growth(player_country)*100:.2f}%"
            "\n\n"
            f"Расходы на рост стабильности: {get_stability_invest_spending(player, player_country):.2f} монет в ход")

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=STABILITY_KB
    )

def open_militarization_invest_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Текущая степень милитаризации: {get_modifier(player_country, 'militarization')*100:.2f}\n"
            f"Ожидаемый рост: {get_militarization_growth(player_country)*100:.2f}%"
            "\n\n"
            f"Расходы на рост милитаризации: {get_militarization_invest_spending(player, player_country):.2f} монет в ход")

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=MILITARIZATION_KB
    )