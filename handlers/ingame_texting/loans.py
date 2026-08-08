from services.bot import bot, db
from handlers.initialization.common_init import *
from services.constants import get_player, get_country
from handlers.ingame_panels.economy_panel import open_loan_panel
from services.math.economy_math import get_total_income, get_total_spending


# Взять заём.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "TAKE_LOAN")
def take_loan(message):
    player = get_player(message.from_user)
    country = get_country(player, 0)
    ten_year_balance = (get_total_income(player, country) - get_total_spending(player, country))*120
    if float(message.text) >= 0:
        if country["loans"] < ten_year_balance:
            to_take = min(float(message.text), ten_year_balance - country["loans"])
            db.players.update_one({"tg_id": message.from_user.id, "countries.id":0},
                                  {"$inc": {"countries.$.loans": to_take, "countries.$.money": to_take},
                                   "$set": {"bot_state": "IN_GAME"}})
        open_loan_panel(message.from_user, message.chat.id, player["last_message"])
    bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "REPAY_LOAN")
def repay_loan(message):
    player = get_player(message.from_user)
    country = get_country(player, 0)
    if float(message.text) >= 0:
        to_repay = min(float(message.text), country["loans"])
        db.players.update_one({"tg_id": message.from_user.id, "countries.id":0},
                              {"$inc": {"countries.$.loans": -to_repay, "countries.$.money": -to_repay},
                               "$set": {"bot_state": "IN_GAME"}})
        open_loan_panel(message.from_user, message.chat.id, player["last_message"])
    bot.delete_message(message.chat.id, message.message_id)