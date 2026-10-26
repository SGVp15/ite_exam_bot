from pathlib import Path

from dotenv import dotenv_values, find_dotenv

VERSION = '1.8.1'

config = dotenv_values(find_dotenv())

BOT_TOKEN: str | None = config.get('BOT_TOKEN')
ADMIN_ID: list[int] = [int(x) for x in config['ADMIN_ID'].split(',')]
USERS_ID: list[int] = [int(x) for x in config['USERS_ID'].split(',')]

if not BOT_TOKEN:
    raise f'ERROR .ENV {BOT_TOKEN=}'

dir_data = Path('./data').resolve()
dir_data.mkdir(parents=True, exist_ok=True)

#  ====================================================================================================================
#  -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL

dir_template = dir_data / 'output' / 'template'
dir_template.mkdir(parents=True, exist_ok=True)
TEMPLATE_FILE_XLSX = dir_template / 'template.xlsx'
PAGE_NAME: str = 'Экзамены'

server_dir = Path(
    "//192.168.20.100/Administrative server/РАБОТА АДМИНИСТРАТОРА/ОРГАНИЗАЦИЯ IT ЭКЗАМЕНОВ/ЭКЗАМЕНЫ ЦИФРОВОЙ ПУТЬ/")
TEMPLATE_SERVER_FILE_XLSX = server_dir / "Регистрация_На_Экзамен.xlsx"

#  == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL
#  ====================================================================================================================

LOG_FILE = Path(server_dir / 'log.txt')

PATH_DOWNLOAD_FILE = dir_data / 'input'
DOCUMENTS = PATH_DOWNLOAD_FILE / 'documents'
DOCUMENTS.mkdir(parents=True, exist_ok=True)
SYSTEM_LOG = dir_data / 'systemlog.txt'

FONT_PATH_GEOMETRIA_LIGHT = Path('./data/fonts/Geometria/geometria_light.otf')
FONT_PATH_RUBIK_REGULAR = Path('./data/fonts/Rubik/Rubik-Regular.ttf')

ALLOWED_EXAMS: list = [
    'BAFC',
    'BASRMC',
    'CPIC',
    'Cobit2019C',
    'DGTC',
    'ICSC',
    'ITAMC',
    'ITHRC',
    'ITIL4FC',
    'ITSMC',
    'OPSC',
    'RCVC',
    'RISKC',
    'SCMC',
    'SOAC',
    'SYSAC',
]
