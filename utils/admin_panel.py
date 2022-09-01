import asyncio
import logging

from aiogram import Bot, Dispatcher, executor, types
from pyqiwip2p import QiwiP2P

from utils import settings
from utils.buttons import Button
from utils.validators import Validator
from utils.db_manager import Database

logger = logging.getLogger(__name__)