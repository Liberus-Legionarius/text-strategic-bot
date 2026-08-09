from handlers.actions.conscript_army_action import conscript_army
from handlers.actions.reorganize_amy_action import reorganize_army
from handlers.ingame_panels.territory_panel import open_one_city_panel
from services.bot import bot, db
from handlers.ingame_panels.army_panel import open_army_panel, open_mobilization_panel, open_armies_panel, \
    open_one_army_panel, open_campaign_panel, open_delete_confirmation, open_army_reorganize, \
    open_army_reorganize_unit_info, open_army_creation_panel, open_province_selection_panel
from services.math.army_math import get_army, get_reorganization_cost, get_manpower
from services.constants import MOBILIZATION_LAWS, get_player, get_country, ARMY_TYPES, get_is_pacifism
from bson import ObjectId
from services.math.army_math import get_army_type
from services.math.territory_math import get_cities, change_population


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
            pp = country["polit_power"]
            if law in MOBILIZATION_LAWS.keys() and not law == country["national_spirits"][2]["_id"] and pp >= 150:
                to_add = MOBILIZATION_LAWS[law]
                to_add.update({"id":2, "name":"Политика призыва", "_id": call.data.split(":")[2]})
                db.players.update_one({"tg_id":call.from_user.id, "countries.id":0},
                                      {"$set":{"countries.$.national_spirits.2":to_add},
                                       "$inc":{"countries.$.polit_power":-150}})
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
                        cost = get_army_type(army)["cost"]*army["size"]*(army["hp"]/get_army_type(army)["hp"])/2
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
                        change_population(player, 0, to_inc)
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
                            reorganize_army(get_player(call.from_user), 0, army["army_id"], army_type["_id"])
                        open_one_army_panel(call.from_user, call.message.chat.id, call.message.message_id, panel)
                else:
                    open_army_reorganize(call.from_user, call.message.chat.id, call.message.message_id, panel)
            elif datas[3] == "move":
                pass
    elif panel == "campaign":
        datas = call.data.split(":")
        if len(datas) < 4:
            open_province_selection_panel(call.from_user, call.message.chat.id, call.message.message_id, datas[2])
        elif len(datas) < 5:
            open_campaign_panel(call.from_user, call.message.chat.id, call.message.message_id, datas[2], datas[3])
        else:
            if get_country(get_player(call.from_user), 0)["money"] >= int(datas[4]):
                start_campaign(call.from_user, datas[2], datas[3], int(datas[4]))
                open_armies_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panel == "create":
        datas = call.data.split(":")
        player = get_player(call.from_user)
        country = get_country(player, 0)
        if get_is_pacifism(country):
            return
        if get_manpower(player, country) >= 100:
            if len(datas) == 4:
                conscript_army(player, country, datas[3])
                open_one_city_panel(call.from_user, call.message.chat.id, call.message.message_id, datas[2])
            else:
                open_army_creation_panel(call.from_user, call.message.chat.id, call.message.message_id, datas[2])

def start_campaign(user, army_id, province, cost):
    player = get_player(user)
    country = get_country(player, 0)
    army = get_army(country, army_id)
    prov = next(p for p in player["province_map"] if p["name"] == province)
    db.players.update_one({"tg_id":user.id, "countries.id":0},
                          {"$push":{
                                "countries.$.campaigns":{
                                    "cost": cost,
                                    "army":army,
                                    "province":prov
                                }
                          },
                          "$pull":{
                                "countries.$.armies":army
                          },
                          "$inc":{"countries.$.money":-cost}})