import os
from dotenv import load_dotenv
from pathlib import Path

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties 


env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

token = os.getenv("BOT_FATHER")
if not token:
    raise ValueError("Токен бота не найден!")

bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))


    