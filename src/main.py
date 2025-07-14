import asyncio

from bot.bot import bot
from bot.dispatcher import dp

from handlers.admin.product.create.catalog import register_product_create_catalog
from handlers.admin.product.create.category import register_product_create_category
from handlers.admin.product.create.enter_params import register_product_create_enter_params
from handlers.admin.product.create.unit import register_product_create_unit


register_product_create_catalog(dp)
register_product_create_category(dp)
register_product_create_enter_params(dp)
register_product_create_unit(dp)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())