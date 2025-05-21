# Для ловли мышей
import pyautogui

# Переменные для отслеживания AFK (Away From Keyboard - так вот оно как)
current_cursor_coordinates: list = None # Текущие координаты курсора
afk_count: int = 0                      # Счетчик AFK
start_afk: float = 0                    # Время начала AFK
end_afk: float = 0                      # Время окончания AFK

def check_cursor_movement() -> bool:
    """
    Функция для проверки движения курсора мыши.
    
    Возвращает:
    - True, если курсор не двигался
    - False, если курсор двигался или определяется впервые
    """
    global current_cursor_coordinates

    new_cursor_coordinates = pyautogui.position()
    
    # Если координаты определены впервые
    if current_cursor_coordinates is None:
        current_cursor_coordinates = new_cursor_coordinates
        return False
    
    # Последующие итерации
    if current_cursor_coordinates != new_cursor_coordinates:
        current_cursor_coordinates = new_cursor_coordinates
        return False  # Курсор двигался
    
    return True  # Курсор не двигался
    

def update_afk_counter()-> None:
    """
    Обновляет счетчик бездействия.
    
    Увеличивает счетчик при отсутствии активности,
    сбрасывает при возобновлении активности.
    """
    global afk_count
    
    if check_cursor_movement():
        afk_count += 1
    else:
        afk_count = 0


def is_afk(config_info: dict, info: dict) -> bool:
    """
    Проверяет, находится ли пользователь в состоянии AFK.
    
    Параметры:
    config_info (dict): словарь с конфигурацией
        - afk_time: время бездействия в минутах
        - check_time: интервал проверки в секундах
    
    Возвращает:
    bool: True если пользователь AFK, иначе False
    """
    global afk_count
    
    update_afk_counter()
    afk_time = config_info.get('afk_time', 3)       # значение по умолчанию 60 секунд
    check_time = config_info.get('check_time', 5)   # значение по умолчанию 30 секунд
    
    threshold = afk_time * 60 / check_time
    
    if afk_count > threshold and not check_video(info):
        return True
    return False




list_video = ['мульт', 'фильм', 'аниме', 'сериал', 'cartoon', 'movie', 'anime', 'series', 'youtube']

def check_video(info: dict) -> bool:
    """
    Проверяет, имеет ли открытое окно в названии или в пути что-то связанное с медиа, чтобы исключить афк от просмотра видео

    Аргументы: 
    info(dict) - информация (словарь) об активном окне
    """
    for title in list_video:
        if title.lower() in info['process_path'].lower() or title.lower() in info['window_title'].lower():
            return True
    return False

        