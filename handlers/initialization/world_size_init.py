from services.bot import bot, db
from services.constants import get_player

@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_WORLD_SIZE")
def world_size_init(message):
    if message.text.isdigit():
        db.players.update_one({"tg_id": message.from_user.id},
                              {
                                  "$set":{"bot_state":"INIT_COUNTRYNAME", "world_size":int(message.text)}
                              })
        bot.send_message(message.chat.id, "Теперь перейдём к инициализации страны.\n"
                                          "Для начала нужно ввести короткое название страны (без 'Республика', 'Империя' и прочих уточнений).\n"
                                          "К слову, название должно начинаться с большой буквы.")
    else:
        bot.send_message(message.chat.id, "Вы уверены, что ввели целое положительное число?\n"
                                          "Попробуйте ещё раз.")