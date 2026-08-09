from handlers.actions.militarization_growth_action import change_militarization_growth
from handlers.actions.pops_invest_action import change_pops_invest
from handlers.actions.stability_growth_action import change_stability_growth
from handlers.ingame_panels.spending_panel import *
from services.bot import bot, db

@bot.callback_query_handler(func=lambda call: call.data.startswith("spending"))
def callback_spending(call):
    bot.answer_callback_query(call.id)
    datas = call.data.split(":")
    player = get_player(call.from_user)
    if datas[1] == "base":
        open_spending_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif datas[1] == "pops":
        if not datas[2] == "open":
            change_pops_invest(player,0, float(datas[2]))
        open_pops_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif datas[1] == "army":
        if not datas[2] == "open":
            change = float(datas[2])
            country = get_country(get_player(call.from_user), 0)
            if 2 >= change + country["national_spirits"][4]["army_maintenance"] >= 0:
                change_army_invest(call.from_user, float(datas[2]))
            else:
                return
        open_army_spending_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif datas[1] == "stability":
        if not datas[2] == "open":
            change_stability_growth(player, 0, float(datas[2]))
        open_stability_invest_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif datas[1] == "militarization":
        if not datas[2] == "open":
            change_militarization_growth(player, 0, float(datas[2]))
        open_militarization_invest_panel(call.from_user, call.message.chat.id, call.message.message_id)


def change_army_invest(user, change):
    db.players.update_one({
        "tg_id":user.id, "countries.id":0
    },
    {"$inc":{
        "countries.$.national_spirits.4.army_maintenance":change,
        "countries.$.national_spirits.4.morale_modifier":change/5,
        "countries.$.national_spirits.4.hp_modifier":change/5,
        "countries.$.national_spirits.4.attack_modifier":change/10,
        "countries.$.national_spirits.4.defense_modifier":change/10,
    }})
