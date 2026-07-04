from pathlib import Path

def load_config(config_path : Path):
    """Парсит файл конфига для получения нужных параметров

    Args:
        config_path (pathlib.Path): Путь до файла конфига
    Returns:
        Dict[str, Any]: Словарь полученный из конфига
    """
    variables = {}
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = [x.strip() for x in line.split('=', 1)]
                try:
                    if '.' in value:
                        variables[key] = float(value)
                    else:
                        variables[key] = int(value)
                except ValueError:
                    if value.lower() in {'true', 'yes', 'on'}:
                        variables[key] = True
                    elif value.lower() in {'false', 'no', 'off'}:
                        variables[key] = False
                    else:
                        variables[key] = value
    return variables