from services.bot import bot
from services.constants import get_player, get_date_move
from services.modifiers import modifiers_russified, modifiers_units
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

DIARY_KB = InlineKeyboardMarkup(row_width=1)
DIARY_KB.add(InlineKeyboardButton("Национальные духи", callback_data = "diary:national_spirits:open"),
             InlineKeyboardButton("Вернуться", callback_data = "state:open"))
SPIRITS_KB = InlineKeyboardMarkup(row_width=1)
SPIRITS_KB.add(InlineKeyboardButton("Вернуться", callback_data = "diary:base:open"))

def open_diary_panel(user, chat_id, message_id):
    player = get_player(user)

    goals = "Цели:\n"
    for goal in player["goals"]:
        goals += f"\t\t\t- {goal}\n"

    ambitions = "Территориальные амбиции:\n"
    for ambition in player["territorial_ambitions"]:
        ambitions += f"\t\t\t- {ambition}\n"
    if ambitions == "Территориальные амбиции:\n":
        ambitions += "\t\t\t- Отсутствуют.\n"

    ultimate_goal = ("Абсолютная цель:\n"
                     f"\t\t\t- {player['ultimate_goal']}")

    text = (f"{get_date_move(player)}"
            "\n\n"
            "Вот и ваш дневник.\n"
            "Здесь вы можете просмотреть цели и амбиции вашего государства... Не беспокойтесь, если список слишком короткий, вы ещё успеете его расширить в ходе внутриигровых событий."
            "\n\n"
            f"{goals}\n"
            f"{ambitions}\n"
            f"{ultimate_goal}")

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=DIARY_KB
    )

def open_national_spirits_panel(user, chat_id, message_id):
    player = get_player(user)

    national_spirits = "Наши национальные духи:\n"
    for spirit in player["national_spirits"]:
        national_spirits += f'\n\t\t- {spirit["name"]}\n'
        for key, value in spirit.items():
            if key in modifiers_russified:
                national_spirits += f'\t\t\t\t- {modifiers_russified[key]}: {get_unit_of_modifier(key, value)}\n'

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"{national_spirits}")

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=SPIRITS_KB
    )


def get_unit_of_modifier(modifier, value):
    unit = modifiers_units[modifier]
    if unit == "%":
        return f"{value*100:.2f}%"
    elif unit == "1":
        return f"{value:.2f}"
    elif unit == "yesno":
        return "Да" if value else "Нет"