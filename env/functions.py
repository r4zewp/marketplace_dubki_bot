import firebase_admin
from aiogram import types
from aiogram.dispatcher import FSMContext

from env.config import cert
from env.datasource.firebase_repository import FirebaseRepository
from env.forms.add_goods import *
from firebase_admin import firestore, credentials

fireRepo = FirebaseRepository()

async def add_good_name(message: types.Message, state: FSMContext):
    await AddGoods.name.set()
    await message.reply(text="Введите *название* товара", parse_mode=types.ParseMode.MARKDOWN)


async def add_good_description(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await AddGoods.description.set()
    await message.reply(text="Введите *описание* товара", parse_mode=types.ParseMode.MARKDOWN)


async def add_good_cost(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await AddGoods.cost.set()
    await message.reply(text="Введите *цену* товара", parse_mode=types.ParseMode.MARKDOWN)


async def add_good_photo(message: types.Message, state: FSMContext):
    await state.update_data(cost=message.text)
    await AddGoods.photo.set()
    await message.reply(text="Отправьте *одну фотографию* товара", parse_mode=types.ParseMode.MARKDOWN)


async def add_good_final(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1]["file_id"])
    stateRes = await state.get_data()
    await upload(stateRes, message.from_user.id)
    await message.reply(text=f"*Успешно!*\n\nДля продолжения введите команду */start*",
                        parse_mode=types.ParseMode.MARKDOWN)
    await state.finish()


async def upload(stateRes, uid):
    resReady = {
        "name": stateRes['name'],
        "description": stateRes['description'],
        "cost": stateRes['cost'],
        "photo": stateRes['photo'],
        'sentby': uid,
    }
    fireRepo.addGood(good=resReady)