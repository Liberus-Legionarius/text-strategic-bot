from services.bot import db

def change_stability_growth(player, country_id, value):
    db.players.update_one({"tg_id": player["tg_id"], "countries.id": country_id},
                          {"$inc": {
                              "countries.$.national_spirits.5.stability_invest": value
                          }})