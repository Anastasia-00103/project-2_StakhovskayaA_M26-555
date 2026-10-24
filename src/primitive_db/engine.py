import shlex

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

DB_FILE = "db_meta.json"

def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    print("\n***База данных***")
    print_help()

    while True:
        metadata = load_metadata(DB_FILE)
        
        try:
            user_input = input(">>>Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход из программы.")
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка в синтаксисе команды. Проверьте кавычки.")
            continue

        command = args[0].lower()
        
        if command == "exit":
            print("Выход из программы.")
            break
        elif command == "help":
            print_help()
        elif command == "create_table":
            if len(args) < 3:
                # Разбили длинную строку на две
                print("Ошибка: Недостаточно аргументов. Использование:")
                print("create_table <имя> <столбец:тип> ...")
                continue
            table_name = args[1]
            columns = args[2:]
            
            # Проверяем, была ли таблица создана успешно
            success = create_table(metadata, table_name, columns)
            if success:
                save_metadata(DB_FILE, metadata)
                
        elif command == "drop_table":
            if len(args) != 2:
                print("Ошибка: Использование: drop_table <имя_таблицы>")
                continue
            table_name = args[1]
            
            success = drop_table(metadata, table_name)
            if success:
                save_metadata(DB_FILE, metadata)
                
        elif command == "list_tables":
            list_tables(metadata)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")