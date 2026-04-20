from pathlib import Path

BASE_PATH = Path(
    '//192.168.20.100/Administrative server/РАБОТА АДМИНИСТРАТОРА/ОРГАНИЗАЦИЯ IT ЭКЗАМЕНОВ/ЭКЗАМЕНЫ ЦИФРОВОЙ ПУТЬ')

FILE_XLSX = BASE_PATH / 'Нумерация_Экзамены.xlsx'
DIR_CERTS = BASE_PATH / 'сертификат'
TEMPLATE_FOLDER = BASE_PATH / 'template_cert_png'

DIR_CERTS.mkdir(parents=True, exist_ok=True)
TEMPLATE_FOLDER.mkdir(parents=True, exist_ok=True)

LOG_FILE = Path('./log.txt').resolve()
PICKLE_USERS = Path('./users.pk').resolve()

# --- Excel --- Excel --- Excel --- Excel --- Excel --- Excel --- Excel ---
SHEETNAME: str = 'Экзамены'

DELTA_DAYS = 3