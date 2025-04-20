# Стандартные модули Python
import time
from datetime import datetime

# Модули для работы с Windows API
import win32gui
import win32process

# Модули для мониторинга активности
import pyautogui
import psutil

# Утилиты
import pprint
import os
import traceback
from typing import Dict

# Глобальные переменные для отслеживания активности
current_window: str = None  # Текущее активное окно
start_time: float = None    # Время начала активности
process_dict: Dict = {}     # Словарь для хранения информации о процессах

# Переменные для отслеживания AFK (Away From Keyboard)
current_cursor_coordinates: list = None  # Текущие координаты курсора
afk_count: int = 0                    # Счетчик бездействия
start_afk: float = 0                  # Время начала AFK
end_afk: float = 0                    # Время окончания AFK

# Текущее время для форматирования даты
today: float = time.time()


def handle_error(message: str, flag_input: bool = True, error: str = '') -> None:
    """
    Функция для логирования ошибок и создания отчета
    
    Параметры:
    message (str): сообщение об ошибке
    flag_input (bool): показывать ли приглашение для выхода
    error (str): дополнительная информация об ошибке
    """
    
    # Создаем директорию для логов, если она не существует
    error_dir = 'error_logs'
    if not os.path.exists(error_dir):
        os.makedirs(error_dir, exist_ok=True)
    
    # Форматируем имя файла с учетом текущей даты
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    log_file = f'{error_dir}/Error_report_{timestamp}.txt'
    
    # Записываем информацию в файл
    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(f'[Ошибка] {time.strftime("%Y-%m-%d %H:%M:%S")} - {message}\n')
        file.write(f'Дополнительная информация: {error}\n')
        file.write(f'Трассировка:\n{traceback.format_exc()}\n')
        
    # Выводим сообщение в консоль
    print(f'\n[Ошибка] {time.strftime("%Y-%m-%d %H:%M:%S")} - {message}\n')
    
    # Ждем ввода, если флаг установлен
    if flag_input:
        input("Нажмите Enter для выхода...")


def get_config_info(config_file) -> dict:
    """
    Считывает конфигурационный файл, ищёт нужные значения, преобразует их в словарь.
    Формат файла: секция: значение1, значение2, значение3
    
    Аргументы:
        config_file (str): путь к конфигурационному файлу
        
    Возвращает:
        dict: словарь с данными из файла
    """
    DEFAULT_CHECK_TIME = 5  # в секундах
    DEFAULT_AFK_TIME = 3    # в минутах
    
    try:
        # Читаем файл конфигурации
        with open(config_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        # Ищем нужные параметры
        check_time = None
        afk_time = None
        
        for line in lines:
            line = line.strip()
            if 'check_time' in line:
                check_time = line.split(': ')[1].strip()
            if 'afk_time' in line:
                afk_time = line.split(': ')[1].strip()
                
        # Валидируем и записываем параметры
        def validate_param(param_name, param, default_value, unit):
            try:
                # Пытаемся преобразовать в float
                float(param)
                is_valid = True
            except ValueError:
                is_valid = False
                
            if not param or not is_valid:
                param = default_value
                log_text = f'Параметр {param_name} установлен по умолчанию = {default_value} {unit}'
            else:
                log_text = f'Параметр {param_name} установлен пользователем = {param} {unit}'
            print(log_text)
            return float(param)
        
        # Обработка check_time
        check_time = validate_param('check_time', check_time, DEFAULT_CHECK_TIME, 'сек.')
        
        # Обработка afk_time
        afk_time = validate_param('afk_time', afk_time, DEFAULT_AFK_TIME, 'мин.')
        
        return {
            'check_time': check_time,
            'afk_time': afk_time
        }
    
    except FileNotFoundError as error:
        handle_error(f'Файл {config_file} не найден', error=error)
        
    except UnicodeDecodeError as error:
        handle_error('Возможно, файл имеет другую кодировку', error=error)
        
    except ValueError as error:
        handle_error('Ошибка: значения параметров содержат недопустимые символы', error=error)


def get_dict_from_config(sections_file) -> dict:
    """
    Считывает конфигурационный файл и преобразует его в словарь.
    Формат файла: секция: значение1, значение2, значение3
    
    Аргументы:
        sections_file (str): путь к конфигурационному файлу
        
    Возвращает:
        dict: словарь с данными из файла
    """
    try:
        # Читаем файл конфигурации
        with open(sections_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            result_dict = {}  # Создаем пустой словарь для результата
            
            for line_number, line in enumerate(lines, start=1):
                try:
                    # Разделяем строку на секцию и значения
                    section, values = line.split(':')
                    section = section.strip()
                    values = values.strip().split(',')
                    
                    # Очищаем каждое значение от пробелов и преобразуем к нижнему регистру
                    values = [value.strip().lower() for value in values]
                    
                    # Проверяем корректность данных
                    if section and values:
                        result_dict[section] = values
                    else:
                        raise ValueError(f"Строка {line_number}: отсутствуют значения")
                except ValueError as e:
                    handle_error(f"Ошибка в строке {line_number}: {e}", False)
                    
        return result_dict
    except FileNotFoundError as error:
        handle_error(f"Файл {sections_file} не найден", error=error)
    except Exception as error:
        handle_error(f"Произошла ошибка при обработке файла {sections_file}", error=error)
        

def get_active_window_info() -> dict:
    """
    Функция для получения информации об активном окне.
    
    Возвращает словарь с данными:
    - заголовок окна
    - имя процесса
    - путь к исполняемому файлу процесса
    """
    
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
        handle_error(f'{format_time(time.time())} {format_date()} process PID not found (pid={pid}) \n')
        process = 'Не найден. Создан отчёт об ошибке'
        process_name = 'Неизвестно'
        process_path = 'Неизвестно'
    
    return {
        'window_title': window_title,
        'process_name': process_name,
        'process_path': process_path
    }


def check_cursor_movement() -> bool:
    """
    Функция для проверки движения курсора мыши.
    
    Возвращает:
    - True, если курсор не двигался
    - False, если курсор двигался или определяется впервые
    """
    global current_cursor_coordinates
    # Получаем новые координаты курсора
    new_cursor_coordinates = pyautogui.position()
    
    # Если координаты определены впервые
    if current_cursor_coordinates is None:
        current_cursor_coordinates = new_cursor_coordinates
        return False  # Курсор только что определен
    
    # Проверяем, изменился ли курсор
    if current_cursor_coordinates != new_cursor_coordinates:
        current_cursor_coordinates = new_cursor_coordinates
        return False  # Курсор двигался
    
    return True  # Курсор не двигался
    

def update_afk_counter()-> None:
    """
    Обновляет счетчик бездействия.
    
    Увеличивает счетчик при отсутствии активности,
    сбрасывает при возобновлении активности.
    """
    global afk_count
    
    if check_cursor_movement():
        afk_count += 1  # Увеличиваем счетчик бездействия
    else:
        afk_count = 0   # Сброс счетчика при активности


def is_afk(config_info: dict) -> bool:
    """
    Проверяет, находится ли пользователь в состоянии AFK.
    
    Параметры:
    config_info (dict): словарь с конфигурацией
        - afk_time: время бездействия в минутах
        - check_time: интервал проверки в секундах
    
    Возвращает:
    bool: True если пользователь AFK, иначе False
    """
    global afk_count, start_afk
    
    afk_time = config_info.get('afk_time', 3)  # значение по умолчанию 60 секунд
    check_time = config_info.get('check_time', 5)  # значение по умолчанию 30 секунд
    
    threshold = afk_time * 60 / check_time
    
    if afk_count > threshold:
        start_afk = time.time() - afk_count * 60 / check_time
        return True
    return False


def detect_activity_resume(config_info: dict):
    """
    Определяет момент возобновления активности после AFK.
    
    Параметры:
    config_info (dict): конфигурация системы
    
    Возвращает:
    tuple: (время начала AFK, время окончания AFK) или False
    """
    global end_afk, start_afk
    
    was_afk = is_afk(config_info)
    update_afk_counter()
    
    if not is_afk(config_info) and was_afk:
        end_afk = time.time()
        return start_afk, end_afk
    return False


def format_time(timestamp: float) -> str:
    """
    Форматирует временную метку Unix в формат времени HH:MM:SS
    
    Параметры:
    timestamp (float): временная метка Unix
    
    Возвращает:
    str: отформатированное время в формате HH:MM:SS
    """
    time_struct = time.gmtime(timestamp)
    return time.strftime("%H:%M:%S", time_struct)


def format_date(today: float = today) -> str:
    """
    Форматирует дату в формат DD.MM.YYYY
    
    Параметры:
    today (float): временная метка Unix для текущей даты
    
    Возвращает:
    str: отформатированная дата в формате DD.MM.YYYY
    """
    time_struct = time.gmtime(today)
    return time.strftime("%d.%m.%Y", time_struct)


def format_filename(today: float = today) -> str:
    """
    Форматирует дату и время в формат для имени файла YYYY_MM_DD_HH_MM
    
    Параметры:
    today (float): временная метка Unix для текущей даты
    
    Возвращает:
    str: отформатированное имя файла в формате YYYY_MM_DD_HH_MM
    """
    time_struct = time.localtime(today)
    return time.strftime("%Y_%m_%d_%H_%M", time_struct)


def create_time_based_report(
    start_time: float, 
    end_time: float, 
    current_window: str
) -> None:
    """
    Создает повременной отчет в текстовый файл
    
    Параметры:
    start_time (float): начальная временная метка Unix
    end_time (float): конечная временная метка Unix
    current_window (str): название активного окна или None
    """
    
    # Форматируем временные метки
    start_formatted = format_time(start_time)
    end_formatted = format_time(end_time)
    
    # Форматируем имя файла отчета
    filename = f'time_based_report_{format_filename(time.time())}.txt'
    
    # Создаем запись для файла
    if current_window:
        report_entry = f'{start_formatted}-{end_formatted} : {current_window}\n'
    else:
        report_entry = f'{start_formatted}-{end_formatted} : Desktop\n'
    
    # Записываем данные в файл
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(report_entry)


def create_process_dict(
    sections_dict: dict, 
    active_window_info: dict, 
    start_time: float, 
    end_time: float
) -> None:
    """
    Создает и обновляет структуру словаря с информацией о процессах
    
    Параметры:
    sections_dict (dict): словарь секций для классификации процессов
    active_window_info (dict): информация об активном окне
    start_time (float): время начала активности
    end_time (float): время окончания активности
    """
    
    global process_dict
    
    # Извлекаем данные из активного окна
    window_name = active_window_info.get('window_title', '')
    process_name = active_window_info.get('process_name', '')
    process_path = active_window_info.get('process_path', '')
    duration = end_time - start_time
    
    # Определяем секцию для процесса
    section = 'Other'
    for subsection, names in sections_dict.items():
        for name in names:
            if name.lower() in process_path.lower():
                section = subsection
                break
        if section != 'Other':
            break
    
    # Создаем структуру по секциям, если её нет
    process_dict.setdefault(section, {
        'total_duration': 0,
        'processes': {}
    })
    
    # Создаем структуру для процесса, если его нет
    process_dict[section]['processes'].setdefault(process_name, {
        'windows': {},
        'total_duration': 0
    })
    
    # Обрабатываем информацию об окнах
    window_key = 'Desktop' if not window_name else window_name
    window_data = process_dict[section]['processes'][process_name]['windows']
    
    if window_key not in window_data:
        window_data[window_key] = {'duration': duration}
    else:
        window_data[window_key]['duration'] += duration
    
    # Обновляем длительности
    process_dict[section]['processes'][process_name]['total_duration'] += duration
    process_dict[section]['total_duration'] += duration


def sort_sections_by_duration():
    """
    Сортирует секции по убыванию общей длительности,
    а также сортирует процессы внутри каждой секции
    """
    global process_dict
    
    sorted_dict: Dict[str, dict] = {}
    
    # Сортируем секции по убыванию total_duration
    for section, data in sorted(
        process_dict.items(),
        key=lambda x: x[1]['total_duration'],
        reverse=True
    ):
        # Создаем новую структуру с отсортированными процессами
        sorted_dict[section] = {
            'total_duration': data['total_duration'],
            'processes': sort_processes_by_duration(data['processes'])
        }
    
    process_dict = sorted_dict


def sort_processes_by_duration(processes: Dict) -> Dict:
    """
    Сортирует процессы внутри секции по убыванию длительности
    """
    sorted_processes: Dict = {}
    
    for process, data in sorted(
        processes.items(),
        key=lambda x: x[1]['total_duration'],
        reverse=True
    ):
        sorted_processes[process] = {
            'total_duration': data['total_duration'],
            'windows': sort_windows_by_duration(data['windows'])
        }
    
    return sorted_processes


def sort_windows_by_duration(windows: Dict) -> Dict:
    """
    Сортирует окна внутри процесса по убыванию длительности
    """
    return {
        window: {'duration': data['duration']}
        for window, data in sorted(
            windows.items(),
            key=lambda x: x[1]['duration'],
            reverse=True
        )
    }

def sort_all_by_duration():
    """
    Выполняет полную сортировку всей структуры данных
    """
    sort_sections_by_duration()
    
    for section in process_dict:
        process_dict[section]['processes'] = sort_processes_by_duration(
            process_dict[section]['processes']
        )
        
        for process in process_dict[section]['processes']:
            process_dict[section]['processes'][process]['windows'] = sort_windows_by_duration(
                process_dict[section]['processes'][process]['windows']
            )


def save_dict_to_txt(filename: str, directory: str):
    """
    Сохраняет словарь process_dict в текстовый файл с форматированием.
    
    Параметры:
    filename (str): имя файла для сохранения
    directory (str): путь к директории для сохранения
    """
    # Создаем директорию, если она не существует
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    # Сортируем данные перед сохранением
    sort_all_by_duration()
    
    # Открываем файл для записи
    with open(f'{directory}/{filename}', 'w', encoding='utf-8') as file:
        # Записываем заголовок с датой
        file.write(f'Отчёт {format_date()}\n\n')
        
        # Проходим по всем разделам
        for section, info in process_dict.items():
            file.write(f'Раздел: {section}\n')
            file.write(f'Общая длительность процессов раздела: {format_time(info["total_duration"])}\n')
            file.write(f'(процессы: {", ".join(info["processes"].keys())})\n\n')
            
            # Проходим по всем процессам в разделе
            for process, process_info in info["processes"].items():
                file.write(f'   Процесс: {process}\n')
                file.write(f'   Общая длительность процесса: {format_time(process_info["total_duration"])}\n')
                file.write(f'   (окна: {", ".join(process_info["windows"].keys())})\n\n')
                
                # Проходим по всем окнам процесса
                for window, window_info in process_info["windows"].items():
                    file.write(f'       Окно: {window}\n')
                    file.write(f'       Длительность: {format_time(window_info["duration"])}\n\n')
            
            # Добавляем разделитель между разделами
            file.write("\n")

