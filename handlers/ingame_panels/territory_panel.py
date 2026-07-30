from services.bot import db, bot
from services.constants import get_player, get_date_move, get_buildings_info, get_country, get_city_name
from services.math.territory_math import *
from services.math.economy_math import get_pops_invest_spending
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from bson import ObjectId

TERRITORY_KB = InlineKeyboardMarkup(row_width=2)
TERRITORY_KB.add(InlineKeyboardButton("Население", callback_data="territory:pops:open"),
                 InlineKeyboardButton("Выбрать город", callback_data = "territory:cities:open"),
                 InlineKeyboardButton("Назад", callback_data = "state:open"))
POPS_KB = InlineKeyboardMarkup(row_width=3)
POPS_KB.add(InlineKeyboardButton("-5%", callback_data = "territory:pops:down5"), InlineKeyboardButton("-2%", callback_data = "territory:pops:down2"),
            InlineKeyboardButton("-1%", callback_data = "territory:pops:down1"),InlineKeyboardButton("1%", callback_data = "territory:pops:rise1"),
            InlineKeyboardButton("2%", callback_data = "territory:pops:rise2"),InlineKeyboardButton("5%", callback_data = "territory:pops:rise5"),
            InlineKeyboardButton("Вернуться", callback_data="territory:base:open"))

def open_territory_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Столица: {get_city_name(player_country['capital'])}"
            "\n\n"
            f"Количество городов: {len(get_cities(player, 0))}\n"
            f"Общее население: {get_total_population(player, 0)}\n"
            f"Среднее население: {get_avg_population(player, 0):.0f}\n"
            f"Крупнейший город: {get_largest_city(player, 0)}")

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=TERRITORY_KB
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

def open_cities_panel(user, chat_id, message_id):
    player = get_player(user)
    country_player = get_country(player, 0)
    db.players.update_one({"tg_id": user.id},{
        "$set":{"selected_city":None}
    })
    cities_kb = InlineKeyboardMarkup(row_width=3)
    cities = get_cities(player, 0)
    for city in cities:
        cities_kb.add(InlineKeyboardButton(city["name"], callback_data = f"territory:cities:{str(city['_id'])}"))
    cities_kb.row(InlineKeyboardButton("Вернуться", callback_data = "territory:base:open"))
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Столица: {get_city_name(country_player['capital'])}"
            "\n\n"
            f"Количество городов: {len(get_cities(player, 0))}\n"
            f"Общее население: {get_total_population(player, 0)}\n"
            f"Среднее население: {get_avg_population(player, 0):.0f}\n"
            f"Крупнейший город: {get_largest_city(player, 0)}")

    bot.edit_message_text(
        text,
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = cities_kb
    )

def open_one_city_panel(user, chat_id, message_id, city_id):
    player = get_player(user)
    player_country = get_country(player, 0)
    city_id = ObjectId(city_id)
    city = next((city for city in get_cities(player, 0) if city["_id"] == city_id), None)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Население: {city['population']}\n"
            f"Доход с налогов: {get_one_city_tax_income(player_country, city):.2f} монет в ход\n"
            f"Доход от зданий: {get_prod_city_income(player_country, city):.2f} монет в ход\n"
            f"Здания: {get_buildings(city)}")

    city_kb = InlineKeyboardMarkup(row_width=3)
    city_kb.add(InlineKeyboardButton("Построить здание", callback_data=f"territory:cities:{city_id}:build"),
                InlineKeyboardButton("Разграбить", callback_data=f"territory:cities:{city_id}:raze"),
                InlineKeyboardButton("Нанять армию", callback_data=f"army:create:{city_id}"),
                InlineKeyboardButton("Вернуться", callback_data="territory:cities:open"))

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=city_kb
    )

def open_buildings_panel(user, chat_id, message_id, city_id):
    player = get_player(user)
    country_player = get_country(player, 0)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Казна: {country_player['money']:.2f}"
            "\n"
            f"{get_buildings_info()}"
            "\n\n"
            f"Учитывайте, что вы не можете построить ничего, что сделает казну отрицательной.")

    buildings_kb = InlineKeyboardMarkup(row_width=2)
    for building in BUILDINGS.values():
        buildings_kb.add(InlineKeyboardButton(f"{building['title']} ({building['cost']} монет)",
                                              callback_data=f"territory:build:{city_id}:{building['_id']}"))
    buildings_kb.row(InlineKeyboardButton("Вернуться", callback_data=f"territory:cities:{city_id}"))

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=buildings_kb
    )