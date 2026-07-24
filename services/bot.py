import telebot as tg
from pymongo import MongoClient
from config import TELEBOT_APIKEY, MONGODB_CONNECTION

bot = tg.TeleBot(TELEBOT_APIKEY)
client = MongoClient(MONGODB_CONNECTION)
db = client.strategic_textgame