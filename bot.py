import telebot as tg
from pymongo import MongoClient

bot = tg.TeleBot("")
client = MongoClient("mongodb://localhost:27017/")
db = client.strategic_textgame