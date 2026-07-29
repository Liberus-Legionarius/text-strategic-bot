from services.bot import bot, db
from handlers.ingame_panels.army_panel import open_army_panel, open_mobilization_panel, open_armies_panel, \
    open_one_army_panel, open_campaign_panel
from services.constants import MOBILIZATION_LAWS, get_player, get_country
from bson import ObjectId

from services.math.army_math import get_army_type
from services.math.territory_math import get_cities


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
            country = get_country(player, 0)
            if law in MOBILIZATION_LAWS.keys() and not law == country["national_spirits"][2]["_id"]:
                to_add = MOBILIZATION_LAWS[law]
                to_add.update({"name":"Политика призыва"})
                db.players.update_one({"tg_id":call.from_user.id, "countries.id":0},
                                      {"$set":{"countries.$.national_spirits.2":to_add}})
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
            if get_country(get_player(call.from_user), 0)["money"] >= int(datas[3]):
                start_campaign(call.from_user, datas[2], int(datas[3]))
                open_armies_panel(call.from_user, call.message.chat.id, call.message.message_id)

def start_campaign(user, army_id, cost):
    player = get_player(user)
    country = get_country(player, 0)
    army = next((army for army in country["armies"] if str(army["army_id"]) == army_id), None)
    city = next((city for city in get_cities(player, 0) if city["_id"] == army["city_id"]), None)
    db.players.update_one({"tg_id":user.id, "countries.id":0},
                          {"$push":{
                                "countries.$.campaigns":{
                                    "started": player["step"],
                                    "cost": cost,
                                    "army":army
                                },
                                "countries.$.actions":f"Армия '{army['name']}' типа {get_army_type(army)['title']}, размещённая в городе {city['name']}, "
                                          f"отправилась в исследовательскую экспедицию. Стоимость экспедиции составила {cost} монет."
                          },
                          "$pull":{
                                "countries.$.armies":army
                          },
                          "$inc":{"countries.$.money":-cost}})