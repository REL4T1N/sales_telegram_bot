from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart, CommandObject, BaseFilter
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.types import InlineKeyboardMarkup

from keyboards.start_keyboard import start_admin_keyboard
from keyboards.admin_update_catalog import work_with_catalog_keyboard

admin_ids = [6376753355]

class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in admin_ids
    

async def start_command(mes: Message):
    await mes.answer(
        text="Выберите",
        reply_markup=start_admin_keyboard                 
    )


async def work_with_catalog(mes: Message):
    await mes.answer(
        text="Выберите действие",
        reply_markup=work_with_catalog_keyboard
    )


async def add_new_catalog(query: CallbackQuery):
    await query.message.edit_text(
        text="Заглушка"
        # reply_markup=  # должна быть клавиатура
    )


def admin_handlers(dp: Dispatcher):
    dp.message.register(start_command, CommandStart(), IsAdmin())
    dp.message.register(work_with_catalog, F.text=="Обновить каталог", IsAdmin())