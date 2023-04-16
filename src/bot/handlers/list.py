from typing import List, Dict, Any

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.UI.list_keyboards import product_with_tasks_keyboard, tasks_by_product_keyboard, actions_keyboard, Actions
from src.bot.handlers.base import BaseHandlerList


class ListHandlerList(BaseHandlerList):

    class ListState(StatesGroup):
        WAIT_FOR_PRODUCT = State()
        WAIT_FOR_TASK = State()
        WAIT_FOR_ACTION = State()

    def handlers(self) -> List[Dict[str, Any]]:
        return [
            {'function': self.list_handler, 'filters': {'commands': ['list'], 'state': '*'}},
            {'function': self.select_product, 'filters': {'state': self.ListState.WAIT_FOR_PRODUCT}},
            {'function': self.select_task, 'filters': {'state': self.ListState.WAIT_FOR_TASK}},
            {'function': self.select_action, 'filters': {'state': self.ListState.WAIT_FOR_ACTION}},
        ]

    async def list_handler(self, message: Message, **kwargs):
        keyboard = await product_with_tasks_keyboard(self.db_manager)
        await message.answer('Выбирете товар', reply_markup=keyboard)
        await self.ListState.WAIT_FOR_PRODUCT.set()

    async def select_product(self, message: Message, state: FSMContext, **kwargs):
        external_id = message.text.split(':')[0]
        marketplace = message.text.split(':')[1]
        async with state.proxy() as data:
            data['external_id'] = external_id
            data['marketplace'] = marketplace

        keyboard = await tasks_by_product_keyboard(self.db_manager, external_id, marketplace)
        await message.answer('Выбирете оповещение', reply_markup=keyboard)
        await self.ListState.WAIT_FOR_TASK.set()

    async def select_task(self, message: Message, state: FSMContext, **kwargs):
        async with state.proxy() as data:
            task = await self.db_manager.get_task(data['external_id'], data['marketplace'], message.text)
            data['task_id'] = task.id
            data['task_type'] = task.type

        await message.answer(
            f'Оповещение для товара: {data["external_id"]}\n'
            f'Маркетплейс: {data["marketplace"]}\n'
            f'Тип оповещения: {task.type}\n'
            f'Последняя проверка: {task.last_update_at}\n'
            + (f'Приоритет: {task.priority}' if hasattr(task, 'priority') else ''),
            reply_markup=actions_keyboard())
        await self.ListState.WAIT_FOR_ACTION.set()

    async def select_action(self, message: Message, state: FSMContext, **kwargs):
        if message.text == Actions.DELETE:
            async with state.proxy() as data:
                await self.db_manager.delete_task(data['task_id'], data['task_type'])
                await message.answer('Задача успешно удалена')

        await message.answer('Возвращаюсь', reply_markup=ReplyKeyboardRemove())
        await state.reset_state()
