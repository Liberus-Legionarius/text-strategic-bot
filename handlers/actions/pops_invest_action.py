from services.bot import db

def change_pops_invest(player, country_id, value):
    db.players.update_one({"tg_id": player["tg_id"], "countries.id": country_id},
        {"$inc": {
            "countries.$.national_spirits.3.population_growth_invest": value,
            "countries.$.national_spirits.3.stability": value / 2
        }})