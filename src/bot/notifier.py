from aiogram import Bot

from src.db.manager import DbManager


class Notifier:
    def __init__(
        self,
        db_manager: DbManager,
        bot: Bot,
        notification_chat_id: int,
    ):
        self.telegram = bot
        self.db_manager = db_manager
        self.notification_chat_id = notification_chat_id
