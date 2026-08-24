from services.bot import bot, db
from handlers.initialization.common_init import *
from services.constants import get_player
import services.ai as ai

# Выбор полного названия страны.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_FULLNAME")
def full_countryname_init(message):
    player = get_player(message.from_user)
    if check_format(PATTERN_UPPERCASE, message.text, message.chat.id, player["last_message"]):
        ai_check = ai.check_fullname(message.text, player["countries"][0]["countryname"], player["countries"][0]["ideology"], player["api_key"])
        if name_handler(ai_check, message.chat.id, player["last_message"], "полное название страны"):
            bot.edit_message_text(
                "Отлично, теперь остаётся только выбрать столицу вашей страны.\n"
                "К слову, ваша столица в начале будет единственным городом, которым вы владеете.",
                chat_id = message.chat.id,
                message_id = player["last_message"]
            )
            db.players.update_one({"tg_id": message.from_user.id, "countries.id":0},
                                  {"$set": {"bot_state": "INIT_CAPITAL", "countries.$.full_countryname": message.text}})
    bot.delete_message(message.chat.id, message.message_id)