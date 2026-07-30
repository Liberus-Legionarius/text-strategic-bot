from handlers.ingame_panels.territory_panel import open_one_city_panel
from services.bot import bot, db
from handlers.ingame_panels.army_panel import open_army_panel, open_mobilization_panel, open_armies_panel, \
    open_one_army_panel, open_campaign_panel, open_delete_confirmation, open_army_reorganize, open_army_move_selection, \
    open_army_reorganize_unit_info, open_army_creation_panel
from services.math.army_math import get_army, get_reorganization_cost, get_manpower
from services.constants import MOBILIZATION_LAWS, get_player, get_country, ARMY_TYPES
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
            datas = call.data.split(":")
            if len(datas) < 4:
                open_one_army_panel(call.from_user, call.message.chat.id, call.message.message_id, panel)
            elif datas[3] == "delete":
                if len(datas) > 4:
                    if datas[4] == "yes":
                        player = get_player(call.from_user)
                        army = get_army(get_country(player, 0), panel)
                        cost = get_army_type(army)["cost"]*army["size"]/2
                        db.players.update_one({"tg_id": call.from_user.id, "countries.id":0},
                                              {
                                                  "$pull":{
                                                      "countries.$.armies":army
                                                  },
                                                  "$inc":{
                                                      "countries.$.money":cost
                                                  }
                                              })
                        to_inc = army["size"]*100/len(get_cities(player, 0))
                        db.cities.update_many({"player_id":player["tg_id"], "owner":0},
                                             {
                                                 "$inc":{
                                                     "population":to_inc
                                                 }
                                             })
                        open_armies_panel(call.from_user, call.message.chat.id, call.message.message_id)
                    elif datas[4] == "no":
                        open_one_army_panel(call.from_user, call.message.chat.id, call.message.message_id, panel)
                else:
                    open_delete_confirmation(call.from_user, call.message.chat.id, call.message.message_id, panel)
            elif datas[3] == "reorganize":
                if len(datas) > 4:
                    army_type = ARMY_TYPES[ObjectId(datas[4])]
                    army = get_army(get_country(get_player(call.from_user), 0), datas[2])
                    cost = get_reorganization_cost(army, army_type)
                    if len(datas) == 5 and get_country(get_player(call.from_user), 0)["money"] >= cost:
                        open_army_reorganize_unit_info(call.from_user, call.message.chat.id, call.message.message_id, panel, datas[4])
                    elif len(datas) == 6:
                        if datas[5] == "yes":
                            a = db.players.find_one({"tg_id":call.from_user.id, "countries.armies.army_id":int(panel)})
                            print(next((s for s in a["countries"][0]["armies"] if s["army_id"] == int(panel)), None)["size"])
                            db.players.update_one({"tg_id":call.from_user.id, "countries.0.armies.army_id":int(panel)},
                                                  {
                                                      "$set":{
                                                          "countries.0.armies.$.type_id": ObjectId(datas[4])
                                                      },
                                                      "$inc":{
                                                          "countries.0.money": -cost
                                                      }
                                                  })
                        open_one_army_panel(call.from_user, call.message.chat.id, call.message.message_id, panel)
                else:
                    open_army_reorganize(call.from_user, call.message.chat.id, call.message.message_id, panel)
            elif datas[3] == "move":
                pass
    elif panel == "campaign":
        datas = call.data.split(":")
        if len(datas) < 4:
            open_campaign_panel(call.from_user, call.message.chat.id, call.message.message_id, datas[2])
        else:
            if get_country(get_player(call.from_user), 0)["money"] >= int(datas[3]):
                start_campaign(call.from_user, datas[2], int(datas[3]))
                open_armies_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panel == "create":
        datas = call.data.split(":")
        player = get_player(call.from_user)
        country = get_country(player, 0)
        if get_manpower(player, country) >= 100 and db.cities.find_one({"_id":ObjectId(datas[2])})["population"] >= 250:
            if len(datas) == 4:
                i = max(country["armies"], key = lambda a: a["army_id"])["army_id"] + 1
                a_type = ARMY_TYPES[ObjectId(datas[3])]
                db.players.update_one({"tg_id":player["tg_id"]},
                                      {
                                          "$push":{
                                              "countries.0.armies":{
                                                  "army_id":i,
                                                  "name": f"Армия №{i}",
                                                  "size": 1,
                                                  "hp": a_type["hp"],
                                                  "morale": a_type["morale"],
                                                  "city_id": ObjectId(datas[2]),
                                                  "type_id": ObjectId(datas[3])
                                              }
                                          },
                                          "$inc":{
                                              "countries.0.money": -a_type["cost"]
                                          }
                                      })
                open_one_city_panel(call.from_user, call.message.chat.id, call.message.message_id, datas[2])
            else:
                open_army_creation_panel(call.from_user, call.message.chat.id, call.message.message_id, datas[2])

def start_campaign(user, army_id, cost):
    player = get_player(user)
    country = get_country(player, 0)
    army = get_army(country, army_id)
    city = next((city for city in get_cities(player, 0) if city["_id"] == army["city_id"]), None)
    db.players.update_one({"tg_id":user.id, "countries.id":0},
                          {"$push":{
                                "countries.$.campaigns":{
                                    "started": player["step"],
                                    "cost": cost,
                                    "army":army
                                },
                                "actions":f"Армия '{army['name']}' типа {get_army_type(army)['title']}, размещённая в городе {city['name']}, "
                                          f"отправилась в исследовательскую экспедицию. Стоимость экспедиции составила {cost} монет."
                          },
                          "$pull":{
                                "countries.$.armies":army
                          },
                          "$inc":{"countries.$.money":-cost}})