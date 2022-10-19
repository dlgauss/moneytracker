import json
import pprint
import sqlite3

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



