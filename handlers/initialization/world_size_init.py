from services.bot import bot, db
from services.constants import get_player
from services.map.map_management import province_map


@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_WORLD_SIZE")
def world_size_init(message):
    player = get_player(message.from_user)
    try:
        if message.text.isdigit():
            if len(province_map) >= int(message.text) >= 20:
                db.players.update_one({"tg_id": message.from_user.id},
                                      {
                                          "$set":{"bot_state":"INIT_COUNTRYNAME", "world_size":int(message.text)}
                                      })
                bot.edit_message_text(
                    "Теперь перейдём к инициализации страны.\n"
                    "Для начала нужно ввести короткое название страны (без 'Республика', 'Империя' и прочих уточнений).\n"
                    "К слову, название должно начинаться с большой буквы.",
                    chat_id = message.chat.id,
                    message_id = player["last_message"]
                )
            elif int(message.text) >len(province_map):
                bot.edit_message_text(
                    "Кажется, выбранное вами количество стран больше количества провинций на карте.\n"
                    f"Введите число, которое будет меньше, чем {len(province_map)}.",
                    chat_id=message.chat.id,
                    message_id=player["last_message"]
                )
            elif int(message.text) < 20:
                bot.edit_message_text(
                    "Кажется, выбранное вами количество стран меньше минимально возможных 20 стран на старте.\n"
                    f"Введите число, которое будет больше двадцати.",
                    chat_id=message.chat.id,
                    message_id=player["last_message"]
                )
        else:
            bot.edit_message_text(
                "Вы уверены, что ввели целое положительное число?\n"
                "Попробуйте ещё раз.",
                chat_id=message.chat.id,
                message_id=player["last_message"]
            )
    except Exception as e:
        print(e)
    bot.delete_message(message.chat.id, message.message_id)