from services.bot import bot
from services.constants import get_player

# Запрет отправки лишних сообщений в ходе игры.
@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "IN_GAME")
def messages_forbidden(message):
    bot.delete_message(message.chat.id, message.message_id)