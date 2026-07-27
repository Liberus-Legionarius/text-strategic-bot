from services.bot import bot, db
from handlers.initialization.common_init import *
from services.constants import get_player
from handlers.ingame_panels.economy_panel import open_loan_panel

# Взять заём.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "TAKE_LOAN")
def take_loan(message):
    player = get_player(message.from_user)
    if float(message.text) >= 0:
        db.players.update_one({"tg_id": message.from_user.id},
                              {"$inc": {"loans": float(message.text), "money": float(message.text)},
                               "$set": {"bot_state": "IN_GAME"}})
        open_loan_panel(message.from_user, message.chat.id, player["last_message"])
    bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "REPAY_LOAN")
def repay_loan(message):
    player = get_player(message.from_user)
    if float(message.text) >= 0:
        db.players.update_one({"tg_id": message.from_user.id},
                              {"$inc": {"loans": -float(message.text), "money": -float(message.text)},
                               "$set": {"bot_state": "IN_GAME"}})
        open_loan_panel(message.from_user, message.chat.id, player["last_message"])
    bot.delete_message(message.chat.id, message.message_id)