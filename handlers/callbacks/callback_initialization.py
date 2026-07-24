from services.bot import db, bot
from handlers.ingame_panels.state_initialization import init_state
from handlers.ingame_panels.state_panel import open_state_panel

@bot.callback_query_handler(func=lambda call: call.data.startswith("init"))
def callback_init(call):
    bot.answer_callback_query(call.id)
    phase = call.data.split(":")[1]
    # Когда игрок выбирает идеологию.
    if phase == "ideology":
        ideology = call.data.split(":")[2]
        db.players.update_one({"tg_id":call.from_user.id}, {"$set":{"bot_state":"INIT_FULLNAME", "ideology":ideology}})
        bot.send_message(call.message.chat.id, "Раз уж с гос. режимом определились, давайте придумаем вашей стране полное название.\n"
                                               "Чувствуйте себя свободно, только не пишите, например, '*** Империя', если у вас гос. режим Республика.")
        bot.edit_message_text(
            f"Выбрана идеология: {ideology}.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    # Начало игры.
    elif call.data.startswith("init:enter"):
        init_state(call.from_user)
        open_state_panel(call.message.chat.id, call.from_user, call.message.message_id)