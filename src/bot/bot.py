import os
from dotenv import load_dotenv

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties 

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
env_path = os.path.join(parent_dir, ".env")

load_dotenv(env_path)

token = os.getenv("BOT_FATHER")
bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))


