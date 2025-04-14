import time
from datetime import datetime
from functions import format_day, get_active_window_title, create_report, custom_format, create_structural_report
import atexit
import ctypes
import sys

dictionary = {}
current_window = None
start_time = None

with open(f'time_based_report_{custom_format()}.txt', 'w', encoding='utf-8') as file:
    file.write(f'Отчёт {format_day()}\n')
print(f'Программа запущена. Дата: {format_day()}')
print(f'Создан файл time_based_report_{custom_format()}.txt')

def exit_handler():
    global start_time, current_window, dictionary
    if start_time:
        end_time = time.time()
        create_report(start_time, end_time, current_window, dictionary)
        create_structural_report()
    print("Создан структурный отчёт")

atexit.register(exit_handler)

try:
    print('Отслеживание активных окон...\n')
    print('Нажмите Ctrl+C для завершения процесса и создания структурного отчёта')
    while True:
        new_window = get_active_window_title()
        
        if current_window is None:
            start_time = time.time()
        
        elif current_window != new_window:
            if start_time:
                end_time = time.time()
                create_report(start_time, end_time, current_window, dictionary)
                start_time = time.time()
        
        current_window = new_window
        time.sleep(1)

except KeyboardInterrupt: 
    print("\nПрограмма остановлена пользователем")







