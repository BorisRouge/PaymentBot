from aiogram import types

class Button:
    def __init__(self):
        self.deposit = self.set_deposit
        self.manage_user = self.set_manage_user
        self.all_users = self.set_all_users
        self.confirm_amount = self.set_confirm_amount
        self.confirm_payment = self.set_confirm_payment
        self.cancel = self.set_cancel

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
        button = types.InlineKeyboardButton(text='Верно', callback_data=f'confirm_amount:{amount}')
        menu = types.InlineKeyboardMarkup(resize_keyboard=True).insert(button)        
        return menu

    @property
    def set_manage_user(self):
        balance_button = types.InlineKeyboardButton(text='Изменить баланс', callback_data='change_balance')
        ban_button = types.InlineKeyboardButton(text='Заблокировать пользователя', callback_data='ban_user')
        menu = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
        menu.insert(balance_button)
        menu.insert(ban_button)       
        return menu

    
    @property
    def set_all_users(self):
        button = types.InlineKeyboardButton(text='Выгрузить всех пользователей', callback_data='all_users')
        menu = types.InlineKeyboardMarkup(resize_keyboard=True).insert(button)
        return menu

    @property
    def set_cancel(self):
        button = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        menu = types.InlineKeyboardMarkup(resize_keyboard=True).insert(button)
        return menu
