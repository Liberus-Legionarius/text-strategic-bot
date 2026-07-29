from handlers.ingame_panels.territory_panel import *
from bson import ObjectId

@bot.callback_query_handler(func= lambda call: call.data.startswith("territory:"))
def callback_territory(call):
    bot.answer_callback_query(call.id)
    panel = call.data.split(":")[1]
    if panel == "base":
        open_territory_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panel == "pops":
        if call.data.endswith("down5"):
            change_pops_invest(call.from_user, -0.05)
        elif call.data.endswith("down2"):
            change_pops_invest(call.from_user, -0.02)
        elif call.data.endswith("down1"):
            change_pops_invest(call.from_user, -0.01)
        elif call.data.endswith("rise1"):
            change_pops_invest(call.from_user, 0.01)
        elif call.data.endswith("rise2"):
            change_pops_invest(call.from_user, 0.02)
        elif call.data.endswith("rise5"):
            change_pops_invest(call.from_user, 0.05)
        open_pops_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panel == "cities":
        city = call.data.split(":")[2]
        if not (city == "open" or city == "city"):
            open_one_city_panel(call.from_user, call.message.chat.id, call.message.message_id, city)
        elif city == "open":
            open_cities_panel(call.from_user, call.message.chat.id, call.message.message_id)
        elif city == "city":
            option = call.data.split(":")[3]
            city_id = db.players.find_one({'tg_id':call.from_user.id})["selected_city"]
            if option == "build":
                open_buildings_panel(call.from_user, call.message.chat.id, call.message.message_id, city_id)
            elif option == "raze":
                population = db.cities.find_one({"_id":ObjectId(city_id)})["population"]
                db.cities.update_one(
                    {"_id":ObjectId(city_id)},
                    {"$inc":{
                        "population": int(-population/100)
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
                open_one_city_panel(call.from_user, call.message.chat.id, call.message.message_id, city_id)
    elif panel == "build":
        b_id = call.data.split(":")[2]
        city_id = db.players.find_one({'tg_id': call.from_user.id})["selected_city"]
        player = get_player(call.from_user)
        if BUILDINGS[b_id]["cost"] <= get_country(player, 0)["money"]:
            city = next((city for city in get_cities(player, 0) if str(city["_id"]) == city_id), None)
            has_b = next((b for b in city["buildings"] if str(b["id"]) == b_id), None)
            if not has_b:
                db.cities.update_one(
                    {"_id": ObjectId(city_id) },
                    {"$push": {
                        "buildings": {"id": b_id, "amount": 1}
                    }})
                db.players.update_one(
                    {"tg_id":player["tg_id"], "countries.id":0},
                    {
                        "$inc":{
                            "countries.$.money": -BUILDINGS[b_id]["cost"]
                        }
                    }
                )
                open_buildings_panel(call.from_user, call.message.chat.id, call.message.message_id, city_id)


def change_pops_invest(user, change):
    db.players.update_one({
        "tg_id":user.id, "countries.id":0
    },
    {"$inc":{
        "countries.$.national_spirits.3.population_growth_invest":change,
        "countries.$.national_spirits.3.stability":change/2
    }})