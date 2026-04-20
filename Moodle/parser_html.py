import json
import re
from asyncio import sleep
from pathlib import Path
from pprint import pprint

import dateparser
from bs4 import BeautifulSoup

from EXCEL.excel_reader import get_all_questions_from_excel_file
from My_jinja import MyJinja
from Question import Question
from Utils.log import log
from Utils.translit import replace_ru_char_to_eng_char
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


def parse_data_questions_html(html_content):
    try:
        email = ''
        if html_content:
            f_line = html_content.split('\n')
            if f_line:
                f_line = f_line[0]
                parrent = re.findall(r"""user_email\=['"].*['"]""", f_line)
                if parrent:
                    parrent = parrent[0]
                    email = re.findall(r"""user_email\=['"](.*)['"]""", parrent)[0]
                    html_content = re.sub(parrent, '', html_content).strip()

        parsed_data = parse_quiz_review(html_content)

        a = json.dumps(parsed_data, indent=4, ensure_ascii=False)
        python_object = json.loads(a)
        return email, python_object
    except Exception as e:
        print(f"Произошла ошибка при парсинге: {e}")
        return '', None


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

    html_content = MyJinja(template_folder='./Moodle/template_html', template_file='report.html').template_file.render(
        user=test_info.get('user', ''),
        time_end=test_info.get('Завершен', ''),
        time_start=test_info.get('Тест начат', ''),
        email=test_info.get('email', ''),
        table_rows=table_rows,
        test_name=test_info.get('test_name', ''),
        all_category_correct=all_category_correct,
        all_category_total=all_category_total,
    )

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n✅ HTML-отчет успешно создан: {filename}")
    except Exception as e:
        print(f"\n❌ Ошибка при записи файла: {e}")


def clean_test_infp(data):
    # Очистка и нормализация текста
    for key, value in data.items():
        if isinstance(data[key], str):
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


def get_all_questions_from_xlsx(dir=QUESTION_INPUT_DIR_XLSX):
    exams_name_path = {}
    for file in dir.glob('*.xlsx'):
        exam_name = re.sub(r'.xlsx$', '', file.name)
        exams_name_path[exam_name] = file

    all_questions = []
    for exam_name, file in exams_name_path.items():
        all_questions.extend(get_all_questions_from_excel_file(file))

    return all_questions


def generate_report(filename: Path, all_questions):
    all_questions = all_questions[:]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()

        email, data = parse_data_questions_html(html_content)
        if not data:
            return
        if not data or data['test_info']['Состояние'].lower() not in ('завершены',):
            return

        questions_user_json = data['questions']
        test_info = data['test_info']
        exam = data['test_info'].get('test_name').replace(' ТЕСТ', '')
        if email:
            test_info['email'] = email

        questions_user = []
        for i, q in enumerate(questions_user_json):
            c = Question(
                text_question=q.get('question_text'),
                ans_a=q.get('answers')[0],
                ans_b=q.get('answers')[1],
                ans_c=q.get('answers')[2],
                ans_d=q.get('answers')[3],
            )
            c.status = q.get('status')
            c.exam = exam
            questions_user.append(c)

        if len(questions_user_json) != len(questions_user):
            return 'len(questions_user_json) != len(questions_user)'

        all_questions = [q for q in all_questions if
                         replace_ru_char_to_eng_char(exam.lower()) == replace_ru_char_to_eng_char(q.exam.lower())]

        all_questions_filtered = []
        not_questions = []
        for q in questions_user:
            if q in all_questions:
                all_questions_filtered.append(q)
            else:
                not_questions.append(q)

        if not_questions:
            print(f'!!! not_questions !!! {len(not_questions)}\n\n')
            return None

        answer_category = {}
        all_category = {}
        for q in all_questions:
            answer_category[q.category] = 0
            all_category[q.category] = 0

        for i, q in enumerate(questions_user):
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
    except Exception as e:
        log.error(f'{e}')
        return


async def create_all_report(is_only_new_report=True):
    dir_path = DIR_HTML_DOWNLOAD
    dir_report_path = DIR_REPORTS
    all_file = [filename_path for filename_path in dir_path.glob('*.html')] or []
    all_report_names = [filename_path.name for filename_path in dir_report_path.glob('*.html')] or []

    if is_only_new_report:
        all_file_filtered = [f for f in all_file if
                             not any(f'_{f.name}' in report for report in all_report_names)] or []
    else:
        all_file_filtered = all_file

    all_questions = get_all_questions_from_xlsx()
    for file in all_file_filtered:
        print(f'\n{file}')
        generate_report(filename=Path(file), all_questions=all_questions)
        await sleep(0.5)
