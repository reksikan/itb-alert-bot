from typing import Any, Dict, List

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message

from src.bot.handlers.base import BaseHandlerList


class SettingsHandlerList(BaseHandlerList):
    class SettingsState(StatesGroup):
        WAIT_FOR_SITE = State()
        WAIT_FOR_ACCOUNT = State()
        WAIT_FOR_NEW_ACCOUNT = State()
        WAIT_FOR_ACTION = State()

    def handlers(self) -> List[Dict[str, Any]]:
        return [
            {'function': self.settings_handler, 'filters': {'commands': ['settings'], 'state': '*'}},
            {'function': self.select_site, 'filters': {'state': self.SettingsState.WAIT_FOR_SITE}},
            {'function': self.select_account, 'filters': {'state': self.SettingsState.WAIT_FOR_ACCOUNT}},
            {'function': self.create_account, 'filters': {'state': self.SettingsState.WAIT_FOR_NEW_ACCOUNT}},
            {'function': self.select_action, 'filters': {'state': self.SettingsState.WAIT_FOR_ACTION}},
        ]

    async def settings_handler(self, message: Message, **kwargs):
        await message.answer('Выберете пользователя')
        await self.SettingsState.WAIT_FOR_SITE.set()

    async def select_site(self, message: Message, state: FSMContext, **kwargs):
        await message.answer('Выберете пользователя')

        await self.SettingsState.WAIT_FOR_ACTION.set()

    async def select_account(self, message: Message, state: FSMContext, **kwargs):
        await message.answer('Выберете пользователя')

        await self.SettingsState.WAIT_FOR_ACTION.set()

    async def create_account(self, message: Message, state: FSMContext, **kwargs):
        await message.answer('Выберете пользователя')

        await state.reset_state()

    async def select_action(self, message: Message, state: FSMContext, **kwargs):
        await message.answer('Выберете пользователя')
        await state.reset_state()
