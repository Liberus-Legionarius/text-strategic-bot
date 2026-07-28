from services.bot import bot, db
from handlers.ingame_panels.army_panel import open_army_panel, open_mobilization_panel, open_armies_panel, \
    open_one_army_panel, open_campaign_panel
from services.constants import MOBILIZATION_LAWS, get_player
from bson import ObjectId

@bot.callback_query_handler(func= lambda call: call.data.startswith("army"))
def callback_army(call):
    bot.answer_callback_query(call.id)
    panel = call.data.split(":")[1]
    if panel == "base":
        open_army_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panel == "mobilization":
        if not call.data.split(":")[2] == "open":
            law = ObjectId(call.data.split(":")[2])
            player = get_player(call.from_user)
            if law in MOBILIZATION_LAWS.keys() and not law == player["national_spirits"][2]["_id"]:
                db.players.update_one({"tg_id":call.from_user.id},
                                      {"$set":{"national_spirits.2":MOBILIZATION_LAWS[law]}})
                open_mobilization_panel(call.from_user, call.message.chat.id, call.message.message_id)
        else:
            open_mobilization_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panel == "armies":
        panel = call.data.split(":")[2]
        if panel == "open":
            open_armies_panel(call.from_user, call.message.chat.id, call.message.message_id)
        else:
            open_one_army_panel(call.from_user, call.message.chat.id, call.message.message_id, panel)
    elif panel == "campaign":
        datas = call.data.split(":")
        if len(datas) < 4:
            open_campaign_panel(call.from_user, call.message.chat.id, call.message.message_id, datas[2])
        else:
            if get_player(call.from_user)["money"] >= int(datas[3]):
                start_campaign(call.from_user, datas[2], int(datas[3]))
                open_armies_panel(call.from_user, call.message.chat.id, call.message.message_id)

def start_campaign(user, army_id, cost):
    player = get_player(user)
    army = next((army for army in player["armies"] if str(army["army_id"]) == army_id), None)
    db.players.update_one({"tg_id":user.id},
                          {"$push":{
                                "campaigns":{
                                    "started": player["step"],
                                    "cost": cost,
                                    "army":army
                                }
                          },
                          "$pull":{
                                "armies":army
                          },
                          "$inc":{"money":-cost}})