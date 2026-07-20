import services.ai as ai
from bot import db, bot

number_to_month = {
    1:"Январь",
    2:"Февраль",
    3:"Март",
    4:"Апрель",
    5:"Май",
    6:"Июнь",
    7:"Июль",
    8:"Август",
    9:"Сентябрь",
    10:"Октябрь",
    11:"Ноябрь",
    12:"Декабрь"
}

def open_state_panel(chat_id, user, message_id = None):
    player = db.players.find_one({"tg_id":user.id})

    total_population = sum(
        city["population"]
        for city in player["cities"]
    )
    text = (f"{number_to_month[player['date'].month]}, год {player['date'].year} - шаг {player['step']}"
            "\n\n"
            f"{player['full_countryname']}\n"
            f"Столица: {player['capital']}"
            "\n\n"
            f"{ai.write_step_plot(player, total_population)['response']}"
            "\n\n"
            f"Стабильность: {player['stability']*100:.2f}%\n"
            f"Милитаризация: {player['militarization']*100:.2f}%\n"
            f"Общее население: {total_population}\n"
            f"Политическая власть: {player['polit_power']}\n"
            f"Очки инициативы: {player['initiative_point']:.2f}")
    bot.send_message(chat_id,text) if not message_id else bot.edit_message_text(text, chat_id = chat_id, message_id = message_id, reply_markup = None)