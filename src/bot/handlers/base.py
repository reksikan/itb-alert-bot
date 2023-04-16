from typing import Any, Callable, Dict, List, Self

from aiogram import Dispatcher
from aiogram.types import Message

from src.db.manager import DbManager


class BaseHandlerList:

    def __init__(self, dispatcher: Dispatcher, db_manager: DbManager):
        self.db_manager = db_manager

        for handler in self.handlers():
            dispatcher.register_message_handler(handler['function'], **handler['filters'])

    def handlers(self) -> List[Dict[str, Any]]:
        pass

    @staticmethod
    def need_auth(func: Callable):
        async def _wrapper(self: Self, message: Message, *args, **kwargs):
            if await self.db_manager.have_access(message.from_user.id):
                return await func(self, message, *args, **kwargs)
            await message.answer(
                f'Нужно подтверждение авторизации, обратитесь к администратору'
                f'Ваш telegram ID: {message.from_user.id}'
            )
        return _wrapper
