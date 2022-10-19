
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from app_functions import read_config

from app_functions import insert_one, read_income_categories,read_spend_categories
from datetime import datetime


INCOME_CATEGORIES = read_income_categories()
EXPENSES_CATEGORIES = read_spend_categories()
storage = MemoryStorage()

class AssetState(StatesGroup):
    asset_type = State()
    asset_category_1 = State()
    asset_category_2 = State()
    asset_summ = State()
    asset_currency = State()
    asset_comment = State()
    asset_if_yes = State()

class AssetStateSpend(StatesGroup):
    asset_type = State()
    asset_category_1 = State()
    asset_category_2 = State()
    asset_summ = State()
    asset_currency = State()
    asset_comment = State()
    asset_if_yes = State()



conf = read_config()

API_TOKEN  = conf[0]['TOKEN']
acl=conf[0]['ACL']
 
logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,storage=storage)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
   
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

@dp.message_handler(commands=['spend'])
async def send_welcome(message: types.Message):
    await message.reply("Hi you will start to add income operation")



@dp.message_handler(commands=['income'])
async def send_welcome(message: types.Message):
    await message.reply("Hi you will start to add expense operation")



@dp.message_handler()
async def echo(message: types.Message):
    track_menu = InlineKeyboardMarkup()
    spend = InlineKeyboardButton(text="Spend",callback_data="spend")
    income = InlineKeyboardButton(text="Income",callback_data="income")
    track_menu.insert(spend)
    track_menu.insert(income)
    user_id = message.from_user.id
    if user_id in acl:
        await bot.send_message(message.from_user.id,f"Please choose one:",reply_markup=track_menu)
    else:
        await bot.send_message(message.from_user.id,f"Sorry. You are not in white list.")
#  INCOME 
@dp.callback_query_handler(text='income')
async def income(message: types.Message,state:FSMContext):
    


    await AssetState.asset_type.set()
    asset_type = 'income'
    await state.update_data(asset_type=asset_type)

    income_menu =  InlineKeyboardMarkup(resize_keyboard=True)
    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    for category in INCOME_CATEGORIES[0]['ro']:
        button_income = KeyboardButton(category)
    
        greet_kb.add(button_income)
    


    await bot.send_message(message.from_user.id,'Type: Income')
    await bot.send_message(message.from_user.id,"Please select Category 1",reply_markup=greet_kb)
    await AssetState.next()

@dp.message_handler(state=AssetState.asset_category_1)
async def get_cat_1_income(message: types.Message,state:FSMContext): 
    asset_category_1=message.text
    
    await state.update_data(asset_category_1=asset_category_1)

    fields = INCOME_CATEGORIES[0]['ro'][asset_category_1]

    cat_2_kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)

    for cat in fields:
        button_income = KeyboardButton(cat)
        cat_2_kb.add(button_income)

    await bot.send_message(message.from_user.id,"Please select Category 2",reply_markup=cat_2_kb)
    await AssetState.next()

@dp.message_handler(state=AssetState.asset_category_2)
async def get_data(message: types.Message,state:FSMContext): 
    asset_category_2=message.text

    await state.update_data(asset_category_2=asset_category_2)
    await bot.send_message(message.from_user.id,"Please enter summ")
    await AssetState.next()


@dp.message_handler(state=AssetState.asset_summ)
async def get_data(message: types.Message,state:FSMContext): 
    asset_summ=message.text
    
    await state.update_data(asset_summ=asset_summ)

    currencies = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    mdl = KeyboardButton('MDL')
    eur = KeyboardButton('EUR')
    usd = KeyboardButton('USD')
    currencies.add(mdl)
    currencies.add(eur)
    currencies.add(usd)
    await bot.send_message(message.from_user.id,"Please select currency",reply_markup=currencies)

    await AssetState.next()

@dp.message_handler(state=AssetState.asset_currency)
async def get_data(message: types.Message,state:FSMContext): 
    asset_currency=message.text
    
    await state.update_data(asset_currency=asset_currency)
    
    y_n = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    yes = KeyboardButton('Yes')
    no = KeyboardButton('No')
    y_n.add(yes)
    y_n.add(no)

    await bot.send_message(message.from_user.id,"Add Comments ?",reply_markup=y_n)
    
    await AssetState.next()



@dp.message_handler(state=AssetState.asset_comment)
async def get_data(message: types.Message,state:FSMContext): 
    asset_comment=message.text
    if asset_comment == 'No':

        await state.update_data(asset_comment='')
        
        data = await state.get_data()
        cat1 = data['asset_category_1']
        cat2 = data['asset_category_2']
        summ = data['asset_summ']
        currency = data['asset_currency']
        comment = data['asset_comment']
        oper_type = data['asset_type']
        insert_one(
        user=message.from_user.first_name,
        type=oper_type,
        category_1=cat1,
        category_2=cat2,
        summ=summ,
        currency=currency,
        comments=comment,
        date_insert=datetime.now()
    )
        await bot.send_message(message.from_user.id,f"Has been succesfully added:\nOpperation type: {oper_type}\nCat 1{cat1}\nCat 2{cat2}\nSumm: {summ}\nCurrency: {currency}\nComment: {comment}")   
        await state.finish()

    else:
        await state.update_data(asset_comment='')
        await bot.send_message(message.from_user.id,"Type comment")
        await AssetState.next()
        

@dp.message_handler(state=AssetState.asset_if_yes)
async def update_in_db(message: types.Message,state:FSMContext):
    
    comment = message.text
    
    await state.update_data(asset_if_yes=comment)

    data = await state.get_data()
    cat1 = data['asset_category_1']
    cat2 = data['asset_category_2']
    summ = data['asset_summ']
    currency = data['asset_currency']
    oper_type = data['asset_type']
    insert_one(
        user=message.from_user.first_name,
        type=oper_type,
        category_1=cat1,
        category_2=cat2,
        summ=summ,
        currency=currency,
        comments=comment,
        date_insert=datetime.now()
    )
    await bot.send_message(message.from_user.id,f"Has been succesfully added:\nOpperation type: {oper_type}\nCat 1{cat1}\nCat 2{cat2}\nSumm: {summ}\nCurrency: {currency}\nComment: {comment}")
    await state.finish()



# @dp.callback_query_handler(text='spend')
# async def income(message: types.Message,state:FSMContext):
#     await bot.send_message(message.from_user.id,'Type: Spend')

#  SPEND

@dp.callback_query_handler(text='spend')
async def income(message: types.Message,state:FSMContext):
   
    await AssetStateSpend.asset_type.set()
    asset_type = 'spend'
    await state.update_data(asset_type=asset_type)
 
    income_menu =  InlineKeyboardMarkup(resize_keyboard=True)
    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    for category in EXPENSES_CATEGORIES[0]['ro']:
        button_income = KeyboardButton(category)
    
        greet_kb.add(button_income)
    


    await bot.send_message(message.from_user.id,'Type: Spend')
    await bot.send_message(message.from_user.id,"Please select Category 1",reply_markup=greet_kb)
    await AssetStateSpend.next()

@dp.message_handler(state=AssetStateSpend.asset_category_1)
async def get_cat_1_income(message: types.Message,state:FSMContext): 
    asset_category_1=message.text
    
    await state.update_data(asset_category_1=asset_category_1)

    fields = EXPENSES_CATEGORIES[0]['ro'][asset_category_1]

    cat_2_kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)

    for cat in fields:
        button_income = KeyboardButton(cat)
        cat_2_kb.add(button_income)

    await bot.send_message(message.from_user.id,"Please select Category 2",reply_markup=cat_2_kb)
    await AssetStateSpend.next()

@dp.message_handler(state=AssetStateSpend.asset_category_2)
async def get_data(message: types.Message,state:FSMContext): 
    asset_category_2=message.text

    await state.update_data(asset_category_2=asset_category_2)
    await bot.send_message(message.from_user.id,"Please enter summ")
    await AssetStateSpend.next()


@dp.message_handler(state=AssetStateSpend.asset_summ)
async def get_data(message: types.Message,state:FSMContext): 
    asset_summ=message.text
    
    await state.update_data(asset_summ=asset_summ)

    currencies = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    mdl = KeyboardButton('MDL')
    eur = KeyboardButton('EUR')
    usd = KeyboardButton('USD')
    currencies.add(mdl)
    currencies.add(eur)
    currencies.add(usd)
    await bot.send_message(message.from_user.id,"Please select currency",reply_markup=currencies)

    await AssetStateSpend.next()

@dp.message_handler(state=AssetStateSpend.asset_currency)
async def get_data(message: types.Message,state:FSMContext): 
    asset_currency=message.text
    
    await state.update_data(asset_currency=asset_currency)
    
    y_n = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    yes = KeyboardButton('Yes')
    no = KeyboardButton('No')
    y_n.add(yes)
    y_n.add(no)

    await bot.send_message(message.from_user.id,"Add Comments ?",reply_markup=y_n)
    
    await AssetStateSpend.next()



@dp.message_handler(state=AssetStateSpend.asset_comment)
async def get_data(message: types.Message,state:FSMContext): 
    asset_comment=message.text
    if asset_comment == 'No':

        await state.update_data(asset_comment='')
        
        data = await state.get_data()
        cat1 = data['asset_category_1']
        cat2 = data['asset_category_2']
        summ = data['asset_summ']
        currency = data['asset_currency']
        comment = data['asset_comment']
        oper_type = data['asset_type']
        
        insert_one(
        user=message.from_user.first_name,
        type=oper_type,
        category_1=cat1,
        category_2=cat2,
        summ=summ,
        currency=currency,
        comments=comment,
        date_insert=datetime.now()
    )
        await bot.send_message(message.from_user.id,f"Has been succesfully added:\nOpperation type: {oper_type}\nCat 1{cat1}\nCat 2{cat2}\nSumm: {summ}\nCurrency: {currency}\nComment: {comment}") 

        await state.finish()

    else:
        await state.update_data(asset_comment='')
        await bot.send_message(message.from_user.id,"Type comment")
        await AssetStateSpend.next()
        

@dp.message_handler(state=AssetStateSpend.asset_if_yes)
async def update_in_db(message: types.Message,state:FSMContext):
    
    comment = message.text
    
    await state.update_data(asset_if_yes=comment)

    data = await state.get_data()
    cat1 = data['asset_category_1']
    cat2 = data['asset_category_2']
    summ = data['asset_summ']
    currency = data['asset_currency']
    oper_type = data['asset_type']
    # insert_one(user:str,type:str,category_1:str,category_2:str,summ:float,currency:str,comments:str,date_insert)
    insert_one(
        user=message.from_user.first_name,
        type=oper_type,
        category_1=cat1,
        category_2=cat2,
        summ=summ,
        currency=currency,
        comments=comment,
        date_insert=datetime.now()
    )
    await bot.send_message(message.from_user.id,f"Has been succesfully added:\nOpperation type: {oper_type}\nCat 1{cat1}\nCat 2{cat2}\nSumm: {summ}\nCurrency: {currency}\nComment: {comment}")
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)