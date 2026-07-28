from services.bot import db, bot
import services.ai as ai
from services.math.territory_math import get_total_population
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from services.constants import get_date_move, get_player, get_modifier

PANELS_KB =InlineKeyboardMarkup()
PANELS_KB.row(InlineKeyboardButton("Экономика", callback_data="economy:base:open"),
              InlineKeyboardButton("Территории", callback_data = "territory:base:open"))
PANELS_KB.row(InlineKeyboardButton("Армия", callback_data="army:base:open"),
              InlineKeyboardButton("Дипломатия", callback_data="diplomacy:base:open"))
PANELS_KB.row(InlineKeyboardButton("Дневник", callback_data="diary:base:open"))
PANELS_KB.row(InlineKeyboardButton("Дополнительно...", callback_data="state:extra:open"),
              InlineKeyboardButton("Настройки", callback_data="settings:open"))
PANELS_KB.row(InlineKeyboardButton("Завершить ход", callback_data="end_move"))

def open_state_panel(user, chat_id, message_id = None):
    player = get_player(user)

    total_population = get_total_population(player)
    if player["step"] == 1 and not player["ai_plot"]:
        ai_response = ai.write_step_first(player)
        ai_plot = ai_response['response']
        db.players.update_one({"tg_id": user.id},
                              {"$set": {"ai_plot": ai_plot}})
    elif not player["ai_plot"]:
        ai_response = ai.write_step_plot(player)
        ai_plot = ai_response['response']
        if ai_response.get("short_report"):
            db.players.update_one({"tg_id": user.id},
                                  {"$set": {"ai_plot": ai_plot, "actions":[]},
                                   "$push": {"history":ai_response['short_report']}})
        else:
            db.players.update_one({"tg_id": user.id},
                                  {"$set": {"ai_plot": ai_plot}})
    else:
        ai_plot = player["ai_plot"]

    text = (f"{get_date_move(player)}"
            "\n\n"
            f"{player['full_countryname']}\n"
            f"Столица: {player['capital']}"
            "\n\n"
            f"{ai_plot}"
            "\n\n"
            f"Стабильность: {get_modifier(player, 'stability')*100:.2f}%\n"
            f"Милитаризация: {get_modifier(player, 'militarization')*100:.2f}%\n"
            f"Общее население: {total_population:.0f}\n"
            f"Политическая власть: {player['polit_power']:.0f}")
    bot.send_message(chat_id,text, reply_markup=PANELS_KB) if not message_id else bot.edit_message_text(text, chat_id = chat_id, message_id = message_id, reply_markup = PANELS_KB)
