# Системные модули
import time
from datetime import datetime
import atexit
import traceback

# Пользовательские функции
from functions import (
    get_active_window_info,
    create_time_based_report,
    resumption_activity,
    create_process_dict,
    save_dict_to_txt,
    custom_format,
    format_time,
    format_day,
    get_config_info,
    handle_error,
    get_dict_from_config,
    start_time,
    current_window
)

""" # Функция-обработчик, которая будет вызвана при выходе из программы
def exit_handler():
    global start_time, current_window, current_process
    if start_time:
        end_time = time.time()
        create_time_based_report(start_time, end_time, current_window)
        create_process_dict(sections_file, active_window_info, start_time, end_time)
        save_dict_to_txt(f'activity_report_{custom_format()}.txt')

    print("Отчёты обновлены")
    
    # Запускаем основную функцию сортировки данных
    custom_sorting.main()

# Регистрируем функцию exit_handler как обработчик выхода
# Она будет автоматически вызвана при завершении программы
atexit.register(exit_handler)
 """

# True если создавать time_based_report
flag_time_based_report = False


# Файл для конфигов
config_file = 'config.txt'
sections_file = 'sections.txt'


# Получение конфигов
config_info = get_config_info(config_file)
sections_dict = get_dict_from_config(sections_file)

# Фиксирование сегодняшней даты
day = format_day()

# Кастомное фиксирование сегодняшней даты и времени
custom_date = custom_format()

# Лог-файлы\папки
time_based_report_directory = 'time_based_report_directory'
activity_report_directory = 'activity_report_directory'

activity_report = f'activity_report_{custom_date}.txt'
if flag_time_based_report:
    time_based_report = f'time_based_report_{custom_date}.txt'


# Техническая писанина
print(
    f'Программа запущена. Дата: {day}',
    f'Создан файл {activity_report}',
    sep='\n'
)

if flag_time_based_report:
    print(f'Создан файл {time_based_report}')

try: 
    # Бесконечный цикл для постоянного отслеживания активности
    print(f'Идёт отслеживание процессов')
    while True:

        # Получаем информацию об активном окне
        active_window_info = get_active_window_info()
        active_window_name = active_window_info['window_title']
        check_activity = resumption_activity(config_info)

        # Обработка состояния AFK (Away From Keyboard)
        if check_activity:
            afk_start, afk_end = check_activity

            # Формируем запись AFK в словарь процессов
            create_process_dict({'AFK':'AFK', 'AFK':'AFK', 'AFK':'AFK'}, afk_start, afk_end)
            # Сохраняем данные словаря
            save_dict_to_txt(activity_report, activity_report_directory)

            if flag_time_based_report:
                # Записываем время AFK в файл
                with open(time_based_report, 'a', encoding='utf-8') as file:
                    file.write(f'{format_time(check_activity[0])}-{format_time(check_activity[1])} : Время AFK\n')
        
            
        # Если текущее окно еще не определено
        elif current_window is None:
            start_time = time.time() # Запоминаем начальное время

        # Если активное окно изменилось    
        elif current_window != active_window_name:
            if start_time:
                end_time = time.time()  # Замеряем время окончания активности
                
                # Делаем записи в отчёты/словари
                create_process_dict(sections_dict, active_window_info, start_time, end_time)
                if flag_time_based_report:
                    create_time_based_report(start_time, end_time, current_window)
                
                # Сохраняем словарь в файл
                save_dict_to_txt(activity_report, activity_report_directory)
                
                start_time = time.time() # Обновляем начальное время
        
        # Обновляем текущие значения
        current_window = active_window_name


        time.sleep(config_info['check_time'])

except KeyboardInterrupt: 
    print("\nПрограмма остановлена пользователем")
    input("Нажмите Enter для выхода...")

except Exception as e:
    log_text = f'{format_time(time.time())} {day} Окончание работы программы. ' \
               f'Причина: {str(e)}\n' \
               f'Трассировка: {traceback.format_exc()}'
    print(log_text)


    