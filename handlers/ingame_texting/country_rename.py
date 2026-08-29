from services.bot import bot, db
from services.constants import get_player, get_country
import services.ai as ai
from services.math.territory_math import get_cities, get_city_by_id
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

BACK_KB = InlineKeyboardMarkup()
BACK_KB.add(InlineKeyboardButton("Вернуться", callback_data = "state:open"))

@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "COUNTRY_RENAME_SHORT")
def country_short_renaming(message):
    player = get_player(message.from_user)
    player_country = get_country(player, 0)
    cities = [city["name"] for city in get_cities(player, 0)]
    capital = get_city_by_id(player, player_country["capital"])["name"]
    ai_response = ai.check_country_short_renaming(player_country["countryname"], cities, capital, message.text, player["api_key"])
    if not ai_response["response"] and player_country["countryname"] == message.text:
        bot.edit_message_text(
            "Введено некорректное название.\n"
            "Причина отклонения запроса:\n"
            f"{ai_response['refusal_desc']}",
            chat_id = message.chat.id,
            message_id = player["last_message"],
            reply_markup = BACK_KB
        )
    else:
        bot.edit_message_text(
            "Короткое название принято.\n"
            "Теперь введите длинное название вашей страны, опять же, учитывая выбранную идеологию.",
            chat_id=message.chat.id,
            message_id=player["last_message"],
            reply_markup = BACK_KB
        )
        db.players.update_one({"tg_id":player["tg_id"]},
                              {
                                  "$set":{
                                      "bot_state":"COUNTRY_RENAME_LONG",
                                      "countries.0.countryname":message.text
                                  }
                              })
    bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(func = lambda msg: get_player(msg.from_user).get("bot_state") == "COUNTRY_RENAME_LONG")
def country_long_renaming(message):
    player = get_player(message.from_user)
    player_country = get_country(player, 0)
    cities = [city["name"] for city in get_cities(player, 0)]
    capital = get_city_by_id(player, player_country["capital"])["name"]
    ai_response = ai.check_country_long_renaming(player_country["countryname"], player_country["full_countryname"],
                                                 player_country["country_characteristics"], player_country["ideology"],
                                                 player_country["ideology_desc"], cities, capital, message.text, player["api_key"])
    if not ai_response["response"]:
        bot.edit_message_text(
            "Введено некорректное название.\n"
            "Причина отклонения запроса:\n"
            f"{ai_response['refusal_desc']}",
            chat_id=message.chat.id,
            message_id=player["last_message"],
            reply_markup = BACK_KB
        )
    else:
        bot.edit_message_text(
            "Название изменено.\n"
            "Можете возвращаться обратно.",
            chat_id=message.chat.id,
            message_id=player["last_message"],
            reply_markup = BACK_KB
        )
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$set": {
                                      "bot_state": "IN_GAME",
                                      "countries.0.full_countryname": message.text
                                  }
                              })
    bot.delete_message(message.chat.id, message.message_id)