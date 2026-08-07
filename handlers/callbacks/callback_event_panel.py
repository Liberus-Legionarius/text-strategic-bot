from services.bot import bot, db
from services.effects import on_effect
from handlers.callbacks.callback_end_move import on_move_effects
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

from services.constants import get_player, get_country


@bot.callback_query_handler(func = lambda call: call.data.startswith("event"))
def callback_event(call):
    bot.answer_callback_query(call.id)
    player = get_player(call.from_user)
    country = get_country(player, 0)

    option = player["event_options"][int(call.data.split(":")[1])]
    for effect, value in option["effects"].items():
        on_effect(effect, value, player, country)

    on_move_effects(player, call.from_user, call.message.chat.id, call.message.message_id)