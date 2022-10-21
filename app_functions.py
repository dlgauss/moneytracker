import json
import pprint
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime



def insert_one(user:str,type:str,category_1:str,category_2:str,summ:float,currency:str,comments:str,date_insert) -> None:

    query = f"""INSERT INTO money_tracer (created,user,type,category_1,category_2,summ,currency,comments) VALUES( '{date_insert}','{user}','{type}','{category_1}','{category_2}',{summ},'{currency}','{comments}');"""

    con = sqlite3.connect('./data/database.db')
    cursor = con.cursor()
    cursor.execute(query)
    con.commit()

def read_income_categories():
    with open('./data/categories_saving.json','r') as f:
        data = json.load(f)
    
    return data


def read_spend_categories():
    with open('./data/categories_expenses.json','r') as f:
        data = json.load(f)
    
    return data

def read_config():
    with open('./data/config.json','r') as f:
        data = json.load(f)
    
    return data


def daily_stats():
    con = sqlite3.connect('./data/database.db')
    cursor = con.cursor()
    return 'daily'


# def insert_one_google(user:str,type:str,category_1:str,category_2:str,summ:float,currency:str,comments:str,date_insert) -> None:
#     pass


def insert_one_google(list_for_insert:list) -> None:

    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('./data/gsheetconfig.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('MoneyTracker').worksheet("logs")
    sheet.append_rows([list_for_insert])
  
# insert_in_one_request(['test1','test2','test1','test2','test1','test2','test1','test2'])

def current_date_string():
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M")
    return dt_string

