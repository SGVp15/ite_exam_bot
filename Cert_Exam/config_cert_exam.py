from pathlib import Path

base_path = Path(
    '//192.168.20.100/Administrative server/РАБОТА АДМИНИСТРАТОРА/ОРГАНИЗАЦИЯ IT ЭКЗАМЕНОВ/ЭКЗАМЕНЫ ЦИФРОВОЙ ПУТЬ')

PATH_FILE_CERT_XLSX = base_path / 'Нумерация_Экзамены.xlsx'
DIR_CERTS = base_path / 'сертификат'
TEMPLATE_FOLDER = base_path / 'template_cert_png'

DIR_CERTS.mkdir(parents=True, exist_ok=True)
TEMPLATE_FOLDER.mkdir(parents=True, exist_ok=True)

LOG_FILE = Path('./log.txt').resolve()
PICKLE_USERS = Path('./users.pk').resolve()

# --- Excel --- Excel --- Excel --- Excel --- Excel --- Excel --- Excel ---
SHEETNAME: str = 'Экзамены'

DELTA_DAYS = 3