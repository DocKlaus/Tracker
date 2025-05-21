#  Работа с ОС и процессами
import win32gui         # Для поиска активного окна и др.
import win32process     # Работа с процессами
import psutil           # Инфа о процессах и ОС
import os               # Взаимодействие с ОС

# Обработка ошибок и форматирование (пользовательская)
from error_handling import handle_error as he

# Форматирование (польз/непольз)
from time_formatting import (
    format_date,
    format_time,
    format_filename
    )
from typing import Dict

# Время по Unix (секунды)
import time

# Глобальные переменные для отслеживания активности
start_time: float = None    # Время начала активности
process_dict: Dict = {}     # Словарь для хранения информации о процессах

# Фиксированное текущее время для форматирования даты
today: float = time.time()


def get_config_info(config_file) -> dict:
    """
    Считывает конфигурационный файл, ищёт нужные значения, преобразует их в словарь.

    Аргументы:
        config_file (str): путь к конфигурационному файлу
        
    Возвращает:
        dict: словарь с данными из файла
    """
    DEFAULT_CHECK_TIME = 5  # в секундах
    DEFAULT_AFK_TIME = 3    # в минутах
    
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        # Поиск нужных параметров
        check_time = None
        afk_time = None
        
        for line in lines:
            line = line.strip()
            if 'check_time' in line:
                check_time = line.split(': ')[1].strip()
            if 'afk_time' in line:
                afk_time = line.split(': ')[1].strip()
                
        # Валидация и запись
        def validate_param(param_name, param, default_value, unit):
            try:
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

        # Обработка check_time
        check_time = validate_param('check_time', check_time, DEFAULT_CHECK_TIME, 'сек.')
        
        # Обработка afk_time
        afk_time = validate_param('afk_time', afk_time, DEFAULT_AFK_TIME, 'мин.')
        
        return {
            'check_time': check_time,
            'afk_time': afk_time
        }
    
    except FileNotFoundError as error:
        he(f'Файл {config_file} не найден', error=error)
        
    except UnicodeDecodeError as error:
        he('Возможно, файл имеет другую кодировку', error=error)
        
    except ValueError as error:
        he('Ошибка: значения параметров содержат недопустимые символы', error=error)


def get_dict_from_config(sections_file) -> dict:
    """
    Считывает конфигурационный файл и преобразует его в словарь.

    Аргументы:
        sections_file (str): путь к конфигурационному файлу
        
    Возвращает:
        dict: словарь с данными из файла
    """
    try:
        with open(sections_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            result_dict = {}
            
            for line_number, line in enumerate(lines, start=1):
                try:

                    section, values = line.split(':')
                    section = section.strip()
                    values = values.strip().split(',')
                    
                    values = [value.strip().lower() for value in values]

                    if section and values:
                        result_dict[section] = values
                    else:
                        raise ValueError(f"Строка {line_number}: отсутствуют значения")
                except ValueError as e:
                    he(f"Ошибка в строке {line_number}: {e}", False)
                    
        return result_dict

    except FileNotFoundError as error:
        he(f"Файл {sections_file} не найден", error=error)
    except Exception as error:
        he(f"Произошла ошибка при обработке файла {sections_file}", error=error)
        

def get_active_window_info() -> dict:
    """
    Функция для получения информации об активном окне.
    
    Возвращает словарь с данными:
    - заголовок окна
    - имя процесса
    - путь к исполняемому файлу процесса
    """
    
    # Дескриптор активного окна
    window_handle = win32gui.GetForegroundWindow()
    
    # Заголовок окна по дескриптору
    window_title = win32gui.GetWindowText(window_handle)
    
    # PID процесса
    _, pid = win32process.GetWindowThreadProcessId(window_handle)
    
    # Процесс по pid, имя процесса, путь.
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        process_path = process.exe()
        if pid < 0:                  #  !!! Понять-найти-решить: PID выскакивает меньше нуля !!!
            he(f'Получен некорректный PID: {pid}. Window_handle: {window_handle}. Window_title:{window_title}', False)
            process = 'Не найден. Создан отчёт об ошибке'
            process_name = 'Неизвестно'
            process_path = 'Неизвестно'
        
    except psutil.NoSuchProcess:
        he(f'{format_time(time.time())} {format_date(today)} process PID not found (pid={pid}) \n', flag_input = False)
        process = 'Не найден. Создан отчёт об ошибке'
        process_name = 'Неизвестно'
        process_path = 'Неизвестно'
    
    return {
        'window_title': window_title,
        'process_name': process_name,
        'process_path': process_path
    }


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
    
    start_formatted = format_time(start_time)
    end_formatted = format_time(end_time)
    
    filename = f'time_based_report_{format_filename(time.time())}.txt'
    
    if current_window:
        report_entry = f'{start_formatted}-{end_formatted} : {current_window}\n'
    else:
        report_entry = f'{start_formatted}-{end_formatted} : Desktop\n'
    
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
    
    # РаспоковОчка словаря
    window_name = active_window_info.get('window_title', '')
    process_name = active_window_info.get('process_name', '')
    process_path = active_window_info.get('process_path', '')
    duration = end_time - start_time

    section = 'Other'
    for subsection, names in sections_dict.items():
        for name in names:
            if name.lower() in process_path.lower():
                section = subsection
                break
        if section != 'Other':
            break
        if window_name == 'AFK':
            section = 'AFK'
    
    # Дефолтная структура по секциям, если её нет
    process_dict.setdefault(section, {
        'total_duration': 0,
        'processes': {}
    })
    
    # Дефолтная структура для процесса, если его нет
    process_dict[section]['processes'].setdefault(process_name, {
        'windows': {},
        'total_duration': 0
    })
    
    # Если нет названия окна, то в Desktopку
    window_key = 'Desktop' if not window_name else window_name
    window_data = process_dict[section]['processes'][process_name]['windows']
    
    if window_key not in window_data:
        window_data[window_key] = {'duration': duration}
    else:
        window_data[window_key]['duration'] += duration
    
    # Накручиваем длительность
    process_dict[section]['processes'][process_name]['total_duration'] += duration
    process_dict[section]['total_duration'] += duration


def sort_sections_by_duration():
    """
    Сортирует секции по убыванию ОБЩЕЙ длительности,
    а также сортирует процессы внутри каждой секции
    """
    global process_dict
    
    sorted_dict: Dict[str, dict] = {}
    
    # Сортировка секций по общей длительности (по убыванию)
    for section, data in sorted(
        process_dict.items(),
        key=lambda x: x[1]['total_duration'],
        reverse=True
    ):
        # Лепим заново сортированные дикты
        sorted_dict[section] = {
            'total_duration': data['total_duration'],
            'processes': sort_processes_by_duration(data['processes'])
        }
    
    process_dict = sorted_dict


def sort_processes_by_duration(processes: Dict) -> Dict:
    """
    Сортирует процессы ВНУТРИ СЕКЦИИ по убыванию длительности
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
    Сортирует окна ВНУТРИ ПРОЦЕССА по убыванию длительности
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
    Сортировочный корень
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
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    # СортировОчка перед сохранением
    sort_all_by_duration()
    
    with open(f'{directory}/{filename}', 'w', encoding='utf-8') as file:
        file.write(f'Отчёт {format_date(today)}\n\n')
        
        # Запись раздела (секции)
        for section, info in process_dict.items():
            file.write(f'Раздел: {section}\n')
            file.write(f'Общая длительность процессов раздела: {format_time(info["total_duration"])}\n')
            file.write(f'(процессы: {", ".join(info["processes"].keys())})\n\n')
            
            # Запись процесса
            for process, process_info in info["processes"].items():
                file.write(f'   Процесс: {process}\n')
                file.write(f'   Общая длительность процесса: {format_time(process_info["total_duration"])}\n')
                file.write(f'   (окна: {", ".join(process_info["windows"].keys())})\n\n')
                
                # Запись окна
                for window, window_info in process_info["windows"].items():
                    file.write(f'       Окно: {window}\n')
                    file.write(f'       Длительность: {format_time(window_info["duration"])}\n\n')

            file.write("\n")

