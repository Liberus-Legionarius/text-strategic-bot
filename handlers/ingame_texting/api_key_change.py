from handlers.ingame_panels.settings_panel import open_settings_panel
from services.bot import bot, db
from services.constants import get_player
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "API_KEY_CHANGE")
def api_key_changing(message):
    player = get_player(message.from_user)
    if not player["api_key"] == message.text:
        db.players.update_one({"tg_id":player["tg_id"]},
                      {
                          "$set": {"bot_state": "IN_GAME", "api_key": message.text}
                      })
    open_settings_panel(message.from_user, message.chat.id, player["last_message"])
    bot.delete_message(message.chat.id, message.message_id)