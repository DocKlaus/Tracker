# Системные модули
import time
from datetime import datetime
import atexit
import custom_sorting

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
    process_dict,
    start_time,
    current_window
)

# Функция-обработчик, которая будет вызвана при выходе из программы
def exit_handler():
    global start_time, current_window, current_process
    if start_time:
        end_time = time.time()
        create_time_based_report(start_time, end_time, current_window)
        create_process_dict(current_process, current_window, start_time, end_time)
        save_dict_to_txt(f'activity_report_{custom_format()}.txt', process_dict)

    print("Отчёты обновлены")
    
    # Запускаем основную функцию сортировки данных
    custom_sorting.main()

# Регистрируем функцию exit_handler как обработчик выхода
# Она будет автоматически вызвана при завершении программы
atexit.register(exit_handler)


#  Создаём файл для повременного отчёта
with open(f'time_based_report_{custom_format()}.txt', 'w', encoding='utf-8') as file:
    file.write(f'Отчёт {format_day()}\n')

#  Создаём файл для отчёта активности
with open(f'activity_report_{custom_format()}.txt', 'w', encoding='utf-8') as file:
    file.write(f'Отчёт {format_day()}\n')

# Техническая писанина
print(f'Программа запущена. Дата: {format_day()}')
print(f'Создан файл time_based_report_{custom_format()}.txt')
print(f'Создан файл activity_report_{custom_format()}.txt.txt')

try:
    # Бесконечный цикл для постоянного отслеживания активности
    while True:
        # Получаем информацию об активном окне
        active_window_info = get_active_window_info()
        active_window_name = active_window_info['window_title']
        active_process_name = active_window_info['process_name']
        check_activity = resumption_activity()

        # Если текущее окно еще не определено
        if current_window is None:
            start_time = time.time() # Запоминаем начальное время

        # Если активное окно изменилось    
        elif current_window != active_window_name:
            if start_time:
                end_time = time.time()  # Замеряем время окончания активности

                # Делаем записи в отчёты/словари
                create_time_based_report(start_time, end_time, current_window)
                create_process_dict(current_process, current_window, start_time, end_time)
                
                # Сохраняем словарь в файл
                save_dict_to_txt(f'activity_report_{custom_format()}.txt', process_dict)
                
                start_time = time.time() # Обновляем начальное время
        

        # Обработка состояния AFK (Away From Keyboard)
        elif check_activity:
            # Записываем время AFK в файл
            with open(f'time_based_report_{custom_format()}.txt', 'a', encoding='utf-8') as file:
                file.write(f'{format_time(check_activity[0])}-{format_time(check_activity[1])} : Время AFK\n')
            
            afk_start, afk_end = check_activity

            # Формируем запись AFK в словарь процессов
            create_process_dict('AFK', 'AFK', afk_start, afk_end)
            # Сохраняем данные словаря
            save_dict_to_txt(f'activity_report_{custom_format()}.txt', process_dict)

        # Обновляем текущие значения
        current_window = active_window_name
        current_process = active_process_name

        time.sleep(5)

except KeyboardInterrupt: 
    print("\nПрограмма остановлена пользователем")