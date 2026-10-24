def create_table(metadata, table_name, columns):
    """Создает таблицу, проверяет типы и добавляет ID."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return False

    allowed_types = ["int", "str", "bool"]
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

    # Добавляем ID в начало
    parsed_columns.insert(0, {"name": "ID", "type": "int"})

    metadata[table_name] = parsed_columns
    
    col_str = ", ".join([f"{c['name']}:{c['type']}" for c in parsed_columns])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {col_str}')
    
    return True


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return True


def list_tables(metadata):
    """Показывает список всех таблиц."""
    if not metadata:
        print("Список таблиц пуст.")
        return
    
    for table_name in metadata.keys():
        print(f"- {table_name}")