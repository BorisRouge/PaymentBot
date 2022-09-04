import asyncio
from random import randint

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputFile
from pyqiwip2p import QiwiP2P

from utils import settings
from utils.buttons import Button
from utils.validators import Validator, Tablemaker
from utils.db_manager import Database
from utils.states import StateAdmin, StateDeposit


config = settings.get_config("sample.env")
bot = Bot(token=config.telegram.telegram_bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database(config.database.con_data)
p2p = QiwiP2P(auth_key=config.qiwi.qiwi_secret_key)


# _________________________________User Handlers_________________________________
@dp.message_handler(commands=['start'], state='*')
async def welcome(message: types.Message, state: FSMContext):
    """Запуск диалога с ботом."""
    user_data = db.user_info(message.from_user.id)
    if user_data is False:
        db.user_create(message.from_user.id)
        user_data = db.user_info(message.from_user.id)
    if user_data[2] is True:
        await message.answer(f"Вы заблокированы администратором.")
        return
    await message.answer(f"Привет, {message.from_user.full_name}"
                    +"\nЯ - бот для пополнения баланса."
                    +"\nНажмите на кнопку, чтобы пополнить баланс."
                    +f"\nСейчас на счету: {user_data[1]} руб.",
                    reply_markup=Button().deposit
                    )
    await state.reset_state()


@dp.callback_query_handler(text='deposit')
async def deposit(callback: types.CallbackQuery):
    """Обработка кнопки "Пополнить баланс"."""
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(callback.from_user.id, "На какую сумму в рублях?")
    await StateDeposit.D1.set()


@dp.message_handler(state=StateDeposit.D1)
async def confirm_amount(message: types.Message):
    """Подтверждение суммы пополнения"""
    amount = Validator(message.text).clean()
    if amount:
        await bot.send_message(message.from_user.id,
            f"Сумма для пополнения: {amount} руб., верно?\nЕсли нет, введите сумму заново.",
            reply_markup=Button().confirm_amount(amount)
        )
    else:
        await bot.send_message(
            message.from_user.id, "Введите сумму целым числом, без букв и пробелов.")


@dp.callback_query_handler(text_contains='confirm_amount:', state=StateDeposit.D1)
async def confirm_amount_button(callback: types.CallbackQuery):
    """Обработка кнопки подтверждения суммы пополнения."""
    amount = int(callback.data.split(':')[-1])
    bill = p2p.bill(bill_id=randint(100000,999999), amount=amount, lifetime=5)
    await StateDeposit.D2.set()
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(
        callback.from_user.id,
        "Счет на оплату для пополнения баланса.",
        reply_markup=Button().confirm_payment(bill.pay_url, bill.bill_id),
        )
    while True:
        status = p2p.check(bill.bill_id).status
        if status == 'WAITING':
            await asyncio.sleep(15)
        elif status == 'PAID':
            db.deposit(callback.from_user.id, amount, bill.bill_id)
            break
        elif status == 'EXPIRED':
            await bot.send_message(callback.from_user.id,
            'Платежный документ просрочен. Вы можете создать новый.',
            reply_markup=Button().deposit,
            )
            break


@dp.callback_query_handler(text_contains='bill:', state=StateDeposit.D2)
async def check_status_button(callback: types.CallbackQuery):
    bill_id = callback.data.split(':')[-1]
    status = p2p.check(bill_id).status
    if status == 'PAID':
        await bot.send_message(callback.from_user.id,
            'Платеж получен.',
            )
    elif status == 'EXPIRED':
        await bot.send_message(callback.from_user.id,
            'Платежный документ просрочен. Вы можете создать новый.',
            reply_markup=Button().deposit,
            )
    elif status == 'WAITING':
        await bot.send_message(callback.from_user.id,
            'Ожидается поступление средств на счет.',
            )


# _________________________________Admin Handlers_________________________________

@dp.message_handler(user_id=config.telegram.admin, commands=["user"], state='*')
async def get_user_info(message: types.Message, state:FSMContext):
    """Управление пользователями."""
    await message.answer('Введите идентификатор пользователя'
                        +', чтобы изменить его баланс или заблокировать.'
                        +'\nИли выгрузите сведения о всех пользователях'
                        +', нажав на кнопку.',
                        reply_markup=Button().all_users)
    await state.reset_state()
    await StateAdmin.A1.set()


@dp.message_handler(user_id=config.telegram.admin, state=StateAdmin.A1)
async def get_user_id(message: types.Message, state:FSMContext):
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
                             +'\nПопробуйте ввести другой.'
                             +'\nИли отмените действие.',
                             reply_markup=Button().cancel)


@dp.callback_query_handler(text='all_users', state=StateAdmin.A1)
async def all_users_button(callback: types.CallbackQuery):
    """Кнопка выгрузки данных пользователей."""
    file = open('logs/users.log', 'w')
    records = Tablemaker(db.user_get_all()).make_table()
    file.write(records)
    file.close()
    all_users = InputFile('logs/users.log')
    await bot.send_document(callback.from_user.id, all_users)


@dp.callback_query_handler(text='change_balance', state=StateAdmin.A1)
async def change_balance_button(callback: types.CallbackQuery):
    """Кнопка изменения баланса."""
    await StateAdmin.A2.set()
    await bot.send_message(callback.from_user.id, 'Введите новое значение баланса.')


@dp.callback_query_handler(text='ban_user', state=StateAdmin.A1)
async def ban_user_button(callback: types.CallbackQuery, state:FSMContext):
    """Блокировка пользователя."""
    await StateAdmin.A2.set()
    async with state.proxy() as data:
        user_id = data['A1']
        db.user_ban(user_id)
        await bot.send_message(callback.from_user.id, 'Пользователь заблокирован.')
        await state.finish()


@dp.message_handler(user_id=config.telegram.admin, state=StateAdmin.A2)
async def change_user_balance(message: types.Message, state:FSMContext):
    """Изменение баланса пользователя."""
    async with state.proxy() as data:
        user_id = data['A1']
        new_balance = message.text
        db.user_update(user_id, new_balance)
        await message.answer('Баланс изменен.')
        await state.finish()


@dp.message_handler(user_id=config.telegram.admin, commands=["log"], state='*')
async def get_user_info(message: types.Message, state:FSMContext):
    """Выгрузка логов."""
    log = InputFile('logs/errors.log')
    await bot.send_document(message.from_id, log)


@dp.callback_query_handler(text='cancel', state='*')
async def cancel_button(callback: types.CallbackQuery, state:FSMContext):
    """Отмена операции."""
    await state.reset_state()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)