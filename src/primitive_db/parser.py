import shlex


def parse_value(val_str):
    """Преобразует строку в Python-тип (int, bool, str)."""
    val_str = val_str.strip()
    if (val_str.startswith('"') and val_str.endswith('"')) or \
       (val_str.startswith("'") and val_str.endswith("'")):
        return val_str[1:-1]
    if val_str.lower() == "true":
        return True
    if val_str.lower() == "false":
        return False
    try:
        return int(val_str)
    except ValueError:
        return val_str

def parse_where(where_parts):
    """Превращает ['age', '=', '28'] в {'age': 28}."""
    if not where_parts:
        return {}
    if len(where_parts) != 3 or where_parts[1] != "=":
        raise ValueError("Некорректное условие WHERE. Формат: <столбец> = <значение>")
    column = where_parts[0]
    value = parse_value(where_parts[2])
    return {column: value}

def parse_set(set_parts):
    """Превращает ['age', '=', '29'] в {'age': 29}."""
    if not set_parts:
        return {}
    if len(set_parts) != 3 or set_parts[1] != "=":
        raise ValueError("Некорректное условие SET. Формат: <столбец> = <значение>")
    column = set_parts[0]
    value = parse_value(set_parts[2])
    return {column: value}

def parse_values(values_str):
    """Разбирает строку ('Sergei', 28, true) в список [Sergei, 28, True]."""
    if not (values_str.startswith("(") and values_str.endswith(")")):
        raise ValueError("Ожидаются скобки для VALUES")
    
    inner = values_str[1:-1]
    lexer = shlex.shlex(inner, posix=True)
    lexer.whitespace = ","
    lexer.whitespace_split = True
    lexer.quotes = '"\''
    tokens = list(lexer)
    return [parse_value(t) for t in tokens]