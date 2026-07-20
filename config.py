from dotenv import load_dotenv
import os

load_dotenv()

TELEBOT_APIKEY = os.getenv("TELEBOT_APIKEY")
GEMINI_APIKEY = os.getenv("GEMINI_APIKEY")
MONGODB_CONNECTION = os.getenv("MONGODB_CONNECTION")