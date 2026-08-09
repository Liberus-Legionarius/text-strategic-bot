from services.bot import db

def change_militarization_growth(player, country_id, value):
    db.players.update_one({"tg_id": player["tg_id"], "countries.id": country_id},
                          {"$inc": {
                              "countries.$.national_spirits.6.militarization_invest": value
                          }})