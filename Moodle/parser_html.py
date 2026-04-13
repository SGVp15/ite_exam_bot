import json
import os
import re
from pathlib import Path
from pprint import pprint

import dateparser
from bs4 import BeautifulSoup

from EXCEL.excel_reader import get_all_questions_from_excel_file
from Question import Question
from Utils.utils import get_all_files_from_pattern
from .config import QUESTION_INPUT_DIR_XLSX, DIR_HTML_DOWNLOAD, DIR_REPORTS


def parse_quiz_review(html_content: str) -> dict:
    """
    Извлекает информацию о тесте, вопросы, ответы пользователя, правильные ответы
    и полный список всех вариантов ответа, ограничивая поиск блоком role="main".
    """
    test_info = 'test_info'
    soup = BeautifulSoup(html_content, 'html.parser')
    results = {test_info: {}, 'questions': []}

    # название теста из заголовка
    if 'название_теста' not in results[test_info]:
        test_title_tag = soup.find('h1', class_="h2 mb-0")
        if test_title_tag:
            results[test_info]['test_name'] = test_title_tag.text

    # --- 1. Ограничение поиска блоком div role="main" ---
    main_content = soup.find('div', role='main')
    if not main_content:
        results['error'] = 'Ошибка: Основной блок контента (div role="main") не найден.'
        return results

    # --- 2. Общая информация о тесте (generaltable quizreviewsummary) ---
    summary_table = main_content.find('table', class_='generaltable generalbox quizreviewsummary mb-0')

    if summary_table:
        for i, row in enumerate(summary_table.find_all('tr')):
            header = row.find('th')
            data = row.find('td')
            if header and data:
                header_text = header.text.strip()
                data_text = data.text.strip()
                results[test_info][header_text] = data_text
                if i == 0:
                    results[test_info]['user'] = data_text
    try:
        name_tag = soup.find('div', class_='card-text content mt-3').find('div', class_='clearfix')
        if name_tag:
            text = re.findall(r'title="([\w\s]+)"', str(name_tag))
            if text:
                results[test_info]['user'] = text[0]
            else:
                keys_exp = set(
                    ['test_name', 'Состояние', 'Тест начат', 'Завершен', 'Затраченное время', 'Оценка', 'Отзыв'])
                k = ''.join(list(set(results[test_info].keys()) - keys_exp)[0])
                results[test_info]['user'] = results[test_info][k]
    except (KeyError, IndexError) as e:
        return None

    # --- 3. Вопросы, ответы и все варианты ---
    # Ищем все блоки вопросов внутри main_content
    question_blocks = main_content.find_all('div', class_=re.compile(r'^que '))

    for q_block in question_blocks:
        question_data = {}

        # Номер вопроса и статус
        q_no_tag = q_block.find('span', class_='qno')
        question_data['number'] = q_no_tag.text.strip() if q_no_tag else 'N/A'
        q_state_tag = q_block.find('div', class_='state')
        question_data['status'] = q_state_tag.text.strip() if q_state_tag else 'N/A'

        grade_tag = q_block.find('div', class_='grade')
        question_data['points'] = grade_tag.text.strip() if grade_tag else 'Баллы не найдены'

        q_text_tag = q_block.find('div', class_='qtext')
        question_data['question_text'] = re.sub(r'\s+', ' ',
                                                q_text_tag.text.strip()) if q_text_tag else 'Текст вопроса не найден'

        # --- Извлечение всех вариантов ответа (data-region="answer-label") ---
        all_options = []
        answer_container = q_block.find('div', class_='answer')

        if answer_container:
            # Проходим по всем блокам вариантов (r0, r1, r2...)
            for option_div in answer_container.find_all('div', recursive=False):
                if not re.match(r'r\d+', ' '.join(option_div.get('class', []))):
                    continue

                # Ищем контейнер текста ответа (по data-region="answer-label")
                label_div = option_div.find('div', attrs={'data-region': 'answer-label'})
                option_text_tag = label_div.find('div', class_='flex-fill') if label_div else None
                option_text = option_text_tag.text.strip() if option_text_tag else 'Текст варианта не найден'

                all_options.append(re.sub(r'\s+', ' ', option_text).strip())

        question_data['answers'] = all_options
        results['questions'].append(question_data)
    return results


def parse_data_questions_html(filename):
    try:
        email = ''
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        if html_content:
            if html_content[0]:
                email_match = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', html_content[0])
                if email_match:
                    email = re.sub(r'.*=', '', html_content[0])
                    html_content = html_content[1:]
        parsed_data = parse_quiz_review(html_content)

        a = json.dumps(parsed_data, indent=4, ensure_ascii=False)
        python_object = json.loads(a)
        return email, python_object
    except FileNotFoundError:
        print("Ошибка: Файл не найден.")
    except Exception as e:
        print(f"Произошла ошибка при парсинге: {e}")


def create_html_page_report(test_info: dict, all_category: dict, answer_category: dict, filename="quiz_report.html"):
    """
    Генерирует полную HTML-страницу с информацией о тесте и результатами по категориям.
    """
    sorted_keys = sorted(all_category.keys())

    table_rows = ""
    all_category_correct = 0
    all_category_total = 0
    for k in sorted_keys:
        total = all_category[k]
        correct = answer_category[k]
        all_category_total += total
        all_category_correct += correct
        percentage = (correct / total * 100) if total > 0 else 0

        # Строка таблицы для категории
        table_rows += f"""
        <tr>
            <td>{k}</td>
            <td class="numeric correct">{correct}</td>
            <td class="numeric total">{total}</td>
            <td class="numeric">
                <div class="progress-bar">
                    <div style="width: {percentage:.0f}%;" class="progress-fill pass "></div>
                </div>
            </td>
        </tr>
        """

    # --- 2. HTML-шаблон ---
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет по тесту: {test_info.get('test_name', 'Без названия')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f9;
            color: #333;
        }}
        .container {{
            max-width: 900px;
            margin: auto;
            background: #fff;
            padding: 20px 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            color: #0056b3;
            border-bottom: 3px solid #0056b3;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-bottom: 1px dashed #ccc;
            padding-bottom: 5px;
        }}
        .summary-box {{
            background: #e9f7ff;
            border: 1px solid #b3e0ff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary-box p {{
            margin: 5px 0;
            line-height: 1.5;
        }}
        .summary-box strong {{
            color: #0056b3;
            display: inline-block;
            width: 150px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .numeric {{
            text-align: center;
            width: 80px;
        }}
        .grade-score {{
            font-size: 1.5em;
            font-weight: bold;
            color: #444444;
        }}
        .progress-bar {{
            background-color: #e0e0e0;
            border-radius: 4px;
            height: 25px;
            overflow: hidden;
            width: 150px;
            margin: 0 auto;
        }}
        .progress-fill {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.9em;
            transition: width 0.5s ease-in-out;
        }}
        .pass {{
            background-color: #28a745; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Отчет о прохождении экзамена: {test_info.get('test_name', 'Н/Д')}</h1>
        <h2>Общая информация</h2>
        <div class="summary-box">
            <p><strong>Пользователь:</strong> {test_info.get('user', 'Н/Д')}</p>
            <p><strong>Начало экзамена:</strong> {test_info.get('Тест начат', 'Н/Д')}</p>
            <p><strong>Завершение экзамена:</strong> {test_info.get('Завершен', 'Н/Д')}</p>
            <p><strong>Проходной балл:</strong> <span class="grade-score"> 21</span></p>
            <p><strong>Итоговая оценка:</strong> <span class="grade-score"> {all_category_correct} / {all_category_total}</span></p>
        </div>

        <h2>Результаты по категориям</h2>
        <table>
            <thead>
                <tr>
                    <th>Категория</th>
                    <th class="numeric">Верно</th>
                    <th class="numeric">Всего</th>
                    <th class="numeric"></th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
</body>
</html>"""

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n✅ HTML-отчет успешно создан: {filename}")
    except Exception as e:
        print(f"\n❌ Ошибка при записи файла: {e}")


def clean_test_infp(data):
    # Очистка и нормализация текста
    for key, value in data.items():
        data[key] = re.sub(r'\s+', ' ', value).strip()
    try:
        data['Оценка'] = re.sub(r',\d+', '', data['Оценка'])
    except KeyError:
        pass
    try:
        data['test_info'] = re.sub(r'[А-Яа-яёЁ]', '', data['test_info']).strip()
    except KeyError:
        pass
    return data


def get_all_questions_from_xlsx():
    exams_name_path = {}
    for file in get_all_files_from_pattern(QUESTION_INPUT_DIR_XLSX, '.xlsx'):
        exam_name = re.sub(r'.xlsx$', '', os.path.basename(file))
        exams_name_path[exam_name] = file

    all_questions = []
    for exam_name, file in exams_name_path.items():
        all_questions.extend(get_all_questions_from_excel_file(file))

    return all_questions


def generate_report(filename: Path, all_questions):
    email, data = parse_data_questions_html(filename=filename)
    if not data:
        return
    q_my = data['questions']
    test_info = data['test_info']
    if email:
        test_info['email'] = email
    quests = []
    for i, q in enumerate(q_my):
        c = Question(
            text_question=q.get('question_text'),
            ans_a=q.get('answers')[0],
            ans_b=q.get('answers')[1],
            ans_c=q.get('answers')[2],
            ans_d=q.get('answers')[3])

        c.status = q.get('status')
        # print(q.get('number'), c.status , q.get('status'))
        quests.append(c)
    all_questions = [q for q in all_questions if q in quests]
    not_questions = [q for q in all_questions if q not in quests]
    if not_questions:
        print(f'NO_questions\t{len(not_questions)}')
    answer_category = {}
    all_category = {}
    for q in all_questions:
        answer_category[q.category] = 0
        all_category[q.category] = 0

    for i, q in enumerate(quests):
        q: Question
        for q_all in all_questions:
            q_all: Question
            if q == q_all:
                all_category[q_all.category] += 1
                if q.status == 'Верно':
                    answer_category[q_all.category] += 1
                break
    test_info = clean_test_infp(test_info)
    pprint(test_info)
    date_start = dateparser.parse(test_info['Тест начат'])
    print(f'{date_start=}')
    try:
        print(test_info['Завершен'])
    except KeyError:
        pass

    for k in sorted(all_category.keys()):
        print(f'{k}\t{answer_category[k]}\t{all_category[k]}')

    report_filename = DIR_REPORTS / f'r_{date_start.strftime('%Y.%m.%d')}_{test_info['test_name']}_{test_info['user']}_{filename.name}'
    create_html_page_report(test_info, all_category, answer_category, filename=report_filename)


def create_all_report(is_only_new_report=True):
    dir_path = DIR_HTML_DOWNLOAD
    dir_report_path = DIR_REPORTS
    all_file = []
    all_report_names = []
    all_questions = get_all_questions_from_xlsx()

    for filename_path in dir_path.glob('*.html'):
        all_file.append(filename_path)
    for filename_path in dir_report_path.glob('*.html'):
        all_report_names.append(filename_path.name)

    if is_only_new_report:
        all_file_filtered = [f for f in all_file if not any(f.name in report for report in all_report_names)] or []
    else:
        all_file_filtered = all_file

    for filename_path in all_file_filtered:
        print(f'\n{filename_path}')
        generate_report(filename=Path(filename_path), all_questions=all_questions)
