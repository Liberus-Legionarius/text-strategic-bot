from services.bot import bot
import re
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

PATTERN_UPPERCASE = r"^([А-ЯЁ][а-яё]+(?:[\s|-][А-ЯЁ][а-яё]+)*)"

start_kb = InlineKeyboardMarkup()
start_kb.add(InlineKeyboardButton("Да начнётся игра!", callback_data="init:enter"))

def check_format(pattern, str, id):
    if re.match(pattern, str):
        bot.send_message(id, "Формат верный, сейчас проверю, насколько название приемлемое. Минуточку...")
        return True
    else:
        bot.send_message(id, "Хм... Что-то здесь не так... Убедитесь, что каждое слово написано с большой буквы и нет цифр.")
        return False

def name_handler(ai_check, id, placeholder):
    if ai_check.get("response"):
        bot.send_message(id, f"Хорошо, {placeholder} принято, можем продолжать.")
        return True
    elif ai_check.get("refusal_code") == "OBSCENE_LANGUAGE":
        bot.send_message(id, f"Кхм... Как некультурно. Подберите {placeholder} без нецензурной брани.")
        return False
    elif ai_check.get("refusal_code") == "MAKES_NO_SENSE":
        bot.send_message(id, f"Придумайте другое {placeholder}, которое не будет представлять из себя случайный набор букв.")
        return False
    elif ai_check.get("refusal_code") == "GEOGRAPHICAL_INCONSISTENCY":
        bot.send_message(id, f"Вы уверены, что с географической точки зрения написали {placeholder}, имеющее смысл?\nПридумайте другое {placeholder}.")
    else:
        bot.send_message(id, f"Я затрудняюсь определить ошибку, которую вы допустили... Пожалуйста, придумайте другое {placeholder}.\n{ai_check.get('refusal_code')}")
        return False