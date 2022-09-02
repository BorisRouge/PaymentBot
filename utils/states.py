from aiogram.dispatcher.filters.state import StatesGroup, State


class StateDeposit(StatesGroup):
    D1 = State()
    D2 = State()


class StateAdmin(StatesGroup):
    A1 = State()
    A2 = State()