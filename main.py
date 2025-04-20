# Системные модули
import time
from datetime import datetime
import traceback

# Пользовательские функции
from functions import (
    get_active_window_info,
    create_time_based_report,
    detect_activity_resume,
    create_process_dict,
    save_dict_to_txt,
    format_filename,
    format_time,
    format_date,
    get_config_info,
    handle_error,
    get_dict_from_config,
    start_time,
    current_window
)

# Настройки программы
flag_time_based_report: bool = False  # Флаг создания time_based_report

# Файлы конфигурации
config_file: str = 'config.txt'
sections_file: str = 'sections.txt'

# Загрузка конфигураций
config_info = get_config_info(config_file)
sections_dict = get_dict_from_config(sections_file)

# Текущая дата и время
day: str = format_date()
custom_date: str = format_filename()

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

try:
    # Основной цикл отслеживания активности
    print('Идёт отслеживание процессов')
    
    while True:
        # Получение информации об активном окне
        active_window_info = get_active_window_info()
        active_window_name = active_window_info['window_title']
        check_activity = detect_activity_resume(config_info)
        
        # Обработка состояния AFK
        if check_activity:
            afk_start, afk_end = check_activity
            
            # Запись AFK в словарь процессов
            create_process_dict({'AFK':'AFK', 'AFK':'AFK', 'AFK':'AFK'}, active_window_info, afk_start, afk_end)
            save_dict_to_txt(activity_report, activity_report_directory)
            
            if flag_time_based_report:
                # Запись времени AFK
                with open(time_based_report, 'a', encoding='utf-8') as file:
                    file.write(f'{format_time(check_activity[0])}-{format_time(check_activity[1])} : Время AFK\n')
        
        # Обработка нового активного окна
        elif current_window is None:
            start_time = time.time()  # Запоминаем начальное время
            
        elif current_window != active_window_name:
            if start_time:
                end_time = time.time()  # Замеряем время окончания активности
                
                # Формирование отчетов
                create_process_dict(sections_dict, active_window_info, start_time, end_time)
                if flag_time_based_report:
                    create_time_based_report(start_time, end_time, current_window)
                
                # Сохранение данных
                save_dict_to_txt(activity_report, activity_report_directory)
                start_time = time.time()  # Обновляем начальное время
        
        # Обновление текущего окна
        current_window = active_window_name
        
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
