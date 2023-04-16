from enum import Enum

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.db.manager import DbManager
from src.db.models import Product


async def product_with_tasks_keyboard(db_manager: DbManager) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        list(
            map(
                lambda product: [KeyboardButton(f'{product.external_id}:{product.marketplace}')],
                await db_manager.get_product_with_tasks()
            )
        )
    )


async def tasks_by_product_keyboard(
    db_manager: DbManager,
    external_id,
    marketplace: Product.Marketplace
) -> ReplyKeyboardMarkup:
    print(await db_manager.get_tasks_by_product(external_id, marketplace))
    return ReplyKeyboardMarkup(
        list(
            map(
                lambda type_: [type_],
                await db_manager.get_tasks_by_product(external_id, marketplace)
            )
        )
    )


class Actions(str, Enum):
    DELETE = 'Удалить'
    CANCEL = 'Отмена'


def actions_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(Actions.DELETE.value)],
            [KeyboardButton(Actions.CANCEL.value)],
        ]
    )
