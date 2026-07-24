from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from handlers.initialization.common_init import *
from services.bot import bot, db
import services.ai as ai
from services.constants import get_player

# Выбор короткого названия
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_COUNTRYNAME")
def texting(message):
    if check_format(PATTERN_UPPERCASE, message.text, message.chat.id):
        ai_check = ai.check_countryname(message.text)
        if name_handler(ai_check, message.chat.id, "название страны"):
            db.players.update_one({"tg_id": message.from_user.id},
                            {"$set": {"bot_state": "INIT_IDEOLOGY", "countryname": message.text}})
            government_type_options = InlineKeyboardMarkup()
            government_type_options.add(InlineKeyboardButton("Республика", callback_data = "init:ideology:Республика"),
                                        InlineKeyboardButton("Монархия", callback_data = "init:ideology:Монархия"))
            bot.send_message(message.chat.id, "Раз уж с названием определились, перейдём к форме государственного управления."
                                              "\nВыберите один из предложенных ниже вариантов:", reply_markup = government_type_options)