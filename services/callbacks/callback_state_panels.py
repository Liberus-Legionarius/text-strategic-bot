from bot import bot, db
from ingame_logic.state_panel import open_state_panel

@bot.callback_query_handler(func=lambda call: call.data.startswith("state"))
def callback_state(call):
    bot.answer_callback_query(call.id)
    if call.data.endswith("open"):
        open_state_panel(call.message.chat.id, call.from_user, call.message.message_id)