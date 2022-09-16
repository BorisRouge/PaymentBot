from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pyqiwip2p import QiwiP2P

from utils import settings
from utils.db_manager import Database


config = settings.get_config("sample.env")
bot = Bot(token=config.telegram.telegram_bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database(config.database.con_data)
p2p = QiwiP2P(auth_key=config.qiwi.qiwi_secret_key)
