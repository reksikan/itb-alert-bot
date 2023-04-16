from typing import List, Dict, Any

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.UI.users_keyboards import users_keyboard, user_actions_keyboard, Actions
from src.bot.handlers.base import BaseHandlerList


class UsersHandlerList(BaseHandlerList):
    class UserState(StatesGroup):
        WAIT_FOR_USER = State()
        WAIT_FOR_ACTION = State()

    def handlers(self) -> List[Dict[str, Any]]:
        return [
            {'function': self.users_handler, 'filters': {'commands': ['users'], 'state': '*'}},
            {'function': self.select_user, 'filters': {'state': self.UserState.WAIT_FOR_USER}},
            {'function': self.select_action, 'filters': {'state': self.UserState.WAIT_FOR_ACTION}},
        ]

    async def users_handler(self, message: Message, **kwargs):
        keyboard = await users_keyboard(self.db_manager)
        await message.answer('Выберете пользователя', reply_markup=keyboard)
        await self.UserState.WAIT_FOR_USER.set()

    async def select_user(self, message: Message, state: FSMContext, **kwargs):
        selected_user = await self.db_manager.get_user_by_id(int(message.text))
        keyboard = user_actions_keyboard(selected_user)
        async with state.proxy() as data:
            data['edit_user_settings'] = selected_user.telegram_id
        await message.answer('Выберете действие', reply_markup=keyboard)
        await self.UserState.WAIT_FOR_ACTION.set()

    async def select_action(self, message: Message, state: FSMContext, **kwargs):
        async with state.proxy() as data:
            selected_user = await self.db_manager.get_user_by_id(data['edit_user_settings'])
            if message.text == Actions.SET_ADMIN:
                await self.db_manager.user_change_right(selected_user, True)
                await message.answer(f'Пользователю {selected_user.telegram_id} дан доступ')
            if message.text == Actions.UNSET_ADMIN:
                await self.db_manager.user_change_right(selected_user, False)
                await message.answer(f'У пользователя {selected_user.telegram_id} забран доступ')

        await message.answer('Возвращаюсь', reply_markup=ReplyKeyboardRemove())
        await state.reset_state()
