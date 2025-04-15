# Пользовательские модули
from functions import (
    custom_format,  
    format_day,
)

def main():
    # Читаем исходный отчет из файла
    
    with open(f'activity_report_{custom_format()}.txt', 'r', encoding='utf-8') as file:
    #with open(f'activity_report_2025_04_15_18_25.txt', 'r', encoding='utf-8') as file: # Раскомментрировать для отладки отдельного файла
        lines = file.readlines()  # Считываем все строки файла в список

    # Создаем структуру данных
    report = {}  # Словарь для хранения отчета
    current_process = None  # Текущий обрабатываемый процесс
    desktop_process = 'Процесс: Desktop'  # Создаем специальный процесс для Desktop

    # Создаем итератор из списка строк
    line_iterator = iter(lines)  # Преобразуем список в итератор для удобного прохода

    for line in line_iterator:
        line = line.strip()  # Убираем пробелы и переносы строк
        
        # Ищем процессы
        if line.startswith('Процесс:'):
            current_process = line  # Запоминаем текущий процесс
            report[current_process] = {
                'total': None,  # Общая длительность процесса
                'windows': []   # Список окон процесса
            }
            
        # Ищем общую длительность процесса
        elif line.startswith('Общая длительность:'):
            duration = line.split(': ')[1].strip()  # Извлекаем длительность
            if current_process is None:
                # Если процесс не определен, добавляем время в Desktop
                current_process = desktop_process
                report[current_process]['total'] = duration
            else:
                report[current_process]['total'] = duration  # Сохраняем в словарь
            
        # Ищем окна
        elif line.startswith('Окно:'):
            try:
                window_name = line.split(': ')[1].strip()  # Извлекаем название окна            
            except IndexError: 
                window_name = 'Desktop'

            # Читаем следующую строку для длительности окна
            duration_line = next(line_iterator, '').strip()  # Получаем следующую строку
            if duration_line.startswith('Длительность:'):
                duration = duration_line.split(': ')[1].strip()  # Извлекаем длительность
                if current_process is None:
                    # Если процесс не определен, добавляем окно в Desktop
                    report[desktop_process]['windows'].append({
                        'name': window_name,
                        'duration': duration
                    })
                else:
                    report[current_process]['windows'].append({
                        'name': window_name,  # Название окна
                        'duration': duration   # Длительность окна
                    })
        

    # Функция для сортировки по длительности
    def sort_by_duration(data):
        # Преобразуем длительность в секунды для корректной сортировки
        def duration_to_seconds(duration_str):
            parts = duration_str.split(':')  # Разбиваем строку на части
            if len(parts) == 3:  # Если формат ЧЧ:ММ:СС
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:  # Если формат ММ:СС
                return int(parts[0]) * 60 + int(parts[1])
            return 0  # Если формат некорректный
        
        # Сортируем процессы по общей длительности
        sorted_processes = sorted(data.items(), 
                                 key=lambda x: duration_to_seconds(x[1]['total']), 
                                 reverse=True)  # От большего к меньшему
        
        # Сортируем окна внутри каждого процесса
        for process, details in sorted_processes:
            details['windows'].sort(
                key=lambda x: duration_to_seconds(x['duration']), 
                reverse=True)  # От большего к меньшему
        
        return sorted_processes

    # Получаем отсортированный отчет
    sorted_report = sort_by_duration(report)

    # Записываем отсортированный отчет в тот же файл
    with open(f'activity_report_{custom_format()}.txt', 'w', encoding='utf-8') as file:
        file.write(f'Отчёт {format_day()} (произведена сортировка по длительности)\n')
        for process, details in sorted_report:
            file.write(f'{process}\n')  # Записываем название процесса
            file.write(f'Общая длительность: {details['total']}\n')  # Записываем общую длительность
            file.write('    Окна:\n')  # Заголовок раздела с окнами
            for window in details['windows']:
                file.write(f'       Окно: {window['name']}\n')  # Записываем название окна
                file.write(f'           Длительность: {window['duration']}\n')  # Записываем длительность окна
            file.write('\n')  # Добавляем пустую строку между процессами
            file.write("\n") # Добавляем пустую строку между процессами для читаемости
    print('Отчет успешно отсортирован и перезаписан!')

# Проверяем, что это основной исполняемый файл
if __name__ == '__main__':
    main()  # Вызываем главную функцию программы