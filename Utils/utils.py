import base64
import functools
import hashlib
import re
import sys
from pathlib import Path

from Utils.log import log


def all_exception(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nПрограмма принудительно завершена пользователем.")
            sys.exit(0)
        except Exception as e:
            print(f"Произошла ошибка в работе программы: {e}")
            log.error(f'{e}')

    return wrapper


def to_md5(s: str):
    return hashlib.md5(s.encode()).hexdigest()


def clean_string(s: str) -> str:
    if type(s) is str:
        s = s.replace(',', ', ')
        s = re.sub(r'\s{2,}', ' ', s)
        s = s.strip()
    elif s in ('None', '#N/A', None):
        s = ''
    return s


def file_to_base64(file_path_str: str) -> str:
    path = Path(file_path_str)

    if not path.exists():
        print(f"Ошибка: Путь '{path}' не существует.")
        return None
    if not path.is_file():
        print(f"Ошибка: '{path}' не является файлом.")
        return None

    try:
        file_bytes_data = path.read_bytes()

        # Кодируем в Base64
        base64_bytes = base64.b64encode(file_bytes_data)

        # Возвращаем строку
        return base64_bytes.decode('utf-8')

    except Exception as e:
        print(f"Произошла ошибка при обработке файла: {e}")
        return None
