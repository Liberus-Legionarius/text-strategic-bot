from services.bot import bot, db
from handlers.initialization.common_init import *
from services.constants import get_player
import services.ai as ai

# Выбор полного названия страны.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_FULLNAME")
def ideology_init(message):
    if check_format(PATTERN_UPPERCASE, message.text, message.chat.id):
        player = get_player(message.from_user)
        ai_check = ai.check_fullname(message.text, player.get("countryname"), player.get("ideology"))
        if name_handler(ai_check, message.chat.id, "полное название страны"):
            bot.send_message(message.chat.id, "Отлично, теперь остаётся только выбрать столицу вашей страны.\n"
                                              "К слову, ваша столица в начале будет единственным городом, которым вы владеете.")
            db.players.update_one({"tg_id": message.from_user.id},
                                  {"$set": {"bot_state": "INIT_CAPITAL", "full_countryname": message.text}})