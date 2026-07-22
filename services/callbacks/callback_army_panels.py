from bot import bot, db
from ingame_logic.army_panel import open_army_panel, open_mobilization_panel
from constants import MOBILIZATION_LAWS, get_player
from bson import ObjectId

@bot.callback_query_handler(func= lambda call: call.data.startswith("army"))
def callback_army(call):
    bot.answer_callback_query(call.id)
    panel = call.data.split(":")[1]
    if panel == "base":
        open_army_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panel == "mobilization":
        law = ObjectId(call.data.split(":")[2])
        player = get_player(call.from_user)
        if law in MOBILIZATION_LAWS.keys() and not law == player["mobilization_laws"]:
            db.players.update_one({"tg_id":call.from_user.id},
                                  {"$set":{"mobilization_laws":law}})
            open_mobilization_panel(call.from_user, call.message.chat.id, call.message.message_id)
        elif call.data.split(":")[2] == "open":
            open_mobilization_panel(call.from_user, call.message.chat.id, call.message.message_id)
    elif panel == "armies":
        pass