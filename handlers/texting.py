from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
import re
from bot import bot, db
import services.ai as ai
from ingame_logic.state_initialization import init_state
from  ingame_logic.state_panel import open_state_panel
from ingame_logic.economy_panel import open_loan_panel

PATTERN_UPPERCASE = r"^([А-ЯЁ][а-яё]+(?:[\s|-][А-ЯЁ][а-яё]+)*)"

start_kb = InlineKeyboardMarkup()
start_kb.add(InlineKeyboardButton("Да начнётся игра!", callback_data="ingame:start"))

@bot.message_handler(func = lambda msg: True)
def texting(message):
    user = db.players.find_one({"tg_id":message.from_user.id})
    state = user.get("bot_state")
    # Выбор короткого названия
    if state == "INIT_COUNTRYNAME" and check_format(PATTERN_UPPERCASE, message.text, message.chat.id):
        ai_check = ai.check_countryname(message.text)
        if name_handler(ai_check, message.chat.id, "название страны"):
            db.players.update_one({"tg_id": message.from_user.id},
                            {"$set": {"bot_state": "INIT_IDEOLOGY", "countryname": message.text}})
            government_type_options = InlineKeyboardMarkup()
            government_type_options.add(InlineKeyboardButton("Республика", callback_data = "Республика"), InlineKeyboardButton("Монархия", callback_data = "Монархия"))
            bot.send_message(message.chat.id, "Раз уж с названием определились, перейдём к форме государственного управления."
                                              "\nВыберите один из предложенных ниже вариантов:", reply_markup = government_type_options)
    # Выбор формы государства (запрет писать, если объективно).
    elif state == "INIT_IDEOLOGY":
        bot.delete_message(message.chat.id, message.id)
        bot.send_message(message.chat.id,
                         "Вы не выбрали государственный режим, пожалуйста, нажмите на один из предложенных вариантов.")
    # Выбор полного названия страны.
    elif state == "INIT_FULLNAME" and check_format(PATTERN_UPPERCASE, message.text, message.chat.id):
        ai_check = ai.check_fullname(message.text, user.get("countryname"), user.get("ideology"))
        if name_handler(ai_check, message.chat.id, "полное название страны"):
            bot.send_message(message.chat.id, "Отлично, теперь остаётся только выбрать столицу и регион вашей страны."
                                              "К слову, ваша столица в начале будет единственным городом, которым вы владеете.")
            db.players.update_one({"tg_id": message.from_user.id},
                                  {"$set": {"bot_state": "INIT_CAPITAL", "full_countryname": message.text}})
    # Выбор столицы.
    elif state == "INIT_CAPITAL" and check_format(PATTERN_UPPERCASE, message.text, message.chat.id):
        ai_check = ai.check_capital(message.text, user.get("countryname"))
        if name_handler(ai_check, message.chat.id, "название столицы"):
            db.players.update_one({"tg_id":message.from_user.id},
                                  {"$set": {"bot_state":"INIT_REGION", "capital": message.text}})
            if ai_check.get("region_name"):
                yes_no_kb = InlineKeyboardMarkup()
                yes_no_kb.add(InlineKeyboardButton("Да", callback_data=ai_check["region_name"]),
                              InlineKeyboardButton("Нет", callback_data='no'))
                bot.send_message(message.chat.id, "Хм... Мы посмотрели на ваш выбор..."
                                                  f"Скажите, вы хотите выбрать регион {ai_check.get('region_name')}?", reply_markup = yes_no_kb)
            else:
                bot.send_message(message.chat.id, "К сожалению, я не смог определить регион вашей столицы."
                                                  "Пожалуйста, введите название региона, но будьте благоразумны, не нужно переносить города в другие регионы, я это не люблю.")
                db.players.update_one({"tg_id": message.from_user.id},
                                      {"$set": {"bot_state": "INIT_REGION_RETRY"}})
    # Ожидание подтверждения региона.
    elif state == "INIT_REGION":
        bot.delete_message(message.chat.id, message.id)
        bot.send_message(message.chat.id,
                         "Пожалуйста, сначала ответьте, правильно ли я определил регион вашей столицы.")
    # Выбор региона (противный случай).
    elif state == "INIT_REGION_RETRY" and check_format(PATTERN_UPPERCASE, message.text, message.chat.id):
        ai_check = ai.check_region(user.get("countryname"), user.get("capital"), message.text)
        if name_handler(ai_check, message.chat.id, "название региона"):
            db.players.update_one({"tg_id": message.from_user.id},
                                  {"$set":{"bot_state":"IN_GAME", "region":message.text}})
            bot.send_message(message.chat.id, "Ну всё, инициализация завершена.", reply_markup=start_kb)
    # Взятие займа.
    elif state == "TAKE_LOAN":
        if float(message.text) >= 0:
            db.players.update_one({"tg_id": message.from_user.id},
                                  {"$inc":{"loans":float(message.text), "money":float(message.text)},
                                   "$set":{"bot_state":"IN_GAME"}})
            open_loan_panel(message.from_user, message.chat.id, user["last_message"])
        bot.delete_message(message.chat.id, message.message_id)
    # Выплата займа.
    elif state == "REPAY_LOAN":
        if float(message.text) >= 0:
            db.players.update_one({"tg_id": message.from_user.id},
                                  {"$inc":{"loans":-float(message.text), "money":-float(message.text)},
                                  "$set":{"bot_state":"IN_GAME"}})
            open_loan_panel(message.from_user, message.chat.id, user["last_message"])
        bot.delete_message(message.chat.id, message.message_id)


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

@bot.callback_query_handler(func=lambda call: not (call.data.startswith("start:") or call.data.startswith("ingame:") or call.data.endswith("open")))
def callback_init(call):
    user = db.players.find_one({"tg_id": call.from_user.id})
    # Когда игрок выбирает идеологию.
    if user.get("bot_state") == "INIT_IDEOLOGY":
        db.players.update_one({"tg_id":call.from_user.id}, {"$set":{"bot_state":"INIT_FULLNAME", "ideology":call.data}})
        bot.send_message(call.message.chat.id, "Раз уж с гос. режимом определились, давайте придумаем вашей стране полное название."
                                               "Чувствуйте себя свободно, только не пишите, например, '*** Империя', если у вас гос. режим Республика.")
        bot.edit_message_text(
            f"Выбрана идеология: {call.data}.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    # Когда подтверждается регион.
    elif user.get("bot_state") == "INIT_REGION":
        if not call.data == "no":
            db.players.update_one({"tg_id":call.from_user.id}, {"$set":{"bot_state":"IN_GAME", "region": call.data}})
            bot.send_message(call.message.chat.id, "На этом этап инициализации закончен.", reply_markup=start_kb)
            bot.edit_message_text(
                f"Вы подтвердили регион: {call.data}.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        else:
            db.players.update_one({"tg_id": call.from_user.id}, {"$set": {"bot_state": "INIT_REGION_RETRY", "region":None}})
            bot.edit_message_text(
                f"В таком случае напишите регион, в котором расположена ваша столица..."
                "\nТолько, пожалуйста, не нужно ставить Париж где-то в Галиции.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )

@bot.callback_query_handler(func= lambda call: call.data.startswith("ingame:"))
def callback_ingame(call):
    if call.data.startswith("ingame:start"):
        init_state(call.from_user)
        open_state_panel(call.message.chat.id, call.from_user, call.message)