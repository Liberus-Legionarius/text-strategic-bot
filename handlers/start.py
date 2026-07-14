import  telebot as tg
from bot import bot, db

start_text = "Приветствую тебя, {}, в текстовой стратегии \"Новый Рассвет\"!\n\nЧтобы мы могли начать, тебе нужно придумать название страны.\nНазвание должно начинаться с большой буквы, а если в названии несколько слов, то каждое слово тоже начинается с большой буквы."

@bot.message_handler(commands=['start'])
def start(message):
    players = db.players
    user = players.find_one({"tg_id": message.from_user.id})
    if user and user.get("country") and user.get("capital"):
        bot.send_message(message.chat.id, f"Добро пожаловать обратно, {message.from_user.first_name}!\nЖелаете продолжить?")
    else:
        bot.send_message(message.chat.id, start_text.format(message.from_user.first_name))
        players.update_one({"tg_id": message.from_user.id}, {"$set":{"bot_state": "INIT_COUNTRYNAME"}}) if user else players.insert_one({"tg_id": message.from_user.id, "bot_state": "INIT_COUNTRYNAME"})
