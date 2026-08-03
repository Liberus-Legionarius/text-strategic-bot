from services.bot import db, bot
import services.ai as ai
from services.math.economy_math import get_total_income, get_total_spending
from services.math.territory_math import get_total_population
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from services.constants import get_date_move, get_player, get_modifier, get_city_name

PANELS_KB =InlineKeyboardMarkup()
PANELS_KB.row(InlineKeyboardButton("Экономика", callback_data="economy:base:open"),
              InlineKeyboardButton("Территории", callback_data = "territory:base:open"))
PANELS_KB.row(InlineKeyboardButton("Армия", callback_data="army:base:open"),
              InlineKeyboardButton("Дипломатия", callback_data="diplomacy:base:open"))
PANELS_KB.row(InlineKeyboardButton("Дневник", callback_data="diary:base:open"))
PANELS_KB.row(InlineKeyboardButton("Переименовать страну", callback_data="state:rename"))
PANELS_KB.row(InlineKeyboardButton("Настройки", callback_data="settings:open"))
PANELS_KB.row(InlineKeyboardButton("Завершить ход", callback_data="end_move"))

def open_state_panel(user, chat_id, message_id = None):
    player = get_player(user)

    total_population = get_total_population(player, 0)
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

    player_country = player["countries"][0]
    text = (f"{get_date_move(player)}"
            "\n\n"
            f"{player_country['full_countryname']}\n"
            f"Столица: {get_city_name(player_country['capital'])}"
            "\n\n"
            f"{ai_plot}"
            "\n\n"
            f"Стабильность: {get_modifier(player_country, 'stability')*100:.2f}%\n"
            f"Милитаризация: {get_modifier(player_country, 'militarization')*100:.2f}%\n"
            f"Общее население: {total_population:.0f}\n"
            f"Политическая власть: {player_country['polit_power']:.0f}\n"
            f"Казна: {player_country['money']:.2f} монет\n"
            f"Баланс в следующем ходу: {get_total_income(player, player_country) - get_total_spending(player, player_country):.2f}")
    bot.send_message(chat_id,text, reply_markup=PANELS_KB) if not message_id else bot.edit_message_text(text, chat_id = chat_id, message_id = message_id, reply_markup = PANELS_KB)
