from aiogram import types

class Button:
    def __init__(self):
        self.deposit = self.set_deposit
        self.confirm_amount = self.set_confirm_amount
        self.confirm_payment = self.set_confirm_payment

    @property
    def set_deposit(self):
        button = types.InlineKeyboardButton(text='Пополнить баланс', callback_data='deposit')
        menu = types.InlineKeyboardMarkup(resize_keyboard=True).insert(button)
        return menu

    
    def set_confirm_payment(self, url:str, bill_id:str):
        url_button = types.InlineKeyboardButton(text='Ссылка на платеж', url=url)
        check_button = types.InlineKeyboardButton(text='Статус платежа', callback_data='bill:'+bill_id)
        menu = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
        menu.insert(url_button)
        menu.insert(check_button)
        return menu
    
    
    def set_confirm_amount(self, amount:int):
        button = types.InlineKeyboardButton(text='Верно.', callback_data=f'confirm_amount:{amount}')
        menu = types.InlineKeyboardMarkup(resize_keyboard=True).insert(button)        
        return menu