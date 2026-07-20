from bot import bot, db
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from ingame_logic.state_initialization import init_state
from ingame_logic.state_panel import open_state_panel

start_text = "Приветствую тебя, {}, в текстовой стратегии \"Новый Рассвет\"!\n\nЧтобы мы могли начать, тебе нужно придумать название страны.\nНазвание должно начинаться с большой буквы, а если в названии несколько слов, то каждое слово тоже начинается с большой буквы."
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
    db.players.update_one({"tg_id": user.id},
                        {"$set": {"bot_state": "INIT_COUNTRYNAME"}}) if db.players.find_one({"tg_id": user.id}) \
                        else db.players.insert_one(
                        {"tg_id": user.id, "bot_state": "INIT_COUNTRYNAME"})

@bot.callback_query_handler(func = lambda call: call.data.startswith("start:"))
def callback(call):
    if call.data == "start:yes":
        if not db.players.find_one({"tg_id":call.from_user.id}).get("money"):
            init_state(call.from_user)
        open_state_panel(call.message.chat.id, call.from_user)
    else:
        new_start(call.message.chat.id, call.from_user)
        bot.edit_message_text(
            "Ваш предыдущий прогресс очищен.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
