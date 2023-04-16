from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.db.manager import DbManager
from src.db.models import Product, ScheduleTask, IntervalTask


def type_keyboard(marketplace: Product.Marketplace) -> ReplyKeyboardMarkup:
    marketplace_task = {
        Product.Marketplace.WILDBERRIES: [
            [ScheduleTask.Type.DOWN_FOR_CATEGORY.value],
            [ScheduleTask.Type.DOWN_FOR_KEYWORD.value],
            [IntervalTask.Type.DISAPPEARANCE.value],
            [IntervalTask.Type.DOWN_RATE.value],
        ],
        Product.Marketplace.OZON: [
            [ScheduleTask.Type.DOWN_FOR_CATEGORY.value],
            [IntervalTask.Type.DISAPPEARANCE.value],
            [IntervalTask.Type.DOWN_RATE.value],
        ],
        Product.Marketplace.YA_MARKET: [
            [IntervalTask.Type.DISAPPEARANCE.value],
            [IntervalTask.Type.DOWN_RATE.value],
        ],
    }
    return ReplyKeyboardMarkup(marketplace_task[marketplace])


def marketplace_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [Product.Marketplace.WILDBERRIES.value],
            [Product.Marketplace.OZON.value],
            [Product.Marketplace.YA_MARKET.value],
        ]
    )


def priority_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [IntervalTask.Priority.HIGH.value],
            [IntervalTask.Priority.MIDDLE.value],
            [IntervalTask.Priority.LOW.value],
        ]
    )


async def products_keyboard(db_manager: DbManager, marketplace: Product.Marketplace) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        list(
            map(
                lambda product: [KeyboardButton(f'{product.external_id}:{product.marketplace}')],
                await db_manager.get_products_by_marketplace(marketplace)
            )
        )
    )
