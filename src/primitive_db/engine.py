import os
import shlex

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    print_table,
    select,
    update,
)
from primitive_db.parser import parse_set, parse_values, parse_where
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

DB_FILE = "db_meta.json"

def print_help():
    print("\n***Операции с данными***")
    print("Функции:")
    print('<command> insert into <имя> values (...) - создать запись.')
    print('<command> select from <имя> where <столбец> = <значение>')
    print('  - прочитать записи по условию.')
    print('<command> select from <имя> - прочитать все записи.')
    print('<command> update <имя> set <столбец> = <новое> where ... - обновить запись.')
    print('<command> delete from <имя> where <столбец> = <значение> - удалить запись.')
    print('<command> info <имя> - вывести информацию о таблице.')
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
            print("Ошибка в синтаксисе команды.")
            continue

        command = args[0].lower()
        
        try:
            if command == "exit":
                print("Выход из программы.")
                break
            elif command == "help":
                print_help()
            elif command == "create_table":
                if len(args) < 3:
                    print("Ошибка: Недостаточно аргументов.")
                    continue
                success = create_table(metadata, args[1], args[2:])
                if success:
                    save_metadata(DB_FILE, metadata)
            elif command == "drop_table":
                if len(args) != 2:
                    print("Ошибка: Использование: drop_table <имя>")
                    continue
                success = drop_table(metadata, args[1])
                if success:
                    save_metadata(DB_FILE, metadata)
                    if os.path.exists(f"data/{args[1]}.json"):
                        os.remove(f"data/{args[1]}.json")
            elif command == "list_tables":
                list_tables(metadata)
            elif command == "insert" and len(args) >= 5 and args[1] == "into":
                table_name = args[2]
                if args[3] != "values":
                    print("Ошибка: Ожидается 'values'")
                    continue
                values_str = " ".join(args[4:])
                values = parse_values(values_str)
                record = insert(metadata, table_name, values)
                if record:
                    table_data = load_table_data(table_name)
                    new_id = max([r["ID"] for r in table_data], default=0) + 1
                    record = {"ID": new_id, **record}
                    table_data.append(record)
                    save_table_data(table_name, table_data)
                    print(f'Запись с ID={new_id} добавлена в таблицу "{table_name}".')
            elif command == "select" and len(args) >= 3 and args[1] == "from":
                table_name = args[2]
                where_clause = None
                if len(args) > 3 and args[3] == "where":
                    where_clause = parse_where(args[4:])
                table_data = load_table_data(table_name)
                result = select(table_data, where_clause)
                if result:
                    print_table(metadata, table_name, result)
                else:
                    print("Записи не найдены.")
            elif command == "update" and len(args) >= 5:
                table_name = args[1]
                if args[2] != "set":
                    print("Ошибка: Ожидается 'set'")
                    continue
                where_idx = -1
                for i, a in enumerate(args):
                    if a == "where":
                        where_idx = i
                        break
                if where_idx == -1:
                    print("Ошибка: Ожидается 'where'")
                    continue
                set_clause = parse_set(args[3:where_idx])
                where_clause = parse_where(args[where_idx+1:])
                table_data = load_table_data(table_name)
                table_data, count = update(table_data, set_clause, where_clause)
                if count > 0:
                    save_table_data(table_name, table_data)
                    print(f'Запись в таблице "{table_name}" обновлена.')
                else:
                    print("Записи для обновления не найдены.")
            elif command == "delete" and len(args) >= 5 and args[1] == "from":
                table_name = args[2]
                if args[3] != "where":
                    print("Ошибка: Ожидается 'where'")
                    continue
                where_clause = parse_where(args[4:])
                table_data = load_table_data(table_name)
                table_data, count = delete(table_data, where_clause)
                if count > 0:
                    save_table_data(table_name, table_data)
                    print(f'Запись удалена из таблицы "{table_name}".')
                else:
                    print("Записи для удаления не найдены.")
            elif command == "info" and len(args) == 2:
                table_name = args[1]
                table_data = load_table_data(table_name)
                info(metadata, table_name, table_data)
            else:
                print(f"Функции {command} нет. Попробуйте снова.")
        except ValueError as e:
            print(f"Ошибка в команде: {e}")
        except Exception as e:
            print(f"Произошла ошибка: {e}")