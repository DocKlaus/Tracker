t= {'test': [''],
'test1': None,
'test2': 0}
for k,v in t.items():
    if v:
        print(f'{k} +')
    else:
        print(f'{k} -')

""" # Функция-обработчик, которая будет вызвана при выходе из программы
def exit_handler():
    global start_time, current_window, current_process
    if start_time:
        end_time = time.time()
        create_time_based_report(start_time, end_time, current_window)
        create_process_dict(sections_file, active_window_info, start_time, end_time)
        save_dict_to_txt(f'activity_report_{format_filename()}.txt')

    print("Отчёты обновлены")
    
    # Запускаем основную функцию сортировки данных
    custom_sorting.main()

# Регистрируем функцию exit_handler как обработчик выхода
# Она будет автоматически вызвана при завершении программы
atexit.register(exit_handler)
 """
