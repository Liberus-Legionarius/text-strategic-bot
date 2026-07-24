from services.bot import db, bot
from handlers.ingame_panels.state_initialization import init_state
from handlers.ingame_panels.state_panel import open_state_panel

@bot.callback_query_handler(func=lambda call: call.data.startswith("init"))
def callback_init(call):
    bot.answer_callback_query(call.id)
    # Начало игры.
    if call.data.startswith("init:enter"):
        init_state(call.from_user)
        open_state_panel(call.message.chat.id, call.from_user, call.message.message_id)
    # Инициализация деталей.
    elif call.data == "init:country:no":
        db.players.update_one({"tg_id":call.from_user.id},
                              {"$set":{
                                  "ideology_desc": None,
                                  "goals": None,
                                  "territorial_ambitions": None,
                                  "bot_state":"INIT_DETAILS"
                              }})
        bot.edit_message_text(
            "Тогда напишите о своём государстве. Обязательно опишите идеологию в подробностях, перечислите цели вашего государства (первоначальные) и ваши территориальные амбиции.",
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = None
        )
