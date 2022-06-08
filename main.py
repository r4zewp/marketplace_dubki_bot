from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputMediaPhoto
from env.config import *
from kbs import *
from env.datasource.firebase_repository import *
from env.functions import *
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin

### creating bot instance
bot = Bot(token=token)

### initializing memory storage
storage = MemoryStorage()

### creating dispatcher instance in order to handle user messages
dp = Dispatcher(bot, storage=storage)

global loggedUser
global index
index = 0


### handling /start command
@dp.message_handler(commands=['start'])
async def greetings(message: types.Message):
    user_ref = fireRepo.client.collection(u'users').document(f'{message.from_user.id}')
    user = user_ref.get()
    if not user.exists:
        await message.answer("Для продолжения введите команду */reg*", parse_mode=types.ParseMode.MARKDOWN)
    else:
        global loggedUser
        loggedUser = user.to_dict()
        await message.answer(f"*Привет, {loggedUser['name']}!*\n\nКак проходит твой день?",
                             parse_mode=types.ParseMode.MARKDOWN, reply_markup=choice_kb)


### handling /reg command
@dp.message_handler(commands=['reg'])
async def handleReg(message=types.message):
    user_ref = fireRepo.client.collection(u'users').document(f'{message.from_user.id}')
    user = user_ref.get()
    if user.exists:
        global loggedUser
        loggedUser = user.to_dict()
        await bot.send_message(chat_id=loggedUser['uid'], text="*Вы уже зарегистрированы.*",
                               parse_mode=types.ParseMode.MARKDOWN)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               parse_mode=types.ParseMode.MARKDOWN,
                               text="Для регистрации поделись своим контактом с нами.\n*Добро пожаловать!*",
                               reply_markup=send_contact_kb)


dp.register_message_handler(add_good_name, commands="add", state="*")
dp.register_message_handler(add_good_description, state=AddGoods.name)
dp.register_message_handler(add_good_cost, state=AddGoods.description)
dp.register_message_handler(add_good_photo, state=AddGoods.cost)
dp.register_message_handler(add_good_final, state=AddGoods.photo, content_types=['photo'])


### handling contact reply
@dp.message_handler(content_types=['contact'])
async def handleContact(message=types.message):
    ### adding new user to db
    fireRepo.client.collection(u'users').document(f'{message.from_user.id}').set({
        "name": message.chat.username,
        "uid": message.from_user.id,
        "phoneNum": message.contact.phone_number,
        "is_admin": 0,
    })
    global loggedUser
    ### setting global user as logged
    loggedUser = {
        "name": message.chat.username,
        "uid": message.from_user.id,
        "phoneNum": message.contact.phone_number,
        "is_admin": 0,
    }
    await bot.send_message(chat_id=message.from_user.id, text=f"*Привет, {message.chat.username}!*\n\n"
                                                              f"Мы существуем для того, чтобы тебе было легче "
                                                              f"продавать свои вещи.\n"
                                                              f"Вот список команд, которые ты можешь использовать:\n\n"
                                                              f"~ */about* - расскажет тебе о нас, как и что работает.\n\n"
                                                              f"В дальнейшем ты можешь получить список команд при "
                                                              f"помощи команды */help*",
                           parse_mode=types.ParseMode.MARKDOWN,
                           reply_markup=choice_kb)


### handling button "sell" callback
@dp.callback_query_handler(lambda callback: callback.data == "sell")
async def handleSellCallback(message: types.message):
    user_ref = fireRepo.client.collection(u'users').document(f"{message.from_user.id}")
    user = user_ref.get()
    if user.exists:
        await bot.send_message(
            text="*Добро пожаловать в модуль добавления товара.*\n\nДля продолжения отправьте команду */add*",
            chat_id=message.from_user.id,
            parse_mode=types.ParseMode.MARKDOWN)
    else:
        await bot.send_message(text="*Вы не зарегистрированы в системе.*\n\nВведите */help* для ознакомления.",
                               parse_mode=types.ParseMode.MARKDOWN, chat_id=message.from_user.id)


### handling button "buy" callback
@dp.callback_query_handler(lambda callback: callback.data == "buy")
async def handleBuyCallback(message: types.message):
    user_ref = fireRepo.client.collection(u'users').document(f"{message.from_user.id}")
    user = user_ref.get()
    if user.exists:
        goods = fireRepo.getGoods(fireRepo.client)
        global index
        await bot.send_photo(photo=goods[index]['photo'], reply_markup=slider_kb,
                             chat_id=message.from_user.id,
                             parse_mode=types.ParseMode.MARKDOWN,
                             caption=f"*Название*: {goods[index]['name']}\n"
                                     f"*Описание*: {goods[index]['description']}\n"
                                     f"*Цена:* {goods[index]['cost']}")
    else:
        await bot.send_message(text="*Вы не зарегистрированы в системе.*\n\nВведите */help* для ознакомления.",
                               parse_mode=types.ParseMode.MARKDOWN, chat_id=message.from_user.id)


### handling next button callback
@dp.callback_query_handler(lambda callback: callback.data == "next")
async def handleNext(message=types.message):
    user_ref = fireRepo.client.collection(u'users').document(f'{message.from_user.id}')
    user = user_ref.get()
    goods = fireRepo.getGoods(fireRepo.client)
    ### slider
    global index
    if index == len(goods) - 1:
        index = 0
    else:
        index += 1
    ###
    if user.exists:
        global loggedUser
        loggedUser = user.to_dict()
        await bot.edit_message_media(message_id=message.message.message_id, chat_id=message.from_user.id,
                                     media=InputMediaPhoto(goods[index]['photo']))
        await bot.edit_message_caption(message_id=message.message.message_id, chat_id=message.from_user.id,
                                       caption=f"*Название*: {goods[index]['name']}\n"
                                               f"*Описание*: {goods[index]['description']}\n"
                                               f"*Цена:* {goods[index]['cost']}",
                                       parse_mode=types.ParseMode.MARKDOWN,
                                       reply_markup=slider_kb,
                                       )


### handling prev button callback
@dp.callback_query_handler(lambda callback: callback.data == "prev")
async def handlePrev(message=types.message):
    user_ref = fireRepo.client.collection(u'users').document(f'{message.from_user.id}')
    user = user_ref.get()
    goods = fireRepo.getGoods(fireRepo.client)
    ### slider
    global index
    if index == 0:
        index = len(goods) -1
    else:
        index -= 1
    ###
    if user.exists:
        global loggedUser
        loggedUser = user.to_dict()
        await bot.edit_message_media(message_id=message.message.message_id, chat_id=message.from_user.id,
                                     media=InputMediaPhoto(goods[index]['photo']))
        await bot.edit_message_caption(message_id=message.message.message_id, chat_id=message.from_user.id,
                                       caption=f"*Название*: {goods[index]['name']}\n"
                                               f"*Описание*: {goods[index]['description']}\n"
                                               f"*Цена:* {goods[index]['cost']}",
                                       parse_mode=types.ParseMode.MARKDOWN,
                                       reply_markup=slider_kb,
                                       )


### handling connect button callback
@dp.callback_query_handler(lambda callback: callback.data == "connect")
async def connectHandler(message=types.Message):
    goods = fireRepo.getGoods(fireRepo.client)
    global index
    userToConnect_ref = fireRepo.client.collection(u'users').document(f"{goods[index]['sentby']}")
    userToConnect_snap = userToConnect_ref.get()
    if userToConnect_snap.exists:
        userToConnect = userToConnect_snap.to_dict()
        await bot.send_message(text=f"*Для связи с продавцом используйте следующие реквизиты:*\n\n"
                                    f"*Username:* @{userToConnect['name']}\n"
                                    f"*Номер телефона:* {userToConnect['phoneNum']}",
                               chat_id=message.from_user.id,
                               parse_mode=types.ParseMode.MARKDOWN)


### handling /about command
@dp.message_handler(commands=['about'])
async def handleAbout(message=types.message):
    user_ref = fireRepo.client.collection(u'users').document(f'{message.from_user.id}')
    user = user_ref.get()
    if user.exists:
        loggedUser = user.to_dict()
        await bot.send_message(chat_id=loggedUser['uid'], text="*Я - курсовой проект Арустамова Тиграна.*\n\n"
                                                               "Основной идеей было показать, что возможно создать"
                                                               " площадку для продажи товаров без особо сложных решений."
                                                               "\n\n"
                                                               "*Все безопасно,*\n"
                                                               "*Быстро,*\n"
                                                               "*Удобно.*\n\n"
                                                               "*Надеюсь, у нас получилось тебя обрадовать!*",
                               parse_mode=types.ParseMode.MARKDOWN)


### handling /help command
@dp.message_handler(commands=['help'])
async def handleHelp(message=types.message):
    await bot.send_message(chat_id=message.from_user.id, text="*Список команд*:\n\n*/about* - узнать о нас больше",
                           parse_mode=types.ParseMode.MARKDOWN)


### handling unknown messages
@dp.message_handler()
async def handleUnknownMessages(message=types.message):
    user_ref = fireRepo.client.collection(u'users').document(f'{message.from_user.id}')
    user = user_ref.get()
    if not user:
        await bot.send_message(chat_id=message.from_user.id, text="Вы не зарегистрированы.\n\nВведите команду */reg*",
                               parse_mode=types.ParseMode.MARKDOWN)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="*Я не понимаю эту команду.*",
                               parse_mode=types.ParseMode.MARKDOWN)


### launching bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
