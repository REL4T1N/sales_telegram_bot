import asyncio

from bot.bot import bot
from bot.dispatcher import dp

from handlers.admin import admin_handlers
from handlers.commom import common_handlers
from handlers.update_product import register_update_product_handlers


admin_handlers(dp)
common_handlers(dp)
register_update_product_handlers(dp)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())