from datetime import datetime
from sqlite3.dbapi2 import Cursor
from cv2 import cv2
from tracker import *
import numpy as np
import time
import sqlite3
import threading
import json

# Loads config file
config = {}
with open('config.json', 'r') as f:
    config = json.load(f)
# Global Constant
# region


now = datetime.today()
today = [now.date()]
quit = [False]
db_name = config['database config']['name']
daily_table = config['database config']['big table']['name']
last_20mins_table = config['database config']['small table']['name']
updating_20mins_table_interval = config['others']['small table update interval']
updating_manufacture_table_interval = config['others']['big table update interval']
speed = config['others']['simulation speed']
key_pause = config['others']['keys']['pause']
key_fast = config['others']['keys']['speed up']
key_slow = config['others']['keys']['speed down']
key_quit = config['others']['keys']['quit']
debug_mode = False
# Colors BGR
# region
color_yellow = (config['others']['colors']['yellow']['b'], config['others']
                ['colors']['yellow']['g'], config['others']['colors']['yellow']['r'])
color_red = (config['others']['colors']['red']['b'], config['others']
             ['colors']['red']['g'], config['others']['colors']['red']['r'])
color_blue = (config['others']['colors']['blue']['b'], config['others']
              ['colors']['blue']['g'], config['others']['colors']['blue']['r'])
color_green = (config['others']['colors']['green']['b'], config['others']
               ['colors']['green']['g'], config['others']['colors']['green']['r'])
color_white = (config['others']['colors']['white']['b'], config['others']
               ['colors']['white']['g'], config['others']['colors']['white']['r'])
color_orange = (config['others']['colors']['orange']['b'], config['others']
                ['colors']['orange']['g'], config['others']['colors']['orange']['r'])
color_pink = (config['others']['colors']['pink']['b'], config['others']
              ['colors']['pink']['g'], config['others']['colors']['pink']['r'])
color_black = (config['others']['colors']['black']['b'], config['others']
               ['colors']['black']['g'], config['others']['colors']['black']['r'])
# endregion

# Colors limits
# region
# Yellow

lower_yellow = np.array([config['others']['hsv color limits']['yellow']['lower']['h'], config['others']
                         ['hsv color limits']['yellow']['lower']['s'], config['others']['hsv color limits']['yellow']['lower']['v']])
upper_yellow = np.array([config['others']['hsv color limits']['yellow']['upper']['h'], config['others']
                         ['hsv color limits']['yellow']['upper']['s'], config['others']['hsv color limits']['yellow']['upper']['v']])
# Blue
lower_blue = np.array([config['others']['hsv color limits']['blue']['lower']['h'], config['others']
                       ['hsv color limits']['blue']['lower']['s'], config['others']['hsv color limits']['blue']['lower']['v']])
upper_blue = np.array([config['others']['hsv color limits']['blue']['upper']['h'], config['others']
                       ['hsv color limits']['blue']['upper']['s'], config['others']['hsv color limits']['blue']['upper']['v']])
# Green
lower_green = np.array([config['others']['hsv color limits']['green']['lower']['h'], config['others']
                        ['hsv color limits']['green']['lower']['s'], config['others']['hsv color limits']['green']['lower']['v']])
upper_green = np.array([config['others']['hsv color limits']['green']['upper']['h'], config['others']
                        ['hsv color limits']['green']['upper']['s'], config['others']['hsv color limits']['green']['upper']['v']])
# Red
lower_red = np.array([config['others']['hsv color limits']['red']['lower']['h'], config['others']
                      ['hsv color limits']['red']['lower']['s'], config['others']['hsv color limits']['red']['lower']['v']])
upper_red = np.array([config['others']['hsv color limits']['red']['upper']['h'], config['others']
                      ['hsv color limits']['red']['upper']['s'], config['others']['hsv color limits']['red']['upper']['v']])
# Cyan
lower_cyan = np.array([config['others']['hsv color limits']['cyan']['lower']['h'], config['others']
                       ['hsv color limits']['cyan']['lower']['s'], config['others']['hsv color limits']['cyan']['lower']['v']])
upper_cyan = np.array([config['others']['hsv color limits']['cyan']['upper']['h'], config['others']
                       ['hsv color limits']['cyan']['upper']['s'], config['others']['hsv color limits']['cyan']['upper']['v']])
# Pink
lower_pink = np.array([config['others']['hsv color limits']['pink']['lower']['h'], config['others']
                       ['hsv color limits']['pink']['lower']['s'], config['others']['hsv color limits']['pink']['lower']['v']])
upper_pink = np.array([config['others']['hsv color limits']['pink']['upper']['h'], config['others']
                       ['hsv color limits']['pink']['upper']['s'], config['others']['hsv color limits']['pink']['upper']['v']])
# Orange
lower_orange = np.array([config['others']['hsv color limits']['orange']['lower']['h'], config['others']
                         ['hsv color limits']['orange']['lower']['s'], config['others']['hsv color limits']['orange']['lower']['v']])
upper_orange = np.array([config['others']['hsv color limits']['orange']['upper']['h'], config['others']
                         ['hsv color limits']['orange']['upper']['s'], config['others']['hsv color limits']['orange']['upper']['v']])
# endregion
# Trackers
# region
tracker_at_rawA = EuclideanDistTracker()
tracker_at_rawB = EuclideanDistTracker()
tracker_at_processA = EuclideanDistTracker()
tracker_at_processB = EuclideanDistTracker()
tracker_at_completedA = EuclideanDistTracker()
tracker_at_completedB = EuclideanDistTracker()
tracker_at_combined = EuclideanDistTracker()
tracker_at_scrapsA = EuclideanDistTracker()
tracker_at_scrapsB = EuclideanDistTracker()
# endregion

# endregion

# Global Variables
# region
data_current_date_dict = {
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
data_latest_update_20mins_dict = {
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

data_current_run_dict = {
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

counter_20mins_table = 0
# endregion

# Sqlite Commands
# region
update_20mins_table_command = "UPDATE {table} SET raw_a={raw_a},raw_b = {raw_b}, processed_a = {processed_a}, processed_b={processed_b}, scrap_a={scrap_a},scrap_b={scrap_b}, completed_a={completed_a},completed_b={completed_b},total_completed={total_completed} WHERE id={id} "
upsert_command_for_daily_table = "INSERT OR REPLACE INTO {table_name} (id,raw_a,raw_b,processed_a,processed_b,scrap_a,scrap_b,completed_a,completed_b,total_completed) VALUES ({year_month_day},{raw_a},{raw_b},{processed_a},{processed_b},{scrap_a},{scrap_b},{completed_a},{completed_b},{total_completed} )"
querry_data_command = "SELECT * FROM {table_name} WHERE id = {year_month_day} ; "
# endregion

# Functions

# region


def debug_pannel(frame):
    # Trackbar
    l_h_val = 84
    l_s_val = 73
    l_v_val = 52
    u_h_val = 87
    u_s_val = 255
    u_v_val = 255
    cv2.namedWindow("Trackbars")
    cv2.createTrackbar("L-H", "Trackbars", l_h_val, 180, nothing)
    cv2.createTrackbar("L-S", "Trackbars", l_s_val, 255, nothing)
    cv2.createTrackbar("L-V", "Trackbars", l_v_val, 255, nothing)
    cv2.createTrackbar("U-H", "Trackbars", u_h_val, 180, nothing)
    cv2.createTrackbar("U-S", "Trackbars", u_s_val, 255, nothing)
    cv2.createTrackbar("U-V", "Trackbars", u_v_val, 255, nothing)

    # Frame masking for testing
    l_h = cv2.getTrackbarPos("L-H", "Trackbars")
    l_s = cv2.getTrackbarPos("L-S", "Trackbars")
    l_v = cv2.getTrackbarPos("L-V", "Trackbars")
    u_h = cv2.getTrackbarPos("U-H", "Trackbars")
    u_s = cv2.getTrackbarPos("U-S", "Trackbars")
    u_v = cv2.getTrackbarPos("U-V", "Trackbars")
    lower_color = np.array([l_h, l_s, l_v])
    upper_color = np.array([u_h, u_s, u_v])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)

    return mask


def fetch_current_day_from_DB(command):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    now = datetime.today()
    cursor.execute(command.format(table_name=daily_table,
                                  year_month_day=now.year*10000+now.month*100+now.day))
    temp = cursor.fetchall()
    if len(temp) > 1:
        print("Database Error")
        quit[0] = True
    if len(temp) == 1:
        _, data_current_date_dict['raw_a'], data_current_date_dict['raw_b'], data_current_date_dict['processed_a'], data_current_date_dict['processed_b'], data_current_date_dict[
            'scrap_a'], data_current_date_dict['scrap_b'], data_current_date_dict['completed_a'], data_current_date_dict['completed_b'], data_current_date_dict['total_completed'] = temp[0]
    connection.close()


def clear_20mins_table(command):
    id = 0
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    while id < 20:

        cursor.execute(command.format(table=last_20mins_table, raw_a=0, raw_b=0, processed_a=0, processed_b=0,
                                      scrap_a=0, scrap_b=0, completed_a=0, completed_b=0, total_completed=0, id=id))
        connection.commit()
        id += 1
    connection.close()


def update_20mins_table(command, delay):
    clear_20mins_table(command)
    id = 0
    t1 = time.perf_counter()
    while not quit[0]:
        if time.perf_counter()-t1 > delay:
            connection = sqlite3.connect(db_name)
            cursor = connection.cursor()
            cursor.execute(command.format(table=last_20mins_table, raw_a=data_latest_update_20mins_dict["raw_a"], raw_b=data_latest_update_20mins_dict["raw_b"], processed_a=data_latest_update_20mins_dict["processed_a"], processed_b=data_latest_update_20mins_dict["processed_b"],
                                          scrap_a=data_latest_update_20mins_dict["scrap_a"], scrap_b=data_latest_update_20mins_dict["scrap_b"], completed_a=data_latest_update_20mins_dict["completed_a"], completed_b=data_latest_update_20mins_dict["completed_b"], total_completed=data_latest_update_20mins_dict["total_completed"], id=id))
            connection.commit()
            connection.close()
            reset_dictionary(data_latest_update_20mins_dict)
            id += 1
            if id > 19:
                id = 0
            t1 = time.perf_counter()
        time.sleep(1)


def update_daily_table(command, delay):
    t1 = time.perf_counter()
    while not quit[0]:
        if time.perf_counter()-t1 > delay:
            connection = sqlite3.connect(db_name)
            cursor = connection.cursor()
            # Execut comman
            now = datetime.today()
            cursor.execute(command.format(table_name=daily_table, year_month_day=now.year*10000+now.month*100+now.day, raw_a=data_current_date_dict["raw_a"], raw_b=data_current_date_dict["raw_b"], processed_a=data_current_date_dict["processed_a"], processed_b=data_current_date_dict["processed_b"],
                                          scrap_a=data_current_date_dict["scrap_a"], scrap_b=data_current_date_dict["scrap_b"], completed_a=data_current_date_dict["completed_a"], completed_b=data_current_date_dict["completed_b"], total_completed=data_current_date_dict["total_completed"]))
            connection.commit()
            connection.close()
            if today[0] != now.date():
                today[0] = now.date()
                reset_dictionary(data_current_date_dict)
            t1 = time.perf_counter()
        time.sleep(1)


def nothing(x):
    pass


def reset_dictionary(dictionary_to_be_reset):
    dictionary_to_be_reset['raw_a'] = 0
    dictionary_to_be_reset['raw_b'] = 0
    dictionary_to_be_reset['processed_a'] = 0
    dictionary_to_be_reset['processed_b'] = 0
    dictionary_to_be_reset['scrap_a'] = 0
    dictionary_to_be_reset['scrap_b'] = 0
    dictionary_to_be_reset['completed_a'] = 0
    dictionary_to_be_reset['completed_b'] = 0
    dictionary_to_be_reset['total_completed'] = 0


def end_all_threads():
    quit[0] = True
    print("Terminated ...")


def manufacturing_detector():
    # Initializing
    speed = 80
    cap = cv2.VideoCapture(config['others']['video file name'])
    while True:
        ret, frame = cap.read()

        # The below line is for capture video only, remove when real-time camera is used
        if not ret:
            end_all_threads()
            break

        # Set up different rois
        rawA = frame[470:550, 280:350]
        rawB = frame[420:530, 600:650]
        processA = frame[550:650, 600:750]
        processB = frame[450:550, 880:1010]
        scrapA = frame[800:1000, 550:800]
        scrapB = frame[400:525, 1200:1400]
        completedA = frame[650:750, 980:1100]
        completedB = frame[550:600, 1080:1300]
        completedCombine = frame[680:780, 1400:1600]

        # Testing Only

        if debug_mode:
            debug_mask = debug_pannel(frame)
            cv2.imshow("Debug-Mask", debug_mask)

        # hsv masking and finding contours
        # region
        # Section A
        # Raw materials input
        hsv_rawA = cv2.cvtColor(rawA, cv2.COLOR_BGR2HSV)
        mask_rawA = cv2.inRange(hsv_rawA, lower_yellow, upper_yellow)
        contours_in_rawA, _ = cv2.findContours(
            mask_rawA, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # After being processed
        hsv_processA = cv2.cvtColor(processA, cv2.COLOR_BGR2HSV)
        mask_processA = cv2.inRange(hsv_processA, lower_red, upper_red)
        contours_in_processA, _ = cv2.findContours(
            mask_processA, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Non-defected
        hsv_completedA = cv2.cvtColor(completedA, cv2.COLOR_BGR2HSV)
        mask_completedA = cv2.inRange(hsv_completedA, lower_red, upper_red)
        contours_in_completedA, _ = cv2.findContours(
            mask_completedA, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Scraps
        hsv_scrapA = cv2.cvtColor(scrapA, cv2.COLOR_BGR2HSV)
        mask_scrapA = cv2.inRange(hsv_scrapA, lower_orange, upper_orange)
        contours_in_scrapA, _ = cv2.findContours(
            mask_scrapA, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Section B
        # Raw materials input
        hsv_rawB = cv2.cvtColor(rawB, cv2.COLOR_BGR2HSV)
        mask_rawB = cv2.inRange(hsv_rawB, lower_red, upper_red)
        contours_in_rawB, _ = cv2.findContours(
            mask_rawB, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # After being processed
        hsv_processB = cv2.cvtColor(processB, cv2.COLOR_BGR2HSV)
        mask_processB = cv2.inRange(hsv_processB, lower_green, upper_green)
        contours_in_processB, _ = cv2.findContours(
            mask_processB, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Scraps
        hsv_scrapB = cv2.cvtColor(scrapB, cv2.COLOR_BGR2HSV)
        mask_scrapB = cv2.inRange(hsv_scrapB, lower_pink, upper_pink)
        contours_in_scrapB, _ = cv2.findContours(
            mask_scrapB, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # non-defected
        hsv_completedB = cv2.cvtColor(completedB, cv2.COLOR_BGR2HSV)
        mask_completedB = cv2.inRange(hsv_completedB, lower_green, upper_green)
        contours_in_completedB, _ = cv2.findContours(
            mask_completedB, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Region of combine completed products

        hsv_combined = cv2.cvtColor(completedCombine, cv2.COLOR_BGR2HSV)
        mask_combined = cv2.inRange(hsv_combined, lower_cyan, upper_cyan)
        contours_in_combined, _ = cv2.findContours(
            mask_combined, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # endregion

        # Detections arrays for each regions

        detections_at_rawA = []
        detections_at_rawB = []
        detections_at_processA = []
        detections_at_processB = []
        detections_at_completedA = []
        detections_at_completedB = []
        detections_at_scraps_A = []
        detections_at_scraps_B = []
        detections_at_combined = []
        # Findout contours

        # region
        for cnt in contours_in_rawA:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                detections_at_rawA.append([x, y, w, h])

        for cnt in contours_in_rawB:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                detections_at_rawB.append([x, y, w, h])

        for cnt in contours_in_processA:
            area = cv2.contourArea(cnt)
            if area > 250:
                x, y, w, h = cv2.boundingRect(cnt)
                detections_at_processA.append([x, y, w, h])

        for cnt in contours_in_processB:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                detections_at_processB.append([x, y, w, h])

        for cnt in contours_in_scrapA:
            area = cv2.contourArea(cnt)
            if area > 250:
                x, y, w, h = cv2.boundingRect(cnt)
                detections_at_scraps_A.append([x, y, w, h])

        for cnt in contours_in_scrapB:
            area = cv2.contourArea(cnt)
            if area > 250:
                x, y, w, h = cv2.boundingRect(cnt)
                detections_at_scraps_B.append([x, y, w, h])

        for cnt in contours_in_completedA:
            area = cv2.contourArea(cnt)
            if area > 250:
                x, y, w, h = cv2.boundingRect(cnt)
                detections_at_completedA.append([x, y, w, h])

        for cnt in contours_in_completedB:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                detections_at_completedB.append([x, y, w, h])

        for cnt in contours_in_combined:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                detections_at_combined.append([x, y, w, h])
        # endregion

        # Updating trackers

        # region
        raw_materials_A = tracker_at_rawA.update(detections_at_rawA)
        raw_materials_B = tracker_at_rawB.update(detections_at_rawB)

        processed_products_A = tracker_at_processA.update(
            detections_at_processA)
        processed_products_B = tracker_at_processB.update(
            detections_at_processB)

        scraps_A = tracker_at_scrapsA.update(detections_at_scraps_A)
        scraps_B = tracker_at_scrapsB.update(detections_at_scraps_B)

        completed_products_A = tracker_at_completedA.update(
            detections_at_completedA)
        completed_products_B = tracker_at_completedB.update(
            detections_at_completedB)

        total_finished_products = tracker_at_combined.update(
            detections_at_combined)
        # endregion

        # Putting text and update counters
        # Section A
        # raw materials
        for raw_material in raw_materials_A:
            x, y, w, h, id = raw_material
            cv2.rectangle(rawA, (x, y), (x+w, y+h), color_black, 2)
            cv2.putText(rawA, str(id), (x + w//2, y+h//2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, color_red, 2)
            if data_current_run_dict['raw_a'] < id and data_current_run_dict['raw_a'] + 1 == id:
                data_current_run_dict['raw_a'] += 1
                data_current_date_dict['raw_a'] += 1
                data_latest_update_20mins_dict['raw_a'] += 1
        # After being processed
        for product in processed_products_A:
            x, y, w, h, id = product
            cv2.rectangle(processA, (x, y), (x+w, y+h), color_black, 2)
            cv2.putText(processA, str(id), (x + w//2, y+h//2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, color_red, 2)
            if data_current_run_dict['processed_a'] < id and data_current_run_dict['processed_a'] + 1 == id:
                data_current_run_dict['processed_a'] += 1
                data_current_date_dict['processed_a'] += 1
                data_latest_update_20mins_dict['processed_a'] += 1
        # Scraps
        for scrap in scraps_A:
            x, y, w, h, id = scrap
            cv2.rectangle(scrapA, (x, y), (x+w, y+h), color_black, 2)
            cv2.putText(scrapA, str(id), (x + w//2, y+h//2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, color_blue, 2)
            if data_current_run_dict['scrap_a'] < id and data_current_run_dict['scrap_a'] + 1 == id:
                data_current_run_dict['scrap_a'] += 1
                data_current_date_dict['scrap_a'] += 1
                data_latest_update_20mins_dict['scrap_a'] += 1
        # Non-defected
        for product in completed_products_A:
            x, y, w, h, id = product
            cv2.rectangle(completedA, (x, y), (x+w, y+h), color_black, 2)
            cv2.putText(completedA, str(id), (x + w//2, y+h//2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, color_red, 2)
            if data_current_run_dict['completed_a'] < id and data_current_run_dict['completed_a'] + 1 == id:
                data_current_run_dict['completed_a'] += 1
                data_current_date_dict['completed_a'] += 1
                data_latest_update_20mins_dict['completed_a'] += 1

        # Section B
        # Raw Material
        for raw_material in raw_materials_B:
            x, y, w, h, id = raw_material
            cv2.rectangle(rawB, (x, y), (x+w, y+h), color_black, 2)
            cv2.putText(rawB, str(id), (x + w//2, y+h//2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, color_blue, 2)
            if data_current_run_dict['raw_b'] < id and data_current_run_dict['raw_b'] + 1 == id:
                data_current_run_dict['raw_b'] += 1
                data_current_date_dict['raw_b'] += 1
                data_latest_update_20mins_dict['raw_b'] += 1

        # After being processed
        for product in processed_products_B:
            x, y, w, h, id = product
            cv2.putText(processB, str(id), (x + w//2, y+h//2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, color_red, 2)
            cv2.rectangle(processB, (x, y),  (x+w, y+h), color_black, 2)
            if data_current_run_dict['processed_b'] < id and data_current_run_dict['processed_b'] + 1 == id:
                data_current_run_dict['processed_b'] += 1
                data_current_date_dict['processed_b'] += 1
                data_latest_update_20mins_dict['processed_b'] += 1
        # Scraps
        for scrap in scraps_B:
            x, y, w, h, id = scrap
            cv2.rectangle(scrapB, (x, y), (x+w, y+h), color_black, 2)
            cv2.putText(scrapB, str(id), (x + w//2, y+h//2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, color_red, 2)
            if data_current_run_dict['scrap_b'] < id and data_current_run_dict['scrap_b'] + 1 == id:
                data_current_run_dict['scrap_b'] += 1
                data_current_date_dict['scrap_b'] += 1
                data_latest_update_20mins_dict['scrap_b'] += 1
        # Non-defected
        for product in completed_products_B:
            x, y, w, h, id = product
            cv2.putText(completedB, str(id), (x + w//2, y+h//2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, color_red, 2)
            cv2.rectangle(completedB, (x, y), (x+w, y+h), color_black, 2)
            if data_current_run_dict['completed_b'] < id and data_current_run_dict['completed_b'] + 1 == id:
                data_current_run_dict['completed_b'] += 1
                data_current_date_dict['completed_b'] += 1
                data_latest_update_20mins_dict['completed_b'] += 1

        # Total finished product for double checking
        for product in total_finished_products:
            x, y, w, h, id = product
            cv2.putText(completedCombine, str(id), (x + w//2, y+h//2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, color_red, 2)
            cv2.rectangle(completedCombine, (x, y), (x+w, y+h), color_black, 2)
            if data_current_run_dict['total_completed'] < id and data_current_run_dict['total_completed'] + 1 == id:
                data_current_run_dict['total_completed'] += 1
                data_current_date_dict['total_completed'] += 1
                data_latest_update_20mins_dict['total_completed'] += 1

        # Edit display on main frame
        # region
        cv2.putText(frame, "raw materials A:  " + str(data_current_run_dict['raw_a']), (5, 25),
                    cv2.FONT_HERSHEY_COMPLEX, 1, color_yellow, 2)
        cv2.putText(frame, "raw materials B:  " + str(data_current_run_dict['raw_b']), (5, 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, color_red, 2)
        cv2.putText(frame, "processed products A:  " + str(data_current_run_dict['processed_a']), (400, 25),
                    cv2.FONT_HERSHEY_COMPLEX, 1, color_blue, 2)
        cv2.putText(frame, "scraps A:  " + str(data_current_run_dict['scrap_a']), (400, 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, color_orange, 2)
        cv2.putText(frame, "processed products B:  " + str(data_current_run_dict['processed_b']), (400, 75),
                    cv2.FONT_HERSHEY_COMPLEX, 1, color_green, 2)
        cv2.putText(frame, "scraps B:  " + str(data_current_run_dict['scrap_b']), (400, 100),
                    cv2.FONT_HERSHEY_COMPLEX, 1, color_pink, 2)
        cv2.putText(frame, "completed products A:  " + str(data_current_run_dict['completed_a']), (850, 25),
                    cv2.FONT_HERSHEY_COMPLEX, 1, color_blue, 2)
        cv2.putText(frame, "completed products B:  " + str(data_current_run_dict['completed_b']), (850, 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, color_green, 2)
        cv2.putText(frame, "total finished:  " + str(data_current_run_dict['total_completed']), (1400, 37),
                    cv2.FONT_HERSHEY_COMPLEX, 1, color_black, 2)

        # endregion
        # Display frames
        cv2.imshow("Frame", frame)
        #cv2.imshow("RAWA", rawA)
        # cv2.imshow("RAWB", rawB)
        # cv2.imshow("processA", processA)
        # cv2.imshow("processB", processB)
        # cv2.imshow("scrapA", scrapA)
        # cv2.imshow("scrapB", scrapB)
        # cv2.imshow("completedA", completedA)
        # cv2.imshow("completedB", completedB)
        # cv2.imshow("completedCombine", completedCombine)
        # Display masks
        #cv2.imshow("RawA-Mask", mask_rawA)
        # cv2.imshow("RawB-Mask", mask_rawB)
        # cv2.imshow("Mask_processA", mask_processA)
        # cv2.imshow("Mask_processB", mask_processB)
        # cv2.imshow("Mask_completedA", mask_completedA)
        # cv2.imshow("Mask_completedB", mask_completedB)
        # cv2.imshow("Mask_final", mask_combined)

        key = cv2.waitKey(speed)
        if key == key_slow:
            speed = 120
        if key == key_fast:
            speed = 1
        if key == key_pause:
            cv2.waitKey(-1)
        if key == key_quit:
            end_all_threads()
            break
    cap.release()
    cv2.destroyAllWindows()
    # For testing only
    # region
    if debug_mode:
        print('Production Line A:  Input=', data_current_run_dict['nr_raw_materials_B'], '| Processed=',
              data_current_run_dict['raw_a'], ',', data_current_run_dict['scrap_a'], ' are scraps, remains ', data_current_run_dict['completed_a'])
        print('\nProduction Line B:  Input=', data_current_run_dict['nr_raw_materials_B'], '| Processed=',
              data_current_run_dict['raw_b'], ',', data_current_run_dict['scrap_b'], ' are scraps, remains ', data_current_run_dict['completed_b'])
        print('Total input = ',
              data_current_run_dict['raw_a']+data_current_run_dict['raw_b'], '|  ')
        print('\nTotal processed = ',
              data_current_run_dict['processed_a']+data_current_run_dict['processed_b'], '|  ')
        print('\nTotal scraps = ', data_current_run_dict['scrap_a']+data_current_run_dict['scrap_b'], '|  Total non-defected = ',
              data_current_run_dict['completed_a']+data_current_run_dict['completed_b'], ' Total final =', data_current_run_dict['total_completed'])
        print('Sum :', data_current_run_dict['scrap_a']+data_current_run_dict['scrap_b'] +
              data_current_run_dict['completed_a']+data_current_run_dict['completed_b'])
    # endregion

# endregion


####
thread_detector = threading.Thread(target=manufacturing_detector)
thread_update_20mins_table = threading.Thread(target=update_20mins_table, args=(
    update_20mins_table_command, updating_20mins_table_interval))
thread_update_daily_table = threading.Thread(target=update_daily_table, args=(
    upsert_command_for_daily_table, updating_manufacture_table_interval))


fetch_current_day_from_DB(querry_data_command)
thread_update_daily_table.start()
thread_detector.start()
thread_update_20mins_table.start()
