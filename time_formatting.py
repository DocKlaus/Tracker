import time

def format_time(timestamp: float) -> str:
    """
    Форматирует временную метку Unix в формат времени HH:MM:SS
    
    Параметры:
    timestamp (float): временная метка Unix
    
    Возвращает:
    str: отформатированное время в формате HH:MM:SS
    """
    time_struct = time.gmtime(timestamp)
    return time.strftime("%H:%M:%S", time_struct)


def format_date(today: float) -> str:
    """
    Форматирует дату в формат DD.MM.YYYY
    
    Параметры:
    today (float): временная метка Unix для текущей даты
    
    Возвращает:
    str: отформатированная дата в формате DD.MM.YYYY
    """
    time_struct = time.gmtime(today)
    return time.strftime("%d.%m.%Y", time_struct)


def format_filename(today: float) -> str:
    """
    Форматирует дату и время в формат для имени файла YYYY_MM_DD_HH_MM
    
    Параметры:
    today (float): временная метка Unix для текущей даты
    
    Возвращает:
    str: отформатированное имя файла в формате YYYY_MM_DD_HH_MM
    """
    time_struct = time.localtime(today)
    return time.strftime("%Y_%m_%d_%H_%M", time_struct)
