from services.bot import db, bot
from services.constants import get_player, get_date_move, get_buildings_info, get_build_kb
from services.math.territory_math import *
from services.math.economy_math import get_pops_invest_spending
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

TERRITORY_KB = InlineKeyboardMarkup(row_width=2)
TERRITORY_KB.add(InlineKeyboardButton("Население", callback_data="territory:pops:open"),
                 InlineKeyboardButton("Выбрать город", callback_data = "territory:cities:open"),
                 InlineKeyboardButton("Назад", callback_data = "state:open"))
POPS_KB = InlineKeyboardMarkup(row_width=3)
POPS_KB.add(InlineKeyboardButton("-5%", callback_data = "territory:pops:down5"), InlineKeyboardButton("-2%", callback_data = "territory:pops:down2"),
            InlineKeyboardButton("-1%", callback_data = "territory:pops:down1"),InlineKeyboardButton("1%", callback_data = "territory:pops:rise1"),
            InlineKeyboardButton("2%", callback_data = "territory:pops:rise2"),InlineKeyboardButton("5%", callback_data = "territory:pops:rise5"),
            InlineKeyboardButton("Вернуться", callback_data="territory:base:open"))
CITY_KB = InlineKeyboardMarkup(row_width=2)
CITY_KB.add(InlineKeyboardButton("Построить здание", callback_data = "territory:cities:city:build"),
              InlineKeyboardButton("Разграбить", callback_data = "territory:cities:city:raze"),
              InlineKeyboardButton("Вернуться", callback_data = "territory:cities:open"))

def open_territory_panel(user, chat_id, message_id):
    player = get_player(user)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Столица: {player['capital']}"
            "\n\n"
            f"Количество городов: {len(player['cities'])}\n"
            f"Общее население: {get_total_population(player)}\n"
            f"Среднее население: {get_avg_population(player):.0f}\n"
            f"Крупнейший город: {get_largest_city(player)}")

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=TERRITORY_KB
    )

def open_pops_panel(user, chat_id, message_id):
    player = get_player(user)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Общее население: {get_total_population(player)}\n"
            f"Рост населения в следующем ходе: {get_next_step_growth(player):.0f}\n"
            f"Ежемесячный рост населения: {get_percent_pop_growth(player)*100:.2f}%"
            "\n\n"
            f"Расходы на рост населения: {get_pops_invest_spending(player):.2f} монет в ход")

    bot.edit_message_text(
        text,
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = POPS_KB
    )

def open_cities_panel(user, chat_id, message_id):
    player = get_player(user)
    db.players.update_one({"tg_id": user.id},{
        "$set":{"selected_city":None}
    })
    cities_kb = InlineKeyboardMarkup(row_width=3)
    for city in player["cities"]:
        cities_kb.add(InlineKeyboardButton(city["name"], callback_data = f"territory:cities:{city['city_id']}"))
    cities_kb.row(InlineKeyboardButton("Вернуться", callback_data = "territory:base:open"))
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Столица: {player['capital']}"
            "\n\n"
            f"Количество городов: {len(player['cities'])}\n"
            f"Общее население: {get_total_population(player)}\n"
            f"Среднее население: {get_avg_population(player):.0f}\n"
            f"Крупнейший город: {get_largest_city(player)}")

    bot.edit_message_text(
        text,
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = cities_kb
    )

def open_one_city_panel(user, chat_id, message_id, city_id):
    player = get_player(user)
    city_id = int(city_id)
    city = next((city for city in player["cities"] if city["city_id"] == city_id), None)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Население: {city['population']}\n"
            f"Доход с налогов: {get_one_city_tax_income(player, city):.2f} монет в ход\n"
            f"Доход от зданий: {get_prod_city_income(city, player):.2f} монет в ход\n"
            f"Здания: {get_buildings(city)}")

    db.players.update_one({"tg_id":user.id},
                          {
                              "$set":{"selected_city":f"{city_id}"}
                          })

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=CITY_KB
    )

def open_buildings_panel(user, chat_id, message_id, city_id):
    player = get_player(user)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Казна: {player['money']:.2f}"
            "\n"
            f"{get_buildings_info()}"
            "\n\n"
            f"Учитывайте, что вы не можете построить ничего, что сделает казну отрицательной.")

    buildings_kb = get_build_kb(city_id)

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=buildings_kb
    )