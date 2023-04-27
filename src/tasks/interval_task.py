from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.notifier import Notifier
from src.db.manager import DbManager
from src.db.models import IntervalTask, Product


class IntervalTaskProcessor:

    def __init__(self, db_manager: DbManager, notifier: Notifier):
        self.db_manager = db_manager
        self.notifier = notifier

    async def get_tasks(self, session: AsyncSession) -> Sequence[IntervalTask]:
        return (
            await session.scalars(
                select(IntervalTask, Product)
                .join(Product)
            )
        ).all()

    async def process_task(self, task: IntervalTask) -> int:
        if task.product.marketplace == Product.Marketplace.WILDBERRIES:
            return
        if task.product.marketplace == Product.Marketplace.OZON: pass
        if task.product.marketplace == Product.Marketplace.YA_MARKET: pass

    async def process_tasks(self):
        async with self.db_manager.session() as session:
            for task in await self.get_tasks(session):
                try:
                    result = self.process_task(task)
                    if result - task.last_value > 5:
                        self.notifier.interval_notify(task, result)

                    task.last_value = result
                except Exception as ex:
                    task.last_try_attempts += 1
                    task.status = IntervalTask.Status.failed

                session.add(result)

            await session.commit()