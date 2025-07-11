import asyncio

from bot.bot import bot
from bot.dispatcher import dp

from handlers.admin.product.create.select_params import register_product_create_select_params


register_product_create_select_params(dp)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())