import time
from datetime import datetime
import win32gui
import pyautogui
import win32process
import psutil

today = time.time()
current_cursor_coordinates = []
afk_count = 0
start_afk = 0
end_afk = 0


def get_active_window_info():
    # Получаем дескриптор активного окна
    window_handle = win32gui.GetForegroundWindow()    
    # Получаем заголовок окна
    window_title = win32gui.GetWindowText(window_handle)    
    # Получаем PID процесса
    _, pid = win32process.GetWindowThreadProcessId(window_handle)    
    # Получаем информацию о процессе
    process = psutil.Process(pid)
    process_name = process.name()
    process_path = process.exe()
    
    return {
        'window title': window_title,
        'pid': pid,
        'process name': process_name,
        'process path': process_path
    }

def format_time(time_unix):
    time_struct = time.localtime(time_unix)
    return f'{time.strftime("%H:%M:%S", time_struct)}'

def format_day():
    time_struct = time.gmtime(today)
    return f'{time.strftime("%d.%m.%Y", time_struct)}'

def custom_format():
    time_struct = time.localtime(today)
    formatted_time = time.strftime("%Y_%m_%d_%H_%M", time_struct)
    return formatted_time

def update_duration(duration_calculation, window_name, dictionary):
    if window_name not in dictionary:
        dictionary[window_name] = duration_calculation
    else:
        dictionary[window_name] += duration_calculation

def checking_cursor_movement():
    global current_cursor_coordinates 
    new_cursor_coordinates = pyautogui.position()
    if not current_cursor_coordinates:
        current_cursor_coordinates = new_cursor_coordinates
        return False
    if current_cursor_coordinates != new_cursor_coordinates:
        current_cursor_coordinates = new_cursor_coordinates
        return False
    
    return True
    
def afk_counter():
    global afk_count
    if checking_cursor_movement():
        afk_count += 1
    else:
        afk_count = 0

def checking_afk():
    global afk_count, start_afk
    if afk_count > 180:
        start_afk = time.time() - afk_count
        return True
    
def resumption_activity():
    global end_afk, start_afk
    fixed_afk = checking_afk()
    afk_counter()
    if not checking_afk() and fixed_afk: 
        end_afk = time.time()
        return f'{format_time(start_afk)}-{format_time(end_afk)}'
    else:
        return False


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
