# Время по Unix (секунды)
import time

# Взаимодействие с ОС
import os

# Понятный ошибка - хороший ошибка
import traceback

def handle_error(message: str, flag_input: bool = True, error: str = '') -> None:
    """
    Функция для логирования ошибок и создания отчета. -- НА ПЕРЕДЕЛКУ --
    
    Аргументы:
    message (str): сообщение об ошибке
    flag_input (bool): показывать ли приглашение для выхода
    error (str): дополнительная информация об ошибке
    """
    
    # Директория для логов
    error_dir = 'error_logs'

    if not os.path.exists(error_dir):
        os.makedirs(error_dir, exist_ok=True)
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    log_file = f'{error_dir}/Error_report_{timestamp}.txt'
    
    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(f'[Ошибка] {time.strftime("%Y-%m-%d %H:%M:%S")} - {message}\n')
        file.write(f'Дополнительная информация: {error}\n')
        file.write(f'Трассировка:\n{traceback.format_exc()}\n')
        
    print(f'\n[Ошибка] {time.strftime("%Y-%m-%d %H:%M:%S")} - {message}\n')
    
    # Ждем ввода, если флаг установлен
    if flag_input:
        input("Нажмите Enter для выхода...")