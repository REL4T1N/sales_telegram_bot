from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup


from keyboards.start_keyboard import start_keyboard

async def start_command(mes: Message):
    await mes.answer(
        text="Добро пожаловать",
        reply_markup=start_keyboard
    )


def common_handlers(dp: Dispatcher):
    dp.message.register(start_command, CommandStart())