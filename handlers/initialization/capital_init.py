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
    if city_exists_on_map(message.text):
            bot.edit_message_text(
                "Хорошо, город существует на текущей карте игры.\n"
                "Сейчас проверю, имеет ли выбранная столица смысл для вашей страны...",
                chat_id=message.chat.id,
                message_id=player["last_message"]
            )
            ai_check = ai.check_capital(message.text, player["countries"][0].get("countryname"), player["api_key"])
            if name_handler(ai_check, message.chat.id, player["last_message"], "название столицы"):
                load_map(message.from_user.id)
                db.players.update_one({"tg_id": message.from_user.id, "countries.id": 0},
                                      {"$set": {"countries.$.capital": message.text}})
                bot.edit_message_text(
                    "Инициализация практически завершена.\n"
                    "Но перед тем, как мы начнём, я постараюсь определить, как вы представляете свою страну, какие у вашей страны цели.\n"
                    "В дальнейшем это позволит мне генерировать максимально подходящие события, аккуратно ведя вас к триумфу выбранной нации.\n"
                    "Впрочем, если я не угадаю, вы сможете сами описать свою страну.",
                    chat_id=message.chat.id,
                    message_id=player["last_message"]
                )
                response = ai.write_country_lore(get_player(message.from_user))
                ideology = f"Объяснение вашей идеологии:\n{response['ideology']}\n"
                goals = "Цели вашего государства:\n"
                for n, g in enumerate(response["goals"]):
                    goals += f"{n + 1}. {g}\n"
                territory = "Территориальные амбиции (на данный момент):\n"
                for n, t in enumerate(response["territorial_ambitions"]):
                    territory += f"{n + 1}. {t}\n"

                ultimate_goal = f"Наша конечная цель:\n{response['ultimate_goal']}"

                set_details(message.from_user.id, response["ideology"], response["ideology_type"], response["goals"],
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
                    chat_id=message.chat.id,
                    message_id=player["last_message"],
                    reply_markup=details_kb
                )
    else:
        bot.edit_message_text(
            "К сожалению, этого города нет на текущей карте.\n"
            "Введите другой город в качестве столицы своего государства.",
            chat_id = message.chat.id,
            message_id = player["last_message"]
        )
    bot.delete_message(message.chat.id, message.message_id)