from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.dispatcher import FSMContext

from bot import bot, dp, db, config
from utils.validators import Tablemaker
from utils.states import StateAdmin
from utils.buttons import Button


async def get_user_info(message: Message, state: FSMContext):
    """Управление пользователями."""
    await message.answer('Введите идентификатор пользователя'
                         + ', чтобы изменить его баланс или заблокировать.'
                         + '\nИли выгрузите сведения о всех пользователях'
                         + ', нажав на кнопку.',
                         reply_markup=Button().all_users)
    await state.reset_state()
    await StateAdmin.A1.set()


async def get_user_id(message: Message, state: FSMContext):
    """Получение данных о пользователях."""
    user_id = message.text
    balance = db.user_info(user_id)
    if balance:
        await message.answer(f'Баланс пользователя: {balance[1]} руб.',
                             reply_markup=Button().manage_user,
                             )
        await state.update_data(A1=user_id)
    else:
        await message.answer('Пользователя с таким идентификатором нет в базе.'
                             + '\nПопробуйте ввести другой.'
                             + '\nИли отмените действие.',
                             reply_markup=Button().cancel)


async def all_users_button(callback: CallbackQuery):
    """Кнопка выгрузки данных пользователей."""
    file = open('logs/users.log', 'w')
    records = Tablemaker(db.user_get_all()).make_table()
    file.write(records)
    file.close()
    all_users = InputFile('logs/users.log')
    await bot.send_document(callback.from_user.id, all_users)


async def change_balance_button(callback: CallbackQuery):
    """Кнопка изменения баланса."""
    await StateAdmin.A2.set()
    await bot.send_message(callback.from_user.id, 'Введите новое значение баланса.')


async def ban_user_button(callback: CallbackQuery, state: FSMContext):
    """Блокировка пользователя."""
    await StateAdmin.A2.set()
    async with state.proxy() as data:
        user_id = data['A1']
        db.user_ban(user_id)
        await bot.send_message(callback.from_user.id, 'Пользователь заблокирован.')
        await state.finish()


async def change_user_balance(message: Message, state: FSMContext):
    """Изменение баланса пользователя."""
    async with state.proxy() as data:
        user_id = data['A1']
        new_balance = message.text
        db.user_update(user_id, new_balance)
        await message.answer('Баланс изменен.')
        await state.finish()


async def get_user_logs(message: Message):
    """Выгрузка логов."""
    log = InputFile('logs/errors.log')
    await bot.send_document(message.from_id, log)


async def cancel_button(state: FSMContext):
    """Отмена операции."""
    await state.reset_state()


def register_admin(d: dp):
    d.register_message_handler(get_user_info, user_id=config.telegram.admin, commands=["user"], state='*')
    d.register_message_handler(get_user_id, user_id=config.telegram.admin, state=StateAdmin.A1)
    d.register_message_handler(change_user_balance, user_id=config.telegram.admin, state=StateAdmin.A2)
    d.register_message_handler(get_user_logs, user_id=config.telegram.admin, commands=["log"], state='*')
    d.register_callback_query_handler(all_users_button, text='all_users', state=StateAdmin.A1)
    d.register_callback_query_handler(change_balance_button, text='change_balance', state=StateAdmin.A1)
    d.register_callback_query_handler(ban_user_button, text='ban_user', state=StateAdmin.A1)
    d.register_callback_query_handler(cancel_button, text='cancel', state='*')
