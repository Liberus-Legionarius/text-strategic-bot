from services.bot import bot, db
from handlers.initialization.common_init import *
from services.constants import get_player
import services.ai as ai

# Выбор столицы.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_CAPITAL")
def capital_init(message):
    if check_format(PATTERN_UPPERCASE, message.text, message.chat.id):
        player = get_player(message.from_user)
        ai_check = ai.check_capital(message.text, player.get("countryname"))
        if name_handler(ai_check, message.chat.id, "название столицы"):
            db.players.update_one({"tg_id": message.from_user.id},
                                  {"$set": {"bot_state": "IN_GAME", "capital": message.text}})
            bot.send_message(message.chat.id, "На этом этап инициализации закончен.", reply_markup=start_kb)