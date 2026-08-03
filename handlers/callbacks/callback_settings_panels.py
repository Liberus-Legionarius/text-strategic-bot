from services.bot import db, bot
from handlers.ingame_panels.settings_panel import *

@bot.callback_query_handler(func=lambda call: call.data.startswith("settings"))
def callback_settings(call):
    bot.answer_callback_query(call.id)
    datas = call.data.split(":")
    if datas[1] == "open":
        open_settings_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif datas[1] == "change_api_key":
        db.players.update_one({"tg_id":call.from_user.id},
                              {
                                  "$set": {"bot_state":"API_KEY_CHANGE", "last_message":call.message.message_id}
                              })
        bot.edit_message_text(
            "Введите новый API-ключ. Вы также можете просто ввести старый ключ, если передумали.\n"
            f"Ваш текущий API-ключ: {get_player(call.from_user)['api_key']}",
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = None
        )