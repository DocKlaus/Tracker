import time
import os
import traceback

def handle_error(message: str, flag_input: bool = True, error: str = '') -> None:
    """
    Функция для логирования ошибок и создания отчета
    
    Аргументы:
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