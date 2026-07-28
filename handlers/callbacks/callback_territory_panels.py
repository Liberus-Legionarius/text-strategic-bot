from handlers.ingame_panels.territory_panel import *

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
                db.players.update_one(
                    {"tg_id":call.from_user.id, "cities.city_id":int(city_id)},
                    {"$inc":{
                        "cities.$.population": -500, "money": 250
                    }}
                )
                open_one_city_panel(call.from_user, call.message.chat.id, call.message.message_id, city_id)
    elif panel == "build":
        b_id = call.data.split(":")[2]
        city_id = db.players.find_one({'tg_id': call.from_user.id})["selected_city"]
        player = get_player(call.from_user)
        if BUILDINGS[b_id]["cost"] <= player["money"]:
            city = next((city for city in player["cities"] if str(city["city_id"]) == city_id), None)
            has_b = next((b for b in city["buildings"] if str(b["id"]) == b_id), None)
            if not has_b:
                db.players.update_one(
                    {"tg_id": call.from_user.id, "cities.city_id": int(city_id)},
                    {"$inc": {
                        "money": -BUILDINGS[b_id]["cost"]
                    },
                    "$push": {
                        "cities.$.buildings": {"id": b_id, "amount": 1}
                    }})
                open_buildings_panel(call.from_user, call.message.chat.id, call.message.message_id, city_id)


def change_pops_invest(user, change):
    db.players.update_one({
        "tg_id":user.id, "national_spirits.id":3
    },
    {"$inc":{
        "national_spirits.$.population_growth_invest":change,
        "national_spirits.$.stability":change/2
    }})