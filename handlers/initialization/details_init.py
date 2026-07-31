from services.bot import bot, db
from handlers.initialization.common_init import *
from services.constants import get_player
import services.ai as ai
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

# Уточнение деталей.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_DETAILS")
def details_init(message):
    response = ai.define_details(message.text, get_player(message.from_user))
    set_details(message.from_user.id, response["ideology"], response["goals"], response["ultimate_goal"], response["territorial_ambitions"], response["country_characteristics"])
    details_kb = InlineKeyboardMarkup()
    details_kb.add(InlineKeyboardButton("Да начнётся игра!",callback_data="init:enter"))
    bot.send_message(message.chat.id, "На этом этап инициализации закончен.", reply_markup=details_kb)