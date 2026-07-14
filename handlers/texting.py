import telebot as tg
import re
from bot import bot, db

@bot.message_handler(func = lambda msg: True)
def texting(message):
    user = db.players.find_one({"tg_id":message.from_user.id})
    state = user.get("bot_state")
    if state in ["INIT_COUNTRYNAME", "INIT_CAPITAL"]:
        pattern = r"^([А-ЯЁ][а-яё]+(?:\s[А-ЯЁ][а-яё]+)*)"
        if re.match(pattern, message.text):
            bot.send_message(message.chat.id, "Название принято.")
            if state == "INIT_COUNTRYNAME":
                bot.send_message(message.chat.id, "Теперь введите название столицы.")
                db.players.update_one({"tg_id": message.from_user.id},
                                      {"$set": {"bot_state": "INIT_CAPITAL", "country": message.text}})
            else:
                bot.send_message(message.chat.id, "Замечательно, настройка завершена.\nСейчас я инициализирую базовые показатели страны и напишу тебе отчёт о положении дел.")
                db.players.update_one({"tg_id": message.from_user.id},
                                      {"$set": {"bot_state": "PLAYING", "capital": message.text}})
        else:
            bot.send_message(message.chat.id, "Хм... Что-то здесь не так... Убедитесь, что каждое слово написано с большой буквы и нет цифр.")