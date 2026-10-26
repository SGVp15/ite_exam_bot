import re
from pathlib import Path
from pprint import pprint

import dateparser
from selectolax.lexbor import LexborHTMLParser

from Moodle.config import PATH_DIR_REPORTS


def parser_report(file: Path):
    if not file:
        return {}
    with open(file, mode='r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()
    # движок Lexbor (он быстрее и современнее стандартного Modest)
    parser = LexborHTMLParser(html_content)

    # 1. Извлекаем название экзамена
    h1_node = parser.css_first('h1')
    exam_name = h1_node.text(strip=True).replace('Отчет о прохождении экзамена:', '').strip() if h1_node else None

    # 2. Извлекаем данные из блока summary-box
    # Ищем все теги <p> внутри .summary-box
    nodes = parser.css('.summary-box p')

    data = {}
    data['exam_name'] = exam_name
    for node in nodes:
        strong_node = node.css_first('strong')
        if strong_node:
            key = strong_node.text(strip=True).replace(':', '')
            # Метод .text() с deep=False позволяет взять текст ТОЛЬКО самого узла p,
            # исключая текст внутри вложенного strong.
            value = node.text(deep=False).strip()
            data[key] = value
    data_return = {}
    data_return['exam_name'] = re.sub(r'[^\dA-Za-z]+', '', data.get('exam_name'))
    data_return['date'] = dateparser.parse(data.get('Начало экзамена')).date()
    data_return['username'] = data.get('Пользователь')
    data_return['file'] = file

    return data_return


def parse_all_repots(path=PATH_DIR_REPORTS):
    # Определяем путь к папке
    reports_dir = path
    list_return = []
    # Проверяем, существует ли папка, чтобы избежать ошибок
    if reports_dir.exists() and reports_dir.is_dir():
        # Итерируемся по всем файлам .html (или всем файлам)
        for file_path in reports_dir.glob('*.html'):
            # Передаем объект Path целиком
            report_data = parser_report(file_path)
            list_return.append(report_data)
    else:
        print(f"Ошибка: Директория {reports_dir} не найдена.")
    return list_return


if __name__ == '__main__':
    pprint(parse_all_repots())
