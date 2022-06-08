from aiogram import *
send_contact_kb = types.ReplyKeyboardMarkup().row(
    types.KeyboardButton(text="Поделиться контактом", callback_data="number", request_contact=True),
)

choice_kb = types.InlineKeyboardMarkup().row(
    types.InlineKeyboardButton(text="Купить", callback_data="buy"),
    types.InlineKeyboardButton(text="Продать", callback_data="sell")
)

slider_kb = types.InlineKeyboardMarkup().row(
    types.InlineKeyboardButton(text="<<", callback_data="prev"),
    types.InlineKeyboardButton(text="Связаться", callback_data="connect", pay=True),
    types.InlineKeyboardButton(text=">>", callback_data="next")
)