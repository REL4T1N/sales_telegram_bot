from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart, CommandObject, BaseFilter
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.types import InlineKeyboardMarkup

admin_ids = []

class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in admin_ids