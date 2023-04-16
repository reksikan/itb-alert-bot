from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import (Boolean, Date, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    class Base(DeclarativeBase, _ColumnExpressionArgument):  # type: ignore # noqa
        pass
else:
    class Base(DeclarativeBase):
        pass


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        UniqueConstraint('marketplace', 'external_id'),
    )

    class Marketplace(str, Enum):
        YA_MARKET = 'ya_market'
        WILDBERRIES = 'wildberries'
        OZON = 'ozon'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    marketplace: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[str] = mapped_column(String, nullable=False)

    interval_tasks: Mapped[List['IntervalTask']] = relationship(
        'IntervalTask',
        uselist=True,
        back_populates='product',
    )
    schedule_tasks: Mapped[List['ScheduleTask']] = relationship(
        'ScheduleTask',
        uselist=True,
        back_populates='product'
    )


class ScheduleTask(Base):
    __tablename__ = 'schedule_task'
    __table_args__ = (
        UniqueConstraint('product_id', 'type'),
    )

    class Type(str, Enum):
        DOWN_FOR_CATEGORY = 'Падение по категории'
        DOWN_FOR_KEYWORD = 'Падение по ключевым словам'

    class Status(str, Enum):
        PENDING = 'pending'
        IN_PROCESS = 'in_process'
        failed = 'failed'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default=Status.PENDING, nullable=False)

    last_try_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_update_at: Mapped[date] = mapped_column(Date, default=date.today(), onupdate=date.today(), nullable=False)

    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('product.id'), nullable=False)
    product: Mapped[Product] = relationship(Product, foreign_keys=[product_id], back_populates='schedule_tasks')


class IntervalTask(Base):
    __tablename__ = 'interval_task'
    __table_args__ = (
        UniqueConstraint('product_id', 'type'),
    )

    class Type(str, Enum):
        DISAPPEARANCE = 'Исчезновение с сайта'
        DOWN_RATE = 'Падение рейтинга'

    class Priority(str, Enum):
        HIGH = 'Высокий'
        MIDDLE = 'Средний'
        LOW = 'Низкий'

    class Status(str, Enum):
        PENDING = 'pending'
        IN_PROCESS = 'in_process'
        failed = 'failed'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default=Status.PENDING, nullable=False)
    priority: Mapped[str] = mapped_column(String, default=Priority.LOW, nullable=False)

    last_try_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_update_at: Mapped[date] = mapped_column(
        Date,
        default=date.today(),
        onupdate=date.today(),
        nullable=False
    )
    last_value: Mapped[int | None] = mapped_column(Integer, nullable=True)

    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('product.id'), nullable=False)
    product: Mapped[Product] = relationship(Product, foreign_keys=[product_id], back_populates='interval_tasks')


class Admin(Base):
    __tablename__ = 'admin'

    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    access: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Account(Base):
    __tablename__ = 'external_account'
    __table_args__ = (
        UniqueConstraint('site', 'api_key'),
    )

    class Site(str, Enum):
        YA_MARKET = 'ya_market'
        WILDBERRIES = 'wildberries'
        OZON = 'ozon'
        MPSTATS = 'mpstats'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    site: Mapped[str] = mapped_column(String, nullable=False)
    api_key: Mapped[str] = mapped_column(String, nullable=False)
    client_id: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
