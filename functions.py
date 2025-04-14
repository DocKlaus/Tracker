import time
from datetime import datetime
import win32gui

today = time.time()

def get_active_window_title():
    window_handle = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(window_handle)
    return window_title

def format_time(time_unix):
    time_struct = time.localtime(time_unix)
    return f'{time.strftime("%H:%M:%S", time_struct)}'

def format_day():
    time_struct = time.gmtime(today)
    return f'{time.strftime("%d.%m.%Y", time_struct)}'

def custom_format():
    time_struct = time.localtime(today)
    formatted_time = time.strftime("%H_%M_%d_%m_%Y", time_struct)
    return formatted_time

def update_duration(duration_calculation, window_name, dictionary):
    if window_name not in dictionary:
        dictionary[window_name] = duration_calculation
    else:
        dictionary[window_name] += duration_calculation


def create_report(start, end, window_name, dictionary):
    duration = end - start
    update_duration(duration, window_name, dictionary)

    with open(f'time_based_report_{custom_format()}.txt', 'a', encoding='utf-8') as file:
        if window_name:
            file.write(f'{format_time(start)}-{format_time(end)} : {window_name}\n')
        else:
            file.write(f'{format_time(start)}-{format_time(end)} : Desktop\n')


def create_structural_dict():
    with open(f'time_based_report_{custom_format()}.txt', 'r', encoding='utf-8') as file:
        structural_dict = {}
        for line in file:
            if ' : ' in line:
                key, value = line.strip().split(' : ')
                if value in structural_dict.keys():
                    structural_dict[value] += duration(key)
                else:
                    structural_dict[value] = duration(key)
    return structural_dict

def duration(time):
    start, end = time.strip().split('-')
    duration = datetime.strptime(end, '%H:%M:%S') - datetime.strptime(start, '%H:%M:%S')
    return duration

def create_structural_report():
    with open(f'structural_report_{custom_format()}.txt', 'w', encoding='utf-8') as file:
        for key, value in create_structural_dict().items():
            file.write(f'{key} : {value}\n')
