from handlers.initialization.capital_init import check_capital
from services.bot import db, bot
from handlers.ingame_panels.state_initialization import init_state
from handlers.ingame_panels.state_panel import open_state_panel
from services.constants import get_player
from services.math.territory_math import get_city_by_id


@bot.callback_query_handler(func=lambda call: call.data.startswith("init"))
def callback_init(call):
    bot.answer_callback_query(call.id)
    # Начало игры.
    if call.data.startswith("init:enter"):
        init_state(call.from_user)
        open_state_panel(call.from_user, call.message.chat.id, call.message.message_id)
    # Инициализация деталей.
    elif call.data == "init:country:no":
        db.players.update_one({"tg_id":call.from_user.id},
                              {"$set":{
                                  "ideology_desc": None,
                                  "goals": None,
                                  "territorial_ambitions": None,
                                  "bot_state":"INIT_DETAILS"
                              }})
        bot.edit_message_text(
            "Тогда напишите о своём государстве. Обязательно опишите идеологию в подробностях, перечислите цели вашего государства (первоначальные) и ваши территориальные амбиции.",
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            reply_markup = None
        )
    elif call.data.startswith("init:capital"):
        player = get_player(call.from_user.id)
        check_capital(player, get_city_by_id(player, call.data.split(":")[2]), call.message.chat.id)
