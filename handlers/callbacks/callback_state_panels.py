from services.bot import bot, db
from handlers.ingame_panels.state_panel import open_state_panel
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

from services.constants import get_player

BACK_KB = InlineKeyboardMarkup()
BACK_KB.add(InlineKeyboardButton("Вернуться", callback_data = "state:open"))

@bot.callback_query_handler(func=lambda call: call.data.startswith("state"))
def callback_state(call):
    bot.answer_callback_query(call.id)
    panels = call.data.split(":")
    if panels[1] == "open":
        if not get_player(call.from_user)["bot_state"] == "IN_GAME":
            db.players.update_one({"tg_id": call.from_user.id},
                                  {
                                      "$set": {"bot_state": "IN_GAME"}
                                  })
        open_state_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panels[1] == "rename":
        db.players.update_one({"tg_id":call.from_user.id},
                              {
                                  "$set":{"bot_state":"COUNTRY_RENAME_SHORT", "last_message":call.message.message_id}
                              })
        bot.edit_message_text(
            "Введите желаемое краткое название для вашей страны.\n"
            "Правила всё те же, что и при инициализации, вот только повысить ранг нельзя при малом количестве городов.",
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = BACK_KB
        )
