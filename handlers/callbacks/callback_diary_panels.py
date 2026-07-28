from services.bot import bot
from handlers.ingame_panels.diary_panel import open_diary_panel, open_national_spirits_panel

@bot.callback_query_handler(func=lambda call: call.data.startswith("diary"))
def callback_diary(call):
    bot.answer_callback_query(call.id)
    panels = call.data.split(":")
    if panels[1] == "base":
        open_diary_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panels[1] == "national_spirits":
        open_national_spirits_panel(call.from_user, call.message.chat.id, call.message.message_id)