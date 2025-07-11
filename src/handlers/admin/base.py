from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject


admin_ids = [6376753355]


class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in admin_ids