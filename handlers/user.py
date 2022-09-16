import asyncio
from random import randint

from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from bot import bot, dp, db, p2p
from utils.validators import Validator
from utils.states import StateDeposit
from utils.buttons import Button


async def welcome(message: Message, state: FSMContext):
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


async def deposit(callback: CallbackQuery):
    """Обработка кнопки "Пополнить баланс"."""
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(callback.from_user.id, "На какую сумму в рублях?")
    await StateDeposit.D1.set()


async def confirm_amount(message: Message):
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


async def confirm_amount_button(callback: CallbackQuery):
    """Обработка кнопки подтверждения суммы пополнения."""
    amount = int(callback.data.split(':')[-1])
    bill = p2p.bill(bill_id=randint(100000, 999999), amount=amount, lifetime=5)
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


async def check_status_button(callback: CallbackQuery):
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


def register_user(d: dp):
    d.register_message_handler(welcome, commands=['start'], state='*')
    d.register_message_handler(confirm_amount, state=StateDeposit.D1)
    d.register_callback_query_handler(deposit, text='deposit')
    d.register_callback_query_handler(confirm_amount_button,
                                       text_contains='confirm_amount:',
                                       state=StateDeposit.D1)
    d.register_callback_query_handler(check_status_button,
                                       text_contains='bill:',
                                       state=StateDeposit.D2)
