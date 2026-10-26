from pathlib import Path

from dotenv import dotenv_values, find_dotenv

config = dotenv_values(find_dotenv())

LOGIN_MOODLE = config.get('LOGIN_MOODLE')
PASSWORD_MOODLE = config.get('PASSWORD_MOODLE')
MOODLE_TOKEN = config.get('MOODLE_TOKEN')
MOODLE_URL = config.get('MOODLE_URL')

BASE_URL = 'https://exam.itexpert.ru'

PATH_DIR_BASE = Path(
    '//192.168.20.100/Administrative server/РАБОТА АДМИНИСТРАТОРА/ОРГАНИЗАЦИЯ IT ЭКЗАМЕНОВ/ЭКЗАМЕНЫ ЦИФРОВОЙ ПУТЬ')
PATH_DIR_CERTS = PATH_DIR_BASE / 'сертификат'
PATH_DIR_HTML_DOWNLOAD = PATH_DIR_BASE / 'DOWNLOAD_Moodle'
PATH_DIR_HTML_DOWNLOAD.mkdir(exist_ok=True, parents=True)
PATH_DIR_REPORTS = PATH_DIR_BASE / 'Результаты HTML'
PATH_DIR_REPORTS.mkdir(exist_ok=True, parents=True)
PATH_FILE_QUESTIONS_XLSX = PATH_DIR_BASE / 'questions_xlsx'
PATH_FILE_QUESTIONS_XLSX.mkdir(exist_ok=True, parents=True)

if not LOGIN_MOODLE:
    raise f'ERROR .ENV {MOODLE_TOKEN=}'
if not PASSWORD_MOODLE:
    raise f'ERROR .ENV {MOODLE_URL=}'
if not MOODLE_TOKEN:
    raise f'ERROR .ENV {MOODLE_TOKEN=}'
if not MOODLE_URL:
    raise f'ERROR .ENV {MOODLE_URL=}'
