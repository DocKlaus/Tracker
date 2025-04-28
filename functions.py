# Стандартные модули Python
import time
from datetime import datetime

# Модули для работы с Windows API
import win32gui
import win32process

# Модули для мониторинга активности

import psutil

# Утилиты
import pprint
import os
from typing import Dict

from error_handling import handle_error as he
from time_formatting import format_date, format_time, format_filename

# Глобальные переменные для отслеживания активности
start_time: float = None    # Время начала активности
process_dict: Dict = {}     # Словарь для хранения информации о процессах



# Текущее время для форматирования даты
today: float = time.time()


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
        he(f'Файл {config_file} не найден', error=error)
        
    except UnicodeDecodeError as error:
        he('Возможно, файл имеет другую кодировку', error=error)
        
    except ValueError as error:
        he('Ошибка: значения параметров содержат недопустимые символы', error=error)


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
        if pid < 0:
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
        if window_name == 'AFK':
            section = 'AFK'
    
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
        file.write(f'Отчёт {format_date(today)}\n\n')
        
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

