from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from handlers.initialization.common_init import *
from services.bot import bot, db
import services.ai as ai
from services.constants import get_player

# Выбор короткого названия
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_COUNTRYNAME")
def texting(message):
    last_message = get_player(message.from_user)["last_message"]
    if check_format(PATTERN_UPPERCASE, message.text, message.chat.id, last_message):
        ai_check = ai.check_countryname(message.text, get_player(message.from_user)["api_key"])
        if name_handler(ai_check, message.chat.id, last_message, "название страны"):
            db.players.update_one({"tg_id": message.from_user.id},
                            {"$set": {"bot_state": "INIT_IDEOLOGY", "countries":[{"id":0, "countryname": message.text}]}})
            bot.edit_message_text(
                "Раз уж с названием определились, перейдём к идеологии.\n"
                "Можете написать любую идеологию, почти без ограничений.",
                chat_id = message.chat.id,
                message_id = last_message
            )
    bot.delete_message(message.chat.id, message.message_id)