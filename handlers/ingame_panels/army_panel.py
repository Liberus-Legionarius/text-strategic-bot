from handlers.callbacks.callback_start import callback
from services.bot import bot
from services.constants import get_player, get_date_move
from services.math.army_math import *
from services.math.economy_math import get_prod_units_consumption, get_prod_units, get_army_spending
from services.math.territory_math import get_total_population
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

ARMY_KB = InlineKeyboardMarkup()
ARMY_KB.add(InlineKeyboardButton("Политика призыва", callback_data = "army:mobilization:open"),
            InlineKeyboardButton("Армии", callback_data = "army:armies:open"),
            InlineKeyboardButton("Назад", callback_data = "state:base:open"))

ONE_ARMY_KB = InlineKeyboardMarkup()
ONE_ARMY_KB.add(InlineKeyboardButton("WIP", callback_data = "army:armies:open"), InlineKeyboardButton("Назад", callback_data = "army:armies:open"))

def open_army_panel(user, chat_id, message_id):
    player = get_player(user)

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"Количество боевых подразделений: {get_total_army(player)}\n"
            f"Общая боевая мощь: {get_army_power(player)}"
            "\n\n"
            f"Затраты единиц производства: {get_prod_units_consumption(player)}\n"
            f"Всего единиц производства: {get_prod_units(player)}\n"
            f"Баланс единиц производства: {get_prod_units(player) - get_prod_units_consumption(player)}"
            "\n\n"
            f"Расходы на содержание армии: {get_army_spending(player)} монет в ход"
            "\n\n"
            f"Общее население: {get_total_population(player)}\n"
            f"Мобилизационный резерв: {int(get_manpower(player))}\n"
            f"Служба для женщин: {get_women_at_war(player)}"
            )
    bot.edit_message_text(
            text,
            chat_id = chat_id,
            message_id = message_id,
            reply_markup = ARMY_KB
    )

def open_mobilization_panel(user, chat_id, message_id):
        player = get_player(user)

        text = (f"{get_date_move(player)}"
                "\n\n"
                f"Общее население страны: {get_total_population(player)}\n"
                f"Мобилизационный резерв: {int(get_manpower(player))}"
                "\n\n"
                "Наши законы в отношении призыва:\n"
                f"\t- Закон о призыве: {MOBILIZATION_LAWS[player['mobilization_law']]['title']}\n"
                f"\t\t- Процент военнообязанных: {get_manpower_percent(player):.2f}%\n"
                f"\t\t- Статус женской службы: {get_women_at_war(player)}")

        mobilization_kb = InlineKeyboardMarkup()
        for law_id, law in MOBILIZATION_LAWS.items():
                if not player["mobilization_law"] == law_id:
                        mobilization_kb.add(InlineKeyboardButton(law["title"], callback_data = f"army:mobilization:{str(law_id)}"))
        mobilization_kb.add(InlineKeyboardButton("Вернуться", callback_data = "army:base:open"))
        bot.edit_message_text(
                text,
                chat_id = chat_id,
                message_id = message_id,
                reply_markup = mobilization_kb
        )

def open_armies_panel(user, chat_id, message_id):
        player = get_player(user)

        text = (f"{get_date_move(player)}"
                "\n\n"
                f"Количество боевых подразделений: {get_total_army(player)}\n"
                f"Общая боевая мощь: {get_army_power(player)}"
                "\n\n"
                f"Типы подразделений и их распределение:\n")

        for a_type in ARMY_TYPES.values():
                text += f'{str(a_type["title"])} - {len(list(filter(lambda unit: unit["type_id"] == a_type["_id"], player["armies"])))}\n'

        armies_kb = InlineKeyboardMarkup()

        for army in player["armies"]:
                armies_kb.add(InlineKeyboardButton(f"{army['name']} ({next((city for city in player['cities'] if city['city_id'] == army['city_id']), None)['name']})",
                                                   callback_data = f"army:armies:{army['army_id']}"))

        armies_kb.add(InlineKeyboardButton("Назад", callback_data = "army:base:open"))

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=armies_kb
        )

def open_one_army_panel(user, chat_id, message_id, army_id):
        player = get_player(user)

        army = next((a for a in player["armies"] if str(a["army_id"]) == army_id), None)

        text = (f"{get_date_move(player)}"
                "\n\n"
                f"Название подразделения: {army['name']}"
                "\n\n"
                f"Тип: {get_army_type(army)['title']}\n"
                f"Боевая мощь: {get_army_type(army)['power']}\n"
                f"Атака: {get_army_type(army)['attack']}\n"
                f"Бронебойность: {get_army_type(army)['armour_piercing']}\n"
                f"Защита: {get_army_type(army)['defense']}\n"
                f"Является бронированным: {get_is_armour(army)}"
                "\n\n"
                f"Противодействует: {get_army_counteracts(army)}"
                "\n\n"
                f"Расходы производства: {get_army_type(army)['prod_units_consumption']}\n"
                f"Ежемесячные расходы: {get_army_type(army)['per_unit_spending']}")

        bot.edit_message_text(
                text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=ONE_ARMY_KB
        )



