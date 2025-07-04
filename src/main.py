import asyncio

from bot.bot import bot
from bot.dispatcher import dp


async def main():
    dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())