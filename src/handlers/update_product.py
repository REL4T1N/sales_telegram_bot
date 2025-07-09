import asyncio

from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.filters import CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.admin import IsAdmin, admin_ids

from keyboards.common import create_keyboard

from services.product.common import create_object, update_object, get_all
from services.product.product import get_product_display_data

from states.product import UpdateProductStates

from utils.formatting_float_nums import pretty_num


def register_update_product_handlers(dp: Dispatcher):
    pass