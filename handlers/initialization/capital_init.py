from services.bot import bot, db
from handlers.initialization.common_init import *
from services.constants import get_player
import services.ai as ai
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from services.map.map_management import city_exists_on_map, load_map

# Выбор столицы.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_CAPITAL")
def capital_init(message):
    player = get_player(message.from_user)
    capitals = city_exists_on_map(message.text)
    if len(capitals) == 1:
            bot.edit_message_text(
                "Хорошо, город существует на текущей карте игры.\n"
                "Сейчас проверю, имеет ли выбранная столица смысл для вашей страны...",
                chat_id=message.chat.id,
                message_id=player["last_message"],
                reply_markup=None
            )
            check_capital(player, capitals[0], message.chat.id)

    elif len(capitals) > 1:
        capitals_kb = InlineKeyboardMarkup()
        for capital in capitals:
            capitals_kb.row(InlineKeyboardButton(capital["province"], callback_data=f"init:capital:{capital['_id']}"))
        bot.edit_message_text(
            "Кажется, на карте имеется несколько городов с таким названием.\n"
            "Ниже вы можете выбрать, город из какой провинции вы имели в виду.",
            chat_id=message.chat.id,
            message_id=player["last_message"],
            reply_markup=capitals_kb
        )
    else:
        bot.edit_message_text(
            "К сожалению, этого города нет на текущей карте.\n"
            "Введите другой город в качестве столицы своего государства.",
            chat_id = message.chat.id,
            message_id = player["last_message"],
            reply_markup=None
        )
    bot.delete_message(message.chat.id, message.message_id)


def check_capital(player, capital, chat_id):
    ai_check = ai.check_capital(capital["name"], player["countries"][0].get("countryname"), player["api_key"])
    if name_handler(ai_check, chat_id, player["last_message"], "название столицы"):
        load_map(player["tg_id"])
        db.players.update_one({"tg_id": player["tg_id"], "countries.id": 0},
                              {"$set": {"countries.$.capital": capital["_id"]}})
        bot.edit_message_text(
            "Инициализация практически завершена.\n"
            "Но перед тем, как мы начнём, я постараюсь определить, как вы представляете свою страну, какие у вашей страны цели.\n"
            "В дальнейшем это позволит мне генерировать максимально подходящие события, аккуратно ведя вас к триумфу выбранной нации.\n"
            "Впрочем, если я не угадаю, вы сможете сами описать свою страну.",
            chat_id=chat_id,
            message_id=player["last_message"],
            reply_markup=None
        )
        response = ai.write_country_lore(player)
        ideology = f"Объяснение вашей идеологии:\n{response['ideology']}\n"
        goals = "Цели вашего государства:\n"
        for n, g in enumerate(response["goals"]):
            goals += f"{n + 1}. {g}\n"
        territory = "Территориальные амбиции (на данный момент):\n"
        for n, t in enumerate(response["territorial_ambitions"]):
            territory += f"{n + 1}. {t}\n"

        ultimate_goal = f"Наша конечная цель:\n{response['ultimate_goal']}"

        set_details(player["tg_id"], response["ideology"], response["ideology_type"], response["goals"],
                    response["ultimate_goal"], response["territorial_ambitions"],
                    response["country_characteristics"])

        details_kb = InlineKeyboardMarkup()
        details_kb.add(InlineKeyboardButton("Да, мне это подходит", callback_data=f"init:enter"),
                       InlineKeyboardButton("Нет, у меня другие идеи...", callback_data="init:country:no"))

        bot.edit_message_text(
            "Я оценил входящие данные...\n"
            "Вот описание вашей страны:\n"
            "\n"
            f"{response['response']}\n"
            "\n"
            f"{ideology}\n"
            f"{goals}\n"
            f"{territory}\n"
            f"{ultimate_goal}\n"
            "\n"
            "Что скажете о таком описании?",
            chat_id=chat_id,
            message_id=player["last_message"],
            reply_markup=details_kb
        )