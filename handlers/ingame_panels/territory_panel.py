from services.bot import db, bot
from services.constants import get_player, get_date_move, get_buildings_info, get_country
from services.math.territory_math import *
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from bson import ObjectId

TERRITORY_KB = InlineKeyboardMarkup(row_width=1)
TERRITORY_KB.add(InlineKeyboardButton("Выбрать город", callback_data = "territory:cities:open"),
                 InlineKeyboardButton("Назад", callback_data = "state:open"))

def open_territory_panel(user, chat_id, message_id):
    player = get_player(user)
    player_country = get_country(player, 0)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Столица: {player_country['capital']}"
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

def open_cities_panel(user, chat_id, message_id):
    player = get_player(user)
    country_player = get_country(player, 0)
    cities_kb = InlineKeyboardMarkup(row_width=3)
    cities = get_cities(player, 0)
    for city in cities:
        cities_kb.add(InlineKeyboardButton(city["name"], callback_data = f"territory:cities:{city['name']}"))
    cities_kb.row(InlineKeyboardButton("Вернуться", callback_data = "territory:base:open"))
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Столица: {country_player['capital']}"
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

def open_one_city_panel(user, chat_id, message_id, city_name):
    player = get_player(user)
    player_country = get_country(player, 0)
    city = get_city_by_name(player, city_name)
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Население: {int(city['population'])}\n"
            f"Доход с налогов: {get_one_city_tax_income(player_country, city):.2f} монет в ход\n"
            f"Доход от зданий: {get_prod_city_income(player_country, city):.2f} монет в ход\n"
            f"Здания: {get_buildings(city)}")

    city_kb = InlineKeyboardMarkup()
    city_kb.row(InlineKeyboardButton("Построить здание", callback_data=f"territory:cities:{city_name}:b"),
                InlineKeyboardButton("Разграбить", callback_data=f"territory:cities:{city_name}:raze"))
    city_kb.row(InlineKeyboardButton("Нанять армию", callback_data=f"army:create:{city_name}"))
    city_kb.row(InlineKeyboardButton("Сменить столицу (125м, 50пп)", callback_data = f"territory:cities:{city_name}:capital"))
    city_kb.row(InlineKeyboardButton("Вернуться", callback_data="territory:cities:open"))

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=city_kb
    )

def open_buildings_panel(user, chat_id, message_id, city_name):
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
                                              callback_data=f"territory:b:{city_name}:{building['_id']}"))
    buildings_kb.row(InlineKeyboardButton("Вернуться", callback_data=f"territory:cities:{city_name}"))

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=buildings_kb
    )