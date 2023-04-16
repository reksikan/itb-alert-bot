from typing import List, Dict, Any

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.UI.create_keyboards import (
    type_keyboard,
    marketplace_keyboard,
    products_keyboard,
    priority_keyboard,
)
from src.bot.handlers.base import BaseHandlerList
from src.db.models import IntervalTask


class CreateHandlerList(BaseHandlerList):
    class CreateState(StatesGroup):
        WAIT_FOR_MARKETPLACE = State()
        WAIT_FOR_TYPE = State()
        WAIT_FOR_PRODUCT_ID = State()
        WAIT_FOR_PRIORITY = State()

    def handlers(self) -> List[Dict[str, Any]]:
        return [
            {'function': self.create_handler, 'filters': {'commands': ['create'], 'state': '*'}},
            {'function': self.select_type, 'filters': {'state': self.CreateState.WAIT_FOR_TYPE}},
            {'function': self.select_marketplace, 'filters': {'state': self.CreateState.WAIT_FOR_MARKETPLACE}},
            {'function': self.select_product_id, 'filters': {'state': self.CreateState.WAIT_FOR_PRODUCT_ID}},
            {'function': self.select_priority, 'filters': {'state': self.CreateState.WAIT_FOR_PRIORITY}},
        ]

    async def create_handler(self, message: Message, **kwargs):
        await message.answer(
            'Выберете маркетплейс',
            reply_markup=marketplace_keyboard()
        )
        await self.CreateState.WAIT_FOR_TYPE.set()

    async def select_type(self, message: Message, state: FSMContext, **kwargs):
        async with state.proxy() as data:
            data['marketplace'] = message.text

        await message.answer('Выберете тип', reply_markup=type_keyboard(message.text))
        await self.CreateState.WAIT_FOR_MARKETPLACE.set()

    async def select_marketplace(self, message: Message, state: FSMContext, **kwargs):
        async with state.proxy() as data:
            data['task_type'] = message.text
            data['is_interval'] = message.text in [IntervalTask.Type.DISAPPEARANCE, IntervalTask.Type.DOWN_RATE]

        keyboard = await products_keyboard(self.db_manager, data['marketplace'])
        await message.answer('Выберете товар', reply_markup=keyboard)
        await self.CreateState.WAIT_FOR_PRODUCT_ID.set()

    async def select_product_id(self, message: Message, state: FSMContext, **kwargs):
        product_external_id = message.text.split(':')[0]
        async with state.proxy() as data:
            if not data['is_interval']:
                await self.db_manager.create_schedule_task(
                    product_external_id=product_external_id,
                    marketplace=data['marketplace'],
                    task_type=data['task_type'],
                )
                await message.answer('Товар добавлен', reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
                return

            data['product_external_id'] = product_external_id
            await message.answer('Введите приоритет проверки', reply_markup=priority_keyboard())
            await self.CreateState.WAIT_FOR_PRIORITY.set()

    async def select_priority(self, message: Message, state: FSMContext, **kwargs):
        async with state.proxy() as data:
            await self.db_manager.create_interval_task(
                product_external_id=data['product_external_id'],
                marketplace=data['marketplace'],
                task_type=data['task_type'],
                priority=message.text,
            )

        await message.answer('Товар добавлен', reply_markup=ReplyKeyboardRemove())
        await state.reset_state()
