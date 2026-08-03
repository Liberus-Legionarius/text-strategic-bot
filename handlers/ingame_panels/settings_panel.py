from services.bot import db, bot
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from services.constants import get_player

SETTINGS_KB = InlineKeyboardMarkup(row_width = 1)
SETTINGS_KB.add(InlineKeyboardButton("Изменить ключ API", callback_data = "settings:change_api_key"),
                InlineKeyboardButton("Вернуться", callback_data = "state:open"))

def open_settings_panel(user, chat_id, message_id):
    player = get_player(user)
    text = ("Текущие настройки:\n"
            f"- Ключ API: {player['api_key']}\n"
            f"- Размер мира: {player['world_size']}")

    bot.edit_message_text(
        text,
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = SETTINGS_KB
    )