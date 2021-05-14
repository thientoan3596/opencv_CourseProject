import random
import sqlite3
from datetime import date, datetime, timedelta
import time
import math
import json

config = {}
with open('config.json', 'r') as f:
    config = json.load(f)
data_dict = {
    "raw_a": 0,
    "raw_b": 0,
    "processed_a": 0,
    "processed_b": 0,
    "scrap_a": 0,
    "scrap_b": 0,
    "completed_a": 0,
    "completed_b": 0,
    "total_completed": 0
}

db_name = config['database config']['name']
daily_table = config['database config']['big table']['name']
last_20mins_table = config['database config']['small table']['name']
updating_20mins_table_interval = config['others']['small table update interval']
updating_manufacture_table_interval = config['others']['big table update interval']
raw_input_per_minute = config['others']['generation']['estimate raw input per min']
defected_rate = config['others']['generation']['defect rate']
howlong = config['others']['generation']['days to be generated']

insert_command_for_daily_table = "INSERT INTO {table_name} (id,raw_a,raw_b,processed_a,processed_b,scrap_a,scrap_b,completed_a,completed_b,total_completed) VALUES ({year_month_day},{raw_a},{raw_b},{processed_a},{processed_b},{scrap_a},{scrap_b},{completed_a},{completed_b},{total_completed} )"
drop_table_command = "DROP TABLE IF EXISTS {table_name}"
create_big_table_command = """
    CREATE TABLE "{table_name}" (
	"{col0}"	INTEGER NOT NULL UNIQUE,
	"{col1}"	INTEGER NOT NULL,
	"{col2}"	INTEGER NOT NULL,
	"{col3}"	INTEGER NOT NULL,
	"{col4}"	INTEGER NOT NULL,
	"{col5}"	INTEGER NOT NULL,
	"{col6}"	INTEGER NOT NULL,
	"{col7}"	INTEGER NOT NULL,
	"{col8}"	INTEGER NOT NULL,
	"{col9}"	INTEGER NOT NULL
)
"""
create_small_table_command = """
    CREATE TABLE IF NOT EXISTS "{table_name}" (
	"{col0}"	INTEGER NOT NULL UNIQUE,
	"{col1}"	INTEGER,
	"{col2}"	INTEGER,
	"{col3}"	INTEGER NOT NULL,
	"{col4}"	INTEGER NOT NULL,
	"{col5}"	INTEGER NOT NULL,
	"{col6}"	INTEGER NOT NULL,
	"{col7}"	INTEGER NOT NULL,
	"{col8}"	INTEGER NOT NULL,
	"{col9}"	INTEGER NOT NULL
)
"""

generate_empty_small_table_commad = "INSERT INTO last_20_mins_record VALUES ({counter},0,0,0,0,0,0,0,0,0)"


def generate_val():
    data_dict["raw_a"] = random.randrange(
        raw_input_per_minute*1000, raw_input_per_minute*1500)
    data_dict["processed_a"] = data_dict["raw_a"]
    data_dict["scrap_a"] = random.randrange(
        0, math.floor(data_dict["raw_a"]*defected_rate))
    data_dict["completed_a"] = data_dict["processed_a"]-data_dict["scrap_a"]
    data_dict["raw_b"] = random.randrange(
        raw_input_per_minute*1000, raw_input_per_minute*1500)
    data_dict["processed_b"] = data_dict["raw_b"]
    data_dict["scrap_b"] = random.randrange(
        0, math.floor(data_dict["raw_b"]*defected_rate))
    data_dict["completed_b"] = data_dict["processed_b"]-data_dict["scrap_a"]
    data_dict["total_completed"] = data_dict["completed_a"] + \
        data_dict["completed_b"]


def generate_big_table():
    now = datetime.now()
    counter = 1
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute(drop_table_command.format(table_name=daily_table))
    connection.commit()
    cursor.execute(create_big_table_command.format(table_name=config['database config']['big table']['name'], col0=config['database config']['big table']['col0'], col1=config['database config']['big table']['col1'], col2=config['database config']['big table']['col2'], col3=config['database config']['big table']['col3'],
                                                   col4=config['database config']['big table']['col4'], col5=config['database config']['big table']['col5'], col6=config['database config']['big table']['col6'], col7=config['database config']['big table']['col7'], col8=config['database config']['big table']['col8'], col9=config['database config']['big table']['col9']))
    connection.commit()
    while counter < howlong:
        generate_val()
        temp = (now-timedelta(days=counter))
        cursor.execute(insert_command_for_daily_table.format(table_name=daily_table, year_month_day=temp.year*10000+temp.month*100+temp.day, raw_a=data_dict["raw_a"], raw_b=data_dict["raw_b"], processed_a=data_dict["processed_a"], processed_b=data_dict["processed_b"],
                                                             scrap_a=data_dict["scrap_a"], scrap_b=data_dict["scrap_b"], completed_a=data_dict["completed_a"], completed_b=data_dict["completed_b"], total_completed=data_dict["total_completed"]))
        connection.commit()
        counter += 1
    connection.close()
    print("Done")


def generate_small_table():
    counter = 0
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute(create_small_table_command.format(table_name=config['database config']['small table']['name'], col0=config['database config']['small table']['col0'], col1=config['database config']['small table']['col1'], col2=config['database config']['small table']['col2'], col3=config['database config']['small table']['col3'],
                                                     col4=config['database config']['small table']['col4'], col5=config['database config']['small table']['col5'], col6=config['database config']['small table']['col6'], col7=config['database config']['small table']['col7'], col8=config['database config']['small table']['col8'], col9=config['database config']['small table']['col9']))
    connection.commit()
    while counter < 20:
        cursor.execute(
            generate_empty_small_table_commad.format(counter=counter))
        connection.commit()
    connection.close()


generate_big_table()
# generate_small_table()
