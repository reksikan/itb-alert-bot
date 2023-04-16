from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message

from src.db.manager import DbManager


async def common_error_handler(update, error):
    message: Message = update['message']
    await message.answer('Ошибка при обработке запроса')
    await message.answer(error)
    return True


class AuthMiddleware(BaseMiddleware):

    def __init__(self, db_manager: DbManager):
        self._db_manager = db_manager
        super().__init__()

    async def on_pre_process_message(self, message: Message, _):
        if user := await self._db_manager.get_user_by_id(message.from_user.id):
            if user.access:
                return
        else:
            await self._db_manager.create_user(message.from_user.id)

        await message.answer(
            f'Нужно подтверждение авторизации, обратитесь к администратору'
            f'Ваш telegram ID: {message.from_user.id}'
        )
        raise CancelHandler()
