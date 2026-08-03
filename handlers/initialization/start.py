from services.bot import bot, db
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

start_text = "Приветствую тебя, {}, в текстовой стратегии \"Новый Рассвет\"!\n\nЧтобы мы могли начать, тебе нужно указать свой API-ключ для Gemini.\nЕсли указан неправильный ключ, просто введи команду /start и напиши ещё раз."
yes_no_kb = InlineKeyboardMarkup()
yes_no_kb.add(InlineKeyboardButton("Да", callback_data ="start:yes"), InlineKeyboardButton("Нет", callback_data ='start:no'))

@bot.message_handler(commands=['start'])
def start(message):
    players = db.players
    user = players.find_one({"tg_id": message.from_user.id})
    if user and user.get("bot_state") == "IN_GAME":
        bot.send_message(message.chat.id, f"Добро пожаловать обратно, {message.from_user.first_name}!\nЖелаете продолжить?", reply_markup=yes_no_kb)
    else:
        new_start(message.chat.id, message.from_user)

def new_start(chat_id, user):
    bot.send_message(chat_id, start_text.format(user.first_name))
    if db.players.find_one({"tg_id":user.id}):
        db.players.delete_one({"tg_id":user.id})
        db.cities.delete_many({"player_id":user.id})
    db.players.insert_one({"tg_id": user.id, "bot_state": "INIT_KEYAPI"})