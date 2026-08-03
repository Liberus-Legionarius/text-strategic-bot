from services.bot import bot, db
from services.constants import get_player

@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_KEYAPI")
def api_key_init(message):
    db.players.update_one({"tg_id": message.from_user.id},
                          {
                              "$set":{"bot_state":"INIT_WORLD_SIZE", "api_key":message.text}
                          })
    bot.send_message(message.chat.id, "Хорошо, теперь нужно определить размер мира...\n"
                                      "Знаю, странно звучит, но это способ ограничить появление сотен лишних стран.\n"
                                      "А какое количество считается нормальным? 100-200 стран будет предостаточно.\n"
                                      "Учитывайте, что вы вводите максимальное единовременное количество стран, при этом всего может быть до пяти раз больше стран.")