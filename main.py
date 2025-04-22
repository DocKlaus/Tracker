# Системные модули
import time
import traceback

# Пользовательские функции
from functions import (
    get_active_window_info,
    create_process_dict,
    save_dict_to_txt,
    get_config_info,
    get_dict_from_config
)
from error_handling import handle_error
from time_formatting import format_date, format_time, format_filename
from afk_handling import is_afk

# Настройки программы
flag_time_based_report: bool = False  # Флаг создания time_based_report

# Файлы конфигурации
config_file: str = 'config_files/config.txt'
sections_file: str = 'config_files/sections.txt'

# Загрузка конфигураций
config_info = get_config_info(config_file)
sections_dict = get_dict_from_config(sections_file)

# Словарь для AFK
window_afk_info = {'window_title':'AFK', 'process_name':'AFK', 'process_path':'AFK'}

# Текущая дата и время
day: str = format_date(time.time())
custom_date: str = format_filename(time.time())

# Директории и файлы отчетов
time_based_report_directory: str = 'time_based_report_directory'
activity_report_directory: str = 'activity_report_directory'

activity_report: str = f'activity_report_{custom_date}.txt'
if flag_time_based_report:
    time_based_report: str = f'time_based_report_{custom_date}.txt'


# Инициализация программы
print(
    f'Программа запущена. Дата: {day}',
    f'Создан файл {activity_report}',
    sep='\n'
)

if flag_time_based_report:
    print(f'Создан файл {time_based_report}')


def recording_info(
    info: dict,                           # Словарь с информацией о процессе
    sections_dict: dict = sections_dict,  # Словарь секций для записи
    start_time: float = time.time(),      # Время начала процесса
    end_time: float = time.time(),        # Время окончания процесса
    modifier: float = 0                   # Модификатор времени
) -> None:
    """
    Функция записывает информацию о процессе в словарь и сохраняет его в файл.
    """
    # Корректируем время начала с учетом модификатора
    modifier_start_time = start_time - modifier
    
    # Создаем словарь процесса
    create_process_dict(sections_dict, info, modifier_start_time, end_time)
    
    # Сохраняем отчет в текстовый файл
    save_dict_to_txt(activity_report, activity_report_directory)


def update_window_info(current_info, new_info, modifier=0) -> None:
    """
    Обновляет информацию об активном окне, записывая предыдущую информацию
    и начиная запись новой.
    """
    if current_info:                                     # Если есть текущая информация
        recording_info(current_info, modifier=modifier)  # Записываем предыдущую
        
    recording_info(new_info)                             # Начинаем запись новой информации

try:
    # Основной цикл отслеживания активности
    print('Идёт отслеживание процессов')
    
    # Инициализация переменных
    current_window_info = None  # Текущая информация об окне
    was_afk_flag = False        # Флаг состояния AFK
    
    while True:
        # Получаем информацию об активном окне
        active_window_info = get_active_window_info()
        
        # Проверяем состояние AFK
        is_afk_flag = is_afk(config_info, active_window_info)
        
        # Обработка состояния AFK
        if is_afk_flag:
            if not was_afk_flag:  # Если перешли в состояние AFK
                update_window_info(current_window_info, window_afk_info)
                was_afk_flag = True
            else:                 # Если уже в состоянии AFK
                recording_info(window_afk_info, modifier=config_info['check_time'])
        else:                     # Обработка активного состояния
            if was_afk_flag:      # Если вышли из AFK
                recording_info(window_afk_info, modifier=config_info['check_time'])
                was_afk_flag = False
                
            # Обновляем информацию об активном окне
            update_window_info(current_window_info, active_window_info, modifier=config_info['check_time'])
            
        # Обновляем текущую информацию об окне
        current_window_info = active_window_info
        
        # Ждем заданное время перед следующей проверкой
        time.sleep(config_info['check_time'])

except KeyboardInterrupt:
    print("\nПрограмма остановлена пользователем")
    input("Нажмите Enter для выхода...")

except Exception as e:
    log_text = (
        f'{format_time(time.time())} {day} '
        f'Окончание работы программы. Причина: {str(e)}\n'
        f'Трассировка: {traceback.format_exc()}'
    )
    print(log_text)
    handle_error(log_text)
