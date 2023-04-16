from enum import Enum

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.db.manager import DbManager
from src.db.models import Account


class Actions(str, Enum):
    CREATE_NEW = 'Добавить нoвый'
    DELETE = 'Удалить'
    CANCEL = 'Вернуться назад'


def site_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(Account.Site.WILDBERRIES.value)],
            [KeyboardButton(Account.Site.OZON.value)],
            [KeyboardButton(Account.Site.YA_MARKET.value)],
            [KeyboardButton(Account.Site.MPSTATS.value)],
        ]
    )


async def accounts_by_site_keyboard(db_manager: DbManager, site: Account.Site) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(Actions.CREATE_NEW)]]
        + list(
            map(
                lambda account: [KeyboardButton(account.name)],
                await db_manager.get_accounts_by_site(site)
            )
        )
    )


def actions_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(Actions.DELETE.value)],
            [KeyboardButton(Actions.CANCEL.value)],
        ]
    )
