from database.database import create_db


async def on_startup(dp):
    from notify_admins import on_startup_notify
    await on_startup_notify(dp)
    await create_db()

if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
