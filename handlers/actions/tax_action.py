from services.bot import db

def change_tax_rate(player, country_id, value):
    db.players.update_one({"tg_id": player["tg_id"], "countries.id": country_id},
                          {"$inc": {
                              "countries.$.national_spirits.1.stability": -value/2,
                              "countries.$.national_spirits.1.tax_rate": value}
                          })