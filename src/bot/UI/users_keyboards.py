from enum import Enum

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.db.manager import DbManager
from src.db.models import Admin


class Actions(str, Enum):
    SET_ADMIN = 'Дать доступ'
    UNSET_ADMIN = 'Забрать доступ'
    CANCEL = 'Вернуться назад'


async def users_keyboard(db_manager: DbManager) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        list(
            map(
                lambda user: [KeyboardButton(user.telegram_id)],
                await db_manager.get_users()
            )
        )
    )


def user_actions_keyboard(user: Admin) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(Actions.UNSET_ADMIN.value if user.access is True else Actions.SET_ADMIN.value)],
            [KeyboardButton(Actions.CANCEL.value)]
        ]
    )
