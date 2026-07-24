from handlers.ingame_panels.state_initialization import init_state
from handlers.ingame_panels.state_panel import open_state_panel
from services.bot import db, bot
from handlers.initialization.start import new_start

@bot.callback_query_handler(func = lambda call: call.data.startswith("start"))
def callback(call):
    bot.answer_callback_query(call.id)
    if call.data == "start:yes":
        if not db.players.find_one({"tg_id":call.from_user.id}).get("money"):
            init_state(call.from_user)
        open_state_panel(call.message.chat.id, call.from_user)
    else:
        new_start(call.message.chat.id, call.from_user)
        bot.edit_message_text(
            "Ваш предыдущий прогресс очищен.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
