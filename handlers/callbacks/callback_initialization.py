from services.bot import db, bot
from handlers.ingame_panels.state_initialization import init_state
from handlers.ingame_panels.state_panel import open_state_panel

@bot.callback_query_handler(func=lambda call: call.data.startswith("init"))
def callback_init(call):
    bot.answer_callback_query(call.id)
    phase = call.data.split(":")[1]
    # Начало игры.
    if call.data.startswith("init:enter"):
        init_state(call.from_user)
        open_state_panel(call.message.chat.id, call.from_user, call.message.message_id)