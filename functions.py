# Стандартные модули Python
import time
from datetime import datetime

# Модули для работы с Windows API
import win32gui
import win32process

# Модули для мониторинга активности
import pyautogui
import psutil


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


# Получение информации об активном окне
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
        'window_title': window_title,
        'process_name': process_name,
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
def checking_afk():
    global afk_count, start_afk
    if afk_count > 3:  # Если бездействие более 3 проверок
        start_afk = time.time() - afk_count
        return True
    return False
    

# Определение возобновления активности
def resumption_activity():
    global end_afk, start_afk
    fixed_afk = checking_afk()
    afk_counter()
    
    if not checking_afk() and fixed_afk:  # Если активность возобновилась
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


# Создание словаря с имеющимися процессами и окнами
def create_process_dict(process_name, window_name, start_time, end_time):
    global process_dict # Используем глобальную переменную для хранения данных
    duration = end_time - start_time # Вычисляем длительность активности
    
    # Если процесс еще не существует в словаре
    if process_name not in process_dict:
        process_dict[process_name] = {
            'windows': {}, # Словарь для хранения окон процесса
            'total_duration': 0 # Общая длительность работы процесса
        }
    
    # Обработка информации об окнах
    if window_name not in process_dict[process_name]['windows']:
        # Если окно новое, создаем его запись
        process_dict[process_name]['windows'][window_name] = {
            'duration': duration # Длительность работы окна
        }
    else:
        # Если окно уже существует, добавляем длительность
        process_dict[process_name]['windows'][window_name]['duration'] += duration
    
    # Обновляем общую длительность процесса
    process_dict[process_name]['total_duration'] += duration


# Функция для сохранения словаря в txt-файл
def save_dict_to_txt(filename, data):
    with open(filename, 'w', encoding='utf-8') as file: # Открываем файл для записи
        file.write(f'Отчёт {format_day()}\n') # Записываем заголовок с датой
        
        # Проходим по всем процессам
        for process, info in data.items():
            file.write(f"Процесс: {process}\n") # Записываем название процесса
            file.write(f"   Общая длительность: {format_time(info['total_duration'])}\n") # Записываем общую длительность
            file.write("    Окна:\n") # Заголовок раздела с окнами
            
            # Проходим по всем окнам процесса
            for window, window_info in info['windows'].items():
                file.write(f"       Окно: {window}\n") # Записываем название окна
                file.write(f"           Длительность: {format_time(window_info['duration'])}\n") # Записываем длительность окна
            
            file.write("\n") # Добавляем пустую строку между процессами для читаемости