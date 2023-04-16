from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiologger.loggers.json import JsonLogger

import settings
from src.bot.handlers.create import CreateHandlerList
from src.bot.handlers.list import ListHandlerList
from src.bot.handlers.settings import SettingsHandlerList
from src.bot.handlers.users import UsersHandlerList
from src.bot.middleware import AuthMiddleware, common_error_handler
from src.db.manager import create_db_manager

logger = JsonLogger(__name__)


if __name__ == '__main__':
    db_manager = create_db_manager(settings.POSTGRES_URL)

    bot = Bot(settings.TELEGRAM_TOKEN)
    dispatcher = Dispatcher(bot, storage=MemoryStorage())
    dispatcher.middleware.setup(AuthMiddleware(db_manager))
    dispatcher.register_errors_handler(common_error_handler, exception=Exception)

    CreateHandlerList(dispatcher, db_manager)
    ListHandlerList(dispatcher, db_manager)
    UsersHandlerList(dispatcher, db_manager)
    SettingsHandlerList(dispatcher, db_manager)

    executor.start_polling(dispatcher)
