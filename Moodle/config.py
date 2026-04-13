from pathlib import Path

from dotenv import dotenv_values, find_dotenv

config = dotenv_values(find_dotenv())

LOGIN_MOODLE = config.get('LOGIN_MOODLE')
PASSWORD_MOODLE = config.get('PASSWORD_MOODLE')
MOODLE_TOKEN = config.get('MOODLE_TOKEN')
MOODLE_URL = config.get('MOODLE_URL')

BASE_URL = 'https://exam.itexpert.ru'

DIR_BASE = Path(
    '//192.168.20.100/Administrative server/РАБОТА АДМИНИСТРАТОРА/ОРГАНИЗАЦИЯ IT ЭКЗАМЕНОВ/ЭКЗАМЕНЫ ЦИФРОВОЙ ПУТЬ')
DIR_CERTS = DIR_BASE / 'сертификат'
DIR_HTML_DOWNLOAD = DIR_BASE / 'DOWNLOAD_Moodle'
DIR_HTML_DOWNLOAD.mkdir(exist_ok=True, parents=True)
DIR_REPORTS = DIR_BASE / 'Результаты HTML'
DIR_REPORTS.mkdir(exist_ok=True, parents=True)
QUESTION_INPUT_DIR_XLSX = DIR_BASE / 'questions_xlsx'
QUESTION_INPUT_DIR_XLSX.mkdir(exist_ok=True, parents=True)

if not LOGIN_MOODLE:
    raise f'ERROR .ENV {MOODLE_TOKEN=}'
if not PASSWORD_MOODLE:
    raise f'ERROR .ENV {MOODLE_URL=}'
if not MOODLE_TOKEN:
    raise f'ERROR .ENV {MOODLE_TOKEN=}'
if not MOODLE_URL:
    raise f'ERROR .ENV {MOODLE_URL=}'
