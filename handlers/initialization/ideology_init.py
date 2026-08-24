from services.bot import bot, db
from services.constants import get_player
from handlers.initialization.common_init import *
import services.ai as ai

# Выбор государственной идеологии.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_IDEOLOGY")
def ideology_init(message):
    last_message = get_player(message.from_user)["last_message"]
    if check_format(PATTERN_UPPERCASE, message.text, message.chat.id, last_message):
        ai_check = ai.check_ideology(message.text, get_player(message.from_user)["api_key"])
        if name_handler(ai_check, message.chat.id, last_message, "название идеологии"):
            db.players.update_one({"tg_id": message.from_user.id, "countries.id":0},
                                  {"$set": {"bot_state": "INIT_FULLNAME", "countries.$.ideology": message.text}})
            bot.edit_message_text(
                "Раз уж с гос. режимом определились, давайте придумаем вашей стране полное название.\n"
                "Чувствуйте себя свободно, только учитывайте, что выбранная идеология будет учитываться при проверке полного названия.",
                chat_id = message.chat.id,
                message_id = last_message
            )
    bot.delete_message(message.chat.id, message.message_id)