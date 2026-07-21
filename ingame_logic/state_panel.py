from bot import db, bot
import services.ai as ai
from services.territory_math import get_total_population
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from constants import get_date_move, get_player

PANELS_KB =InlineKeyboardMarkup()
PANELS_KB.add(InlineKeyboardButton("Экономика", callback_data="economy:base:open"), InlineKeyboardButton("Армия", callback_data="army:base:open"),
              InlineKeyboardButton("Дипломатия", callback_data="diplomacy:base:open"), InlineKeyboardButton("Территории", callback_data = "territory:base:open"),
              InlineKeyboardButton("Завершить ход", callback_data="end_move"))

def open_state_panel(chat_id, user, message_id = None):
    player = get_player(user)

    total_population = get_total_population(player)
    if not player.get('ai_plot'):
        ai_response = ai.write_step_plot(player, total_population)
        ai_plot = ai_response['response']
        db.players.update_one({"tg_id":user.id},
                              {"$set":{"ai_plot":ai_plot}})
    else: ai_plot = player["ai_plot"]
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"{player['full_countryname']}\n"
            f"Столица: {player['capital']}"
            "\n\n"
            f"{ai_plot}"
            "\n\n"
            f"Стабильность: {player['stability']*100:.2f}%\n"
            f"Милитаризация: {player['militarization']*100:.2f}%\n"
            f"Общее население: {total_population}\n"
            f"Политическая власть: {player['polit_power']}\n"
            f"Очки инициативы: {player['initiative_point']:.2f}")
    bot.send_message(chat_id,text, reply_markup=PANELS_KB) if not message_id else bot.edit_message_text(text, chat_id = chat_id, message_id = message_id, reply_markup = PANELS_KB)
