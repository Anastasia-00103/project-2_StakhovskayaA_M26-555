from prettytable import PrettyTable

from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time


def create_table(metadata, table_name, columns):
    """Создает новую таблицу с указанными столбцами."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return False

    allowed_types = VALID_TYPES
    parsed_columns = []
    
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return False
        name, col_type = col.split(":", 1)
        if col_type not in allowed_types:
            print(f"Некорректное значение: {col_type}. Попробуйте снова.")
            return False
        parsed_columns.append({"name": name, "type": col_type})

    parsed_columns.insert(0, {"name": "ID", "type": "int"})
    metadata[table_name] = parsed_columns
    
    col_str = ", ".join([f"{c['name']}:{c['type']}" for c in parsed_columns])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {col_str}')
    return True


@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata, table_name):
    """Удаляет таблицу из базы данных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return True


def list_tables(metadata):
    """Выводит список всех существующих таблиц."""
    if not metadata:
        print("Список таблиц пуст.")
        return
    for table_name in metadata.keys():
        print(f"- {table_name}")


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблицы "{table_name}" не существует.')
        return None
    columns = metadata[table_name]
    if len(values) != len(columns) - 1:
        print(f"Ошибка: Ожидалось {len(columns) - 1} значений, получено {len(values)}.")
        return None
    
    record = {}
    for i, col in enumerate(columns[1:]):
        val = values[i]
        expected_type = col["type"]
        
        if expected_type == "int":
            val = int(val)
        elif expected_type == "bool":
            if isinstance(val, str):
                val = val.lower() == "true"
            else:
                val = bool(val)
        elif expected_type == "str":
            val = str(val)
            
        record[col["name"]] = val
    return record


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает записи из таблицы, соответствующие условию."""
    if not where_clause:
        return table_data
    result = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if str(row.get(col)) != str(val):
                match = False
                break
        if match:
            result.append(row)
    return result


def update(table_data, set_clause, where_clause):
    """Обновляет записи в таблице, соответствующие условию."""
    updated_count = 0
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if str(row.get(col)) != str(val):
                match = False
                break
        if match:
            for col, val in set_clause.items():
                old_val = row.get(col)
                if isinstance(old_val, int):
                    row[col] = int(val)
                elif isinstance(old_val, bool):
                    row[col] = str(val).lower() == "true"
                else:
                    row[col] = str(val)
            updated_count += 1
    return table_data, updated_count


@confirm_action("удаление записи из таблицы")
@handle_db_errors
def delete(table_data, where_clause):
    """Удаляет записи из таблицы, соответствующие условию."""
    if not where_clause:
        print("Ошибка: Удаление без условия WHERE не поддерживается.")
        return table_data, 0
    initial_len = len(table_data)
    result_data = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if str(row.get(col)) != str(val):
                match = False
                break
        if not match:
            result_data.append(row)
    deleted_count = initial_len - len(result_data)
    return result_data, deleted_count


def info(metadata, table_name, table_data):
    """Выводит информацию о таблице."""
    if table_name not in metadata:
        print(f'Ошибка: Таблицы "{table_name}" не существует.')
        return
    cols = metadata[table_name]
    col_str = ", ".join([f"{c['name']}:{c['type']}" for c in cols])
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {col_str}")
    print(f"Количество записей: {len(table_data)}")


def print_table(metadata, table_name, table_data):
    """Выводит данные таблицы в красивом табличном формате."""
    cols = metadata[table_name]
    pt = PrettyTable()
    pt.field_names = [c["name"] for c in cols]
    for row in table_data:
        pt.add_row([row.get(c["name"], "") for c in cols])
    print(pt)