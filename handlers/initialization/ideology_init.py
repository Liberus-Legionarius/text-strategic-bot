from services.bot import bot, db
from services.constants import get_player

# Выбор государственной идеологии, фактически запрет на отправку сообщений.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "INIT_IDEOLOGY")
def ideology_init(message):
    bot.delete_message(message.chat.id, message.id)
    bot.send_message(message.chat.id,
                     "Вы не выбрали государственный режим, пожалуйста, нажмите на один из предложенных вариантов.")