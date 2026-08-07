from handlers.ingame_panels.territory_panel import *
from bson import ObjectId

@bot.callback_query_handler(func= lambda call: call.data.startswith("territory:"))
def callback_territory(call):
    bot.answer_callback_query(call.id)
    panel = call.data.split(":")[1]
    player = get_player(call.from_user)
    country = get_country(player,0)
    if panel == "base":
        open_territory_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panel == "cities":
        city = call.data.split(":")[2]
        if not city == "open" and len(call.data.split(":")) == 3:
            open_one_city_panel(call.from_user, call.message.chat.id, call.message.message_id, city)
        elif city == "open":
            open_cities_panel(call.from_user, call.message.chat.id, call.message.message_id)
        else:
            option = call.data.split(":")[3]
            if option == "b":
                open_buildings_panel(call.from_user, call.message.chat.id, call.message.message_id, city)
            elif option == "raze":
                population = get_city_by_name(player, city)["population"]
                db.players.update_one(
                    {"tg_id":player["tg_id"], "cities.name":city},
                    {"$inc":{
                        "cities.$.population": int(-population/100)
                    }}
                )
                db.players.update_one(
                    {"tg_id":call.from_user.id, "countries.id":0},
                    {
                        "$inc":{
                            "countries.$.money": int(population/200)
                        }
                    }
                )
                open_one_city_panel(call.from_user, call.message.chat.id, call.message.message_id, city)
            elif option == "capital":
                if country["money"] >= 125 and country["polit_power"] >= 50 and not country["capital"] == city:
                    db.players.update_one(
                        {"tg_id":call.from_user.id, "countries.id":0},
                        {
                            "$push":{
                                "actions":f"Столица перенесена в город {city}."
                            },
                            "$inc":{
                                "countries.$.money":-125,
                                "countries.$.polit_power":-50
                            },
                            "$set":{
                                "countries.$.capital": city
                            }
                        }
                    )
    elif panel == "b":
        b_id = call.data.split(":")[3]
        city_name = call.data.split(":")[2]
        player = get_player(call.from_user)
        if BUILDINGS[b_id]["cost"] <= get_country(player, 0)["money"]:
            city = get_city_by_name(player, city_name)
            build_in_city(player, city, b_id)
            open_buildings_panel(call.from_user, call.message.chat.id, call.message.message_id, city_name)


