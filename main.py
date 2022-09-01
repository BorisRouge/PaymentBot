import asyncio
import logging
from random import randint

from aiogram import Bot, Dispatcher, executor, types
from pyqiwip2p import QiwiP2P

from utils import settings
from utils.buttons import Button
from utils.validators import Validator
from utils.db_manager import Database


config = settings.get_config("sample.env")
bot = Bot(token=config.telegram.telegram_bot_token)
dp = Dispatcher(bot)
db = Database(config.database.con_data)
p2p = QiwiP2P(auth_key=config.qiwi.qiwi_secret_key)


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    """Запуск диалога с ботом."""
    if db.user_info(message.from_user.id) is False:
        db.user_create(message.from_user.id)
    
    await message.reply(f"Привет, {message.from_user.full_name}"
                    +"\nЯ - бот для пополнения баланса."
                    +"\nНажмите на кнопку, чтобы пополнить баланс."
                    +f"\nСейчас на счету: {db.user_info(message.from_user.id)} руб.",
                    reply_markup=Button().deposit
                    )


@dp.callback_query_handler(text='deposit')
async def deposit(callback: types.CallbackQuery):
    """Обработка кнопки "Пополнить баланс"."""
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(callback.from_user.id, "На какую сумму в рублях?")


@dp.message_handler()
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


@dp.callback_query_handler(text_contains='confirm_amount:')
async def confirm_amount_button(callback: types.CallbackQuery):
    """Обработка кнопки подтверждения суммы пополнения."""
    amount = int(callback.data.split(':')[-1])
    bill = p2p.bill(bill_id=randint(100000,999999), amount=amount, lifetime=5)
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(
        callback.from_user.id,
        "Счет на оплату для пополнения баланса.",
        reply_markup=Button().confirm_payment(bill.pay_url, bill.bill_id),
        )

    while True:
        #status = p2p.check(bill.bill_id).status
        status = 'PAID'
        if status == 'WAITING':
            await asyncio.sleep(15)
            print(p2p.check(bill.bill_id).status)
        elif status == 'PAID':
            db.deposit(callback.from_user.id, amount, bill.bill_id) # Добавить что-то?
            break
        elif status == 'EXPIRED':
            await bot.send_message(callback.from_user.id,
            'Платежный документ просрочен. Вы можете создать новый.',
            reply_markup=Button().deposit,
            )
            break


@dp.callback_query_handler(text_contains='bill:')
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)