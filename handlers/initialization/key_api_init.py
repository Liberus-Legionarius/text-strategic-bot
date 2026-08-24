from services.ai import check_api_key
from services.bot import bot, db
from services.constants import get_player

@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_KEYAPI")
def api_key_init(message):
    player = get_player(message.from_user)
    if check_api_key(message.text):
        db.players.update_one({"tg_id": message.from_user.id},
                              {
                                  "$set":{"bot_state":"INIT_WORLD_SIZE", "api_key":message.text}
                              })
        bot.edit_message_text(
            "Хорошо, теперь нужно определить размер мира...\n"
            "Знаю, странно звучит, но это способ ограничить появление сотен лишних стран.\n"
            "А какое количество считается нормальным? 100-200 стран будет предостаточно.\n",
            chat_id = message.chat.id,
            message_id = player["last_message"])
    else:
        bot.edit_message_text(
            "Хм... Что-то пошло не так.\n"
            "Проверьте ввод ещё раз, возможно, вы указали неправильный ключ API.",
            chat_id=message.chat.id,
            message_id = player["last_message"])
    bot.delete_message(message.chat.id, message.message_id)