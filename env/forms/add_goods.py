from aiogram.dispatcher.filters.state import State, StatesGroup


class AddGoods(StatesGroup):
    name = State()
    description = State()
    cost = State()
    photo = State()


