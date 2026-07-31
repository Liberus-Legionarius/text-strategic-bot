from services.bot import bot
from handlers.ingame_panels.state_panel import open_state_panel

@bot.callback_query_handler(func=lambda call: call.data.startswith("state"))
def callback_state(call):
    bot.answer_callback_query(call.id)
    panels = call.data.split(":")
    if panels[1] == "open":
        open_state_panel(call.from_user, call.message.chat.id, call.message.message_id)