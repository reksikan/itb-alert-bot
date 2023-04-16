from typing import Any, Dict, List

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.handlers.base import BaseHandlerList
from src.bot.UI.settings_keyboards import (Actions, accounts_by_site_keyboard,
                                           actions_keyboard, site_keyboard)
from src.db.models import Account


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
        await message.answer('Выберете площадку', reply_markup=site_keyboard())
        await self.SettingsState.WAIT_FOR_SITE.set()

    async def select_site(self, message: Message, state: FSMContext, **kwargs):
        site = message.text
        async with state.proxy() as data:
            data['site'] = site

        keyboard = await accounts_by_site_keyboard(self.db_manager, site)
        await message.answer('Выберете пользователя', reply_markup=keyboard)
        await self.SettingsState.WAIT_FOR_ACCOUNT.set()

    async def select_account(self, message: Message, state: FSMContext, **kwargs):
        async with state.proxy() as data:
            if message.text == Actions.CREATE_NEW:
                fields = 'Введите [название],[api ключ]'
                if data['site'] == Account.Site.OZON:
                    fields += ',[account id]'
                await message.answer(fields + '\n(Через запятую, без пробелов и квадартных скобок)')
                await self.SettingsState.WAIT_FOR_NEW_ACCOUNT.set()
                return

            account = await self.db_manager.get_account_by_name_and_site(message.text, data['site'])
            data['account_id'] = account.id

        await message.answer(
            f'Аккаунт: {account.name}\n'
            f'Площадка: {account.site}\n'
            f'Api-key: {"*" * (len(account.api_key) - 4) + account.api_key[-4:]}\n'
            + (f'Client-id: {account.client_id}' if account.client_id else ''),
            reply_markup=actions_keyboard()
        )
        await message.answer('Выберете действие')
        await self.SettingsState.WAIT_FOR_ACTION.set()

    async def create_account(self, message: Message, state: FSMContext, **kwargs):
        async with state.proxy() as data:
            site = data['site']

        name = message.text.split(',')[0].strip()
        api_key = message.text.split(',')[1].strip()
        client_id = int(message.text.split(',')[2].strip()) if site == Account.Site.OZON else None

        await self.db_manager.create_account(name, api_key, site, client_id)
        await message.answer('Api ключ успешно добавлен', reply_markup=ReplyKeyboardRemove())
        await state.reset_state()

    async def select_action(self, message: Message, state: FSMContext, **kwargs):
        async with state.proxy() as data:
            if message.text == Actions.DELETE:
                await self.db_manager.remove_account(data['account_id'])
                await message.answer('Ключ успешно удален')

        await message.answer('Возвращаюсь', reply_markup=ReplyKeyboardRemove())
        await state.reset_state()
