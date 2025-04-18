# Стандартные модули Python
import time
from datetime import datetime

# Модули для работы с Windows API
import win32gui
import win32process

# Модули для мониторинга активности
import pyautogui
import psutil

import pprint


# Глобальные переменные для отслеживания активности
current_window = None  # Текущее активное окно
start_time = None      # Время начала активности
process_dict = {}      # Словарь для хранения информации о процессах

# Переменные для отслеживания AFK (Away From Keyboard)
current_cursor_coordinates = []  # Текущие координаты курсора
afk_count = 0                    # Счетчик бездействия
start_afk = 0                    # Время начала AFK
end_afk = 0                      # Время окончания AFK

today = time.time()  # Текущее время для форматирования даты

# Ориентация по разделам
Sections = {
    'Steam': ['steam'],
    'Браузер': ['google', 'chrome', 'yandex'],
    'Мессенджеры': ['discord', 'telegram'],
    'Работа': ['code']
}

def get_config_info(config_file):
    try:
        with open(config_file, 'r', encoding = 'utf-8') as file:
            lines = file.readlines()
            line_iterator = iter(lines)
            time_check_sec = None
            time_afk = None
            for line in line_iterator:
                line = line.strip()
                if 'time_check_sec' in line:
                    time_check_sec = line.split(' = ')[1].strip()                    
                if 'time_afk' in line:
                    time_afk = line.split(' = ')[1].strip()
                if time_check_sec and time_afk != None:
                    break
            with open(f'activity_report_{custom_format()}.txt', 'a', encoding = 'utf-8') as file:
                if time_check_sec == None:
                    time_check_sec = 5
                    log = f'Параметр time_check_sec (частота опроса) установлен по умолчанию = {time_check_sec} сек.'
                else:
                    log = f'Параметр time_check_sec (частота опроса) установлен пользователем = {time_check_sec} сек.'
                
                file.write(f'{log}\n')
                print(f'{log}')

                if time_afk == None:
                    time_afk = 3
                    log = f'Параметр time_afk (фиксирование простоя) установлен по умолчанию = {time_afk} мин.'
                else:
                    log = f'Параметр time_afk (фиксирование простоя) установлен пользователем = {time_afk} мин.'
                
                file.write(f'{log}\n')
                print(f'{log}')
       
        return {
            'time_check_sec': int(time_check_sec),
            'time_afk': int(time_afk)
            }
    
    except FileNotFoundError:
        with open(f'Отчёт об ошибках {format_time(time.time())}', 'a', encoding = 'utf-8') as file:
            file.write(f'Файл {config_file} не найден')
    except UnicodeDecodeError:
        with open(f'Отчёт об ошибках {format_time(time.time())}', 'a', encoding = 'utf-8') as file:
            file.write("Возможно, файл имеет другую кодировку")

# Получение информации об активном окне
def get_active_window_info():
    # Получаем дескриптор активного окна
    window_handle = win32gui.GetForegroundWindow()
    # Получаем заголовок окна
    window_title = win32gui.GetWindowText(window_handle)
    # Получаем PID процесса
    _, pid = win32process.GetWindowThreadProcessId(window_handle)
    # Получаем информацию о процессе
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        process_path = process.exe()

    except psutil.NoSuchProcess: 
        with open(f'Отчёт об ошибках {custom_format()}', 'a', encoding = 'utf-8') as file:
            file.write(f'process PID not found (pid={pid}) \n File "c:\\projects\\GIT\\Tracker\\functions.py"')
        process = 'Не найден. Создан отчёт об ошибке'
        process_name = 'Неизвестно'
        process_path = 'Неизвестно'
    return {
        'window_title': window_title,
        'process_name': process_name,
        'process_path': process_path
    }


# Проверка движения курсора
def checking_cursor_movement():
    global current_cursor_coordinates
    new_cursor_coordinates = pyautogui.position()
    
    if not current_cursor_coordinates:
        current_cursor_coordinates = new_cursor_coordinates
        return False  # Курсор только что определен
    
    if current_cursor_coordinates != new_cursor_coordinates:
        current_cursor_coordinates = new_cursor_coordinates
        return False  # Курсор двигался
    
    return True  # Курсор не двигался
    

# Подсчет времени бездействия
def afk_counter():
    global afk_count
    if checking_cursor_movement():
        afk_count += 1  # Увеличиваем счетчик бездействия
    else:
        afk_count = 0   # Сброс счетчика при активности


# Проверка состояния AFK
def checking_afk(config_info):
    global afk_count, start_afk
    time_afk = config_info['time_afk']
    time_check_sec = config_info['time_check_sec']
    if afk_count > time_afk * 60 / time_check_sec:  
        start_afk = time.time() - afk_count * 60 / time_check_sec
        return True
    return False
    

# Определение возобновления активности
def resumption_activity(config_info):
    global end_afk, start_afk
    fixed_afk = checking_afk(config_info)
    afk_counter()
    
    if not checking_afk(config_info) and fixed_afk:  # Если активность возобновилась
        end_afk = time.time()
        return start_afk, end_afk
    else:
        return False


# Форматирование времени
def format_time(time_unix):
    time_struct = time.gmtime(time_unix)
    return f'{time.strftime("%H:%M:%S", time_struct)}'


# Форматирование даты для отчета
def format_day():
    time_struct = time.gmtime(today)
    return f'{time.strftime("%d.%m.%Y", time_struct)}'


# Форматирование имени файла отчета
def custom_format():
    time_struct = time.localtime(today)
    formatted_time = time.strftime("%Y_%m_%d_%H_%M", time_struct)
    return formatted_time


# Создание повременного отчета
def create_time_based_report(start_time, end_time, current_window):
    with open(f'time_based_report_{custom_format()}.txt', 'a', encoding='utf-8') as file:
        if current_window:
            file.write(f'{format_time(start_time)}-{format_time(end_time)} : {current_window}\n')
        else:
            file.write(f'{format_time(start_time)}-{format_time(end_time)} : Desktop\n')


# Функция для создания структуры словаря
def create_process_dict(process_name, window_name, process_path, start_time, end_time):
    global process_dict
    duration = end_time - start_time
    
    section = 'Other'
    for subsection in Sections:
        for name in Sections[subsection]:
            if name.lower() in process_path.lower():
                section = subsection
                break
    
    # Создаём структуру по секциям, если её нет
    if section not in process_dict:
        process_dict[section] = {
            'total_duration': 0,
            'processes': {}
        }
    
    # Если процесс еще не существует в словаре
    if process_name not in process_dict[section]['processes']:
        process_dict[section]['processes'][process_name] = {
            'windows': {},
            'total_duration': 0
        }
    
    # Обработка информации об окнах
    if window_name not in process_dict[section]['processes'][process_name]['windows']:
        if window_name == '' or None:
            process_dict[section]['processes'][process_name]['windows']['Desktop'] = {
            'duration': duration
        }
        else:
            process_dict[section]['processes'][process_name]['windows'][window_name] = {
                'duration': duration
            }
    else:
        process_dict[section]['processes'][process_name]['windows'][window_name]['duration'] += duration
    
    # Обновляем длительности
    process_dict[section]['processes'][process_name]['total_duration'] += duration
    process_dict[section]['total_duration'] += duration

# Функция для сортировки секций по длительности
def sort_sections_by_duration():
    global process_dict
    sorted_dict = {}
    for section, data in sorted(process_dict.items(), key=lambda x: x[1]['total_duration'], reverse=True):
        sorted_dict[section] = {
            'total_duration': data['total_duration'],
            'processes': sort_processes_by_duration(data['processes'])
        }
    process_dict = sorted_dict

# Функция для сортировки процессов внутри секции
def sort_processes_by_duration(processes):
    sorted_processes = {}
    for process, data in sorted(processes.items(), key=lambda x: x[1]['total_duration'], reverse=True):
        sorted_processes[process] = {
            'total_duration': data['total_duration'],
            'windows': sort_windows_by_duration(data['windows'])
        }
    return sorted_processes

# Функция для сортировки окон внутри процесса
def sort_windows_by_duration(windows):
    return {
        window: {'duration': data['duration']} 
        for window, data in sorted(windows.items(), key=lambda x: x[1]['duration'], reverse=True)
    }

# Функция для полной сортировки всего словаря
def sort_all_by_duration():
    sort_sections_by_duration()
    for section in process_dict:
        process_dict[section]['processes'] = sort_processes_by_duration(process_dict[section]['processes'])
        for process in process_dict[section]['processes']:
            process_dict[section]['processes'][process]['windows'] = sort_windows_by_duration(process_dict[section]['processes'][process]['windows'])



# Функция для сохранения словаря в txt-файл
def save_dict_to_txt(filename):
    sort_all_by_duration()
    with open(filename, 'w', encoding='utf-8') as file: # Открываем файл для записи
        file.write(f'Отчёт {format_day()}\n') # Записываем заголовок с датой
        
        # Проходим по всем процессам
        for section, info in process_dict.items():
            file.write(f'Раздел: {section}\n')
            file.write(f'Общая длительность процессов раздела: {format_time(info['total_duration'])}\n')
            file.write(f'(процессы: {", ".join(info["processes"].keys())})\n')
            file.write("\n")

            for process, process_info in info['processes'].items():
                
                file.write(f'   Процесс: {process}\n')
                file.write(f'   Общая длительность процесса: {format_time(process_info['total_duration'])}\n') # Записываем название процесса
                file.write(f'   (окна: {', '.join(process_info['windows'].keys())})\n')
                file.write("\n")

                # Проходим по всем окнам процесса
                for window, window_info in process_info['windows'].items():
                    file.write(f'       Окно: {window}\n') # Записываем название окна
                    file.write(f'       Длительность: {format_time(window_info['duration'])}\n') # Записываем длительность окна
                    file.write("\n")
  
            file.write("\n") # Добавляем пустую строку между процессами для читаемости


