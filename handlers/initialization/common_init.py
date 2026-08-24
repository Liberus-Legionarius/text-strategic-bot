from services.bot import bot, db
import re

PATTERN_UPPERCASE = r"^([А-ЯЁ][а-яё]+(?:[\s|-][А-ЯЁ][а-яё]+)*)"

def check_format(pattern, str, chat_id, message_id):
    if re.match(pattern, str):
        bot.edit_message_text(
            "Формат верный, сейчас проверю, насколько название приемлемое. Минуточку...",
            chat_id=chat_id,
            message_id=message_id
        )
        return True
    else:
        bot.edit_message_text(
            "Хм... Что-то здесь не так... Убедитесь, что каждое слово написано с большой буквы и нет цифр.",
            chat_id =chat_id,
            message_id = message_id
        )
        return False

def name_handler(ai_check, chat_id, message_id, placeholder):
    if ai_check.get("response"):
        bot.edit_message_text(
            f"Хорошо, {placeholder} принято, можем продолжать.",
            chat_id = chat_id,
            message_id = message_id
        )
        return True
    elif ai_check.get("refusal_code") == "OBSCENE_LANGUAGE":
        bot.edit_message_text(
            f"Кхм... Как некультурно. Подберите {placeholder} без нецензурной брани.",
            chat_id=chat_id,
            message_id=message_id
        )
        return False
    elif ai_check.get("refusal_code") == "MAKES_NO_SENSE":
        bot.edit_message_text(
            f"Придумайте другое {placeholder}, которое не будет представлять из себя случайный набор букв.",
            chat_id=chat_id,
            message_id=message_id
        )
        return False
    elif ai_check.get("refusal_code") == "GEOGRAPHICAL_INCONSISTENCY":
        bot.edit_message_text(
            f"Вы уверены, что с географической точки зрения ваше {placeholder} имеет смысл?\n"
            f"Придумайте другое {placeholder}.",
            chat_id=chat_id,
            message_id=message_id
        )
        return False
    elif ai_check.get("refusal_code") == "NAME_IS_NOT_SHORT":
        bot.edit_message_text(
            f"Хм... Кажется, ваше {placeholder} нельзя назвать коротким.\n"
            f"Придумайте другое {placeholder}, которое не будет содержать намёков на государственный строй или идеологию.",
            chat_id=chat_id,
            message_id=message_id
        )
        return False
    else:
        bot.edit_message_text(
            f"Я затрудняюсь определить ошибку, которую вы допустили... \n"
            f"Пожалуйста, придумайте другое {placeholder}.",
            chat_id=chat_id,
            message_id=message_id
        )
        return False

def set_details(tg_id, ideology, ideology_type, goals, ultimate_goal, territorial_ambitions, characteristics):
    db.players.update_one({"tg_id": tg_id, "countries.id":0}, {
        "$set": {
            "countries.$.ideology_desc": ideology,
            "countries.$.ideology_type": ideology_type,
            "countries.$.goals": goals,
            "countries.$.ultimate_goal": ultimate_goal,
            "countries.$.completed_goals": [],
            "countries.$.territorial_ambitions": territorial_ambitions,
            "countries.$.country_characteristics": characteristics,
            "bot_state": "IN_GAME"
        }
    })