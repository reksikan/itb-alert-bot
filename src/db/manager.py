import subprocess
from typing import Optional, Sequence, Type, Union

from aiologger.loggers.json import JsonLogger
from sqlalchemy import and_, delete, exists, not_, or_, select, text
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.ext.asyncio.session import _AsyncSessionContextManager

from src.db.models import Account, Admin, IntervalTask, Product, ScheduleTask

logger = JsonLogger.with_default_handlers()


class DbManager:

    def __init__(self, async_engine: AsyncEngine):
        self._async_engine = async_engine
        self._async_session = async_sessionmaker(
            self._async_engine,
            expire_on_commit=False,
        )

    async def healthcheck(self) -> bool:
        try:
            async with self.session() as session:
                await session.execute(text('CREATE TEMPORARY TABLE test (testclmn TEXT) ON COMMIT DROP;'))
                return True
        except Exception:
            logger.exception('Database healthcheck failed')
            return False

    def session(self) -> _AsyncSessionContextManager[AsyncSession]:
        return self._async_session.begin()

    # Admin functions
    async def have_access(self, telegram_id: int) -> bool:
        async with self.session() as session:
            return await session.scalar(
                select(
                    exists(Admin)
                    .where(
                        Admin.telegram_id == telegram_id,
                        Admin.access
                    )
                )
            )

    async def create_user(self, telegram_id: int):
        async with self.session() as session:
            user = Admin(telegram_id=telegram_id)
            session.add(user)
            await session.commit()

    async def get_users(self) -> Sequence[Admin]:
        async with self.session() as session:
            return (
                await session.scalars(
                    select(Admin)
                )
            ).all()

    async def get_user_by_id(self, telegram_id: int) -> Optional[Admin]:
        async with self.session() as session:
            return (
                await session.scalars(
                    select(Admin)
                    .where(
                        Admin.telegram_id == telegram_id
                    )
                )
            ).one_or_none()

    async def user_change_right(self, user: Admin, access: bool):
        async with self.session() as session:
            user.access = access
            session.add(user)
            await session.commit()

    # Product functions
    async def get_products_by_marketplace(self, marketplace: Product.Marketplace) -> Sequence[Product]:
        async with self.session() as session:
            return (
                await session.scalars(
                    select(Product)
                    .where(
                        Product.marketplace == marketplace
                    )
                )
            ).all()

    async def get_product(self, external_id: str, marketplace: Product.Marketplace) -> Product:
        async with self.session() as session:
            return (
                await session.scalars(
                    select(Product)
                    .where(
                        Product.external_id == external_id,
                        Product.marketplace == marketplace,
                    )
                )
            ).one()

    async def get_product_with_tasks(self) -> Sequence[Product]:
        async with self.session() as session:
            return (
                await session.scalars(
                    select(Product)
                    .join(
                        IntervalTask,
                        and_(
                            IntervalTask.product_id == Product.id,
                            not_(IntervalTask.priority == IntervalTask.Priority.LOW),
                        ),
                        isouter=True,
                    )
                    .join(ScheduleTask, isouter=True)
                    .where(
                        or_(
                            Product.interval_tasks.any(),
                            Product.schedule_tasks.any(),
                        )
                    )
                )
            ).all()

    # Task functions
    async def create_interval_task(
        self,
        product_external_id: str,
        marketplace: Product.Marketplace,
        task_type: IntervalTask.Type,
        priority: IntervalTask.Priority = IntervalTask.Priority.HIGH,
    ):
        async with self.session() as session:
            product = await self.get_product(product_external_id, marketplace)
            task = IntervalTask(type=task_type, product=product, priority=priority)
            session.add(task)
            await session.commit()

    async def create_schedule_task(
        self,
        product_external_id: str,
        marketplace: Product.Marketplace,
        task_type: ScheduleTask.Type,
    ):
        async with self.session() as session:
            product = await self.get_product(product_external_id, marketplace)
            task = ScheduleTask(type=task_type, product=product)
            session.add(task)
            await session.commit()

    async def get_tasks_by_product(
        self,
        external_id: str,
        marketplace: Product.Marketplace
    ) -> Sequence[Union[ScheduleTask, IntervalTask]]:
        async with self.session() as session:
            return (
                await session.scalars(
                    select(ScheduleTask.type)
                    .join(Product)
                    .where(
                        Product.external_id == external_id,
                        Product.marketplace == marketplace,
                    )
                    .union(
                        select(IntervalTask.type)
                        .join(Product)
                        .where(
                            Product.external_id == external_id,
                            Product.marketplace == marketplace,
                        )
                    )
                )
            ).all()

    async def get_task(
        self,
        product_external_id: str,
        marketplace: Product.Marketplace,
        task_type: Union[ScheduleTask.Type, IntervalTask.Type]
    ) -> Union[ScheduleTask, IntervalTask]:
        async with self.session() as session:
            task_obj = self.get_task_object(task_type)
            return (
                await session.scalars(
                    select(task_obj)
                    .join(Product)
                    .where(
                        Product.external_id == product_external_id,
                        Product.marketplace == marketplace,
                        task_obj.type == task_type,
                    )
                )
            ).one()

    async def delete_task(
        self,
        id_: int,
        task_type: Union[ScheduleTask.Type, IntervalTask.Type],
    ):
        task_obj = self.get_task_object(task_type)
        async with self.session() as session:
            await session.execute(
                delete(task_obj)
                .where(task_obj.id == id_)
            )

    @staticmethod
    def get_task_object(
        task_type: Union[ScheduleTask.Type, IntervalTask.Type]
    ) -> Type[Union[ScheduleTask, IntervalTask]]:
        if task_type in (ScheduleTask.Type.DOWN_FOR_CATEGORY, ScheduleTask.Type.DOWN_FOR_KEYWORD):
            return ScheduleTask
        if task_type in (IntervalTask.Type.DOWN_RATE, IntervalTask.Type.DISAPPEARANCE):
            return IntervalTask
        raise Exception

    # Accounts functions
    async def get_accounts_by_site(self, site: Account.Site) -> Sequence[Account]:
        async with self.session() as session:
            return (
                await session.scalars(
                    select(Account)
                    .where(Account.site == site)
                )
            ).all()

    async def get_account_by_name_and_site(self, name: str, site: Account.Site) -> Optional[Account]:
        async with self.session() as session:
            return (
                await session.scalars(
                    select(Account)
                    .where(
                        Account.name == name,
                        Account.site == site,
                    )
                )
            ).one_or_none()

    async def remove_account(self, account_id: int):
        async with self.session() as session:
            await session.execute(
                delete(Account)
                .where(Account.id == account_id)
            )

    async def create_account(self, name: str, api_key: str, site: Account.Site, client_id: Optional[int]):
        async with self.session() as session:
            account = Account(
                name=name,
                site=site,
                api_key=api_key,
                client_id=client_id,
            )
            session.add(account)
            await session.commit()


def create_db_manager(
    connection_url: str,
    need_migrations: bool = True
) -> DbManager:
    engine = create_async_engine(connection_url)

    if need_migrations:
        subprocess.run(
            'alembic upgrade head',
            check=True,
            shell=True
        )

    return DbManager(engine)
