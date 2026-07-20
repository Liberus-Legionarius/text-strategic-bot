from bot import bot, db
from ingame_logic.state_panel import open_state_panel
import  ingame_logic.economy_panel as economy

@bot.callback_query_handler(func=lambda call: call.data.endswith("open"))
def callback_open_panels(call):
    if call.data.startswith("economy"):
        panel = call.data.split(':')[1]
        if panel == "base": economy.open_economy_panel(call.from_user, call.message.chat.id, call.message.message_id)
        elif panel == "income":
            panel = call.data.split(':')[2]
            if panel == "rise":
                db.players.update_one({"tg_id":call.from_user.id},
                                      {"$inc":{
                                          "stability":-0.05, "taxes": 0.05
                                      }})
            elif panel == "down":
                db.players.update_one({"tg_id": call.from_user.id},
                                      {"$inc": {
                                          "stability": 0.05, "taxes": -0.05
                                      }})
            economy.open_income_panel(call.from_user, call.message.chat.id, call.message.message_id)
        elif panel == "spending": pass
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
                if db.players.find_one({"tg_id": call.from_user.id})["loans"] > 0:
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
                economy.open_loan_panel(call.from_user, call.message.chat.id, call.message.message_id)
        elif panel == "prod_units": pass
        elif panel == "build": pass
    elif call.data.startswith("army"):
        pass
    elif call.data.startswith("diplomacy"):
        pass
    elif call.data.startswith("state"):
        open_state_panel(call.message.chat.id, call.from_user, call.message)