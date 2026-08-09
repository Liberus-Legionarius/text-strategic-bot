from services.bot import db

def reset_national_spirit(player, country_id, spirit_id, new_data):
    db.players.update_one({"tg_id":player["tg_id"], "countries.id":country_id},
                          {
                              "$set":{
                                  f"countries.$.national_spirits.{spirit_id}": new_data
                              }
                          })