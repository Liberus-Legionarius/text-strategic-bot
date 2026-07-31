from services.bot import bot, db
from handlers.ingame_panels.economy_panel import open_economy_panel, open_income_panel, open_loan_panel

@bot.callback_query_handler(func=lambda call: call.data.startswith("economy"))
def callback_economy(call):
    bot.answer_callback_query(call.id)
    panel = call.data.split(':')[1]
     # Базовая панель.
    if panel == "base":
        open_economy_panel(call.from_user, call.message.chat.id, call.message.message_id)
    # Доходы.
    elif panel == "income":
        panel = call.data.split(':')[2]
        if panel == "rise":
            db.players.update_one({"tg_id":call.from_user.id, "countries.id": 0},
                                  {"$inc":{
                                        "countries.$.national_spirits.1.stability":-0.05,
                                        "countries.$.national_spirits.1.tax_rate": 0.05}
                                  })
        elif panel == "down":
            db.players.update_one({"tg_id": call.from_user.id, "countries.id": 0},
                                  {"$inc": {
                                      "countries.$.national_spirits.1.stability": 0.05,
                                      "countries.$.national_spirits.1.tax_rate": -0.05}
                                  })
        open_income_panel(call.from_user, call.message.chat.id, call.message.message_id)
    # Займы.
    elif panel == "loan":
        panel = call.data.split(':')[2]
        if panel == "take":
            db.players.update_one({"tg_id":call.from_user.id},
                                  {"$set":{
                                        "bot_state":"TAKE_LOAN",
                                        "last_message":call.message.message_id
                                  }})
            bot.edit_message_text(
                "Введите желаемый размер займа.\nЕсли передумали, просто введите \"0\".",
                chat_id = call.message.chat.id,
                message_id = call.message.message_id,
                reply_markup = None
            )
        elif panel == "repay":
            if db.players.find_one({"tg_id": call.from_user.id})["countries"][0]["loans"] > 0:
                db.players.update_one({"tg_id": call.from_user.id},
                                      {"$set": {
                                            "bot_state": "REPAY_LOAN",
                                            "last_message":call.message.message_id
                                      }})
                bot.edit_message_text(
                    "Введите, сколько вы желаете выплатить.\nЕсли передумали, просто введите \"0\".",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=None
                )
        else:
            open_loan_panel(call.from_user, call.message.chat.id, call.message.message_id)