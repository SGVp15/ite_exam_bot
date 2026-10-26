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
PATH_FILE_TEMPLATE_REGISTRATION_ON_EXAM_XLSX = dir_template / 'template.xlsx'

PAGE_NAME: str = 'Экзамены'

server_dir = (Path('//192.168.20.100')
              / 'Administrative server'
              / 'РАБОТА АДМИНИСТРАТОРА'
              / 'ОРГАНИЗАЦИЯ IT ЭКЗАМЕНОВ'
              / 'ЭКЗАМЕНЫ ЦИФРОВОЙ ПУТЬ')
PATH_FILE_REGISTRATION_ON_EXAM_XLSX = server_dir / 'Регистрация_На_Экзамен.xlsx'

#  == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL
#  ====================================================================================================================

LOG_FILE = Path(server_dir) / 'log.txt'

PATH_DIR_DOWNLOAD_FILES_INPUT = dir_data / 'input'
PATH_DIR_DOWNLOAD_FILES_TELEGRAM = PATH_DIR_DOWNLOAD_FILES_INPUT / 'documents'
PATH_DIR_DOWNLOAD_FILES_TELEGRAM.mkdir(parents=True, exist_ok=True)
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

paths = [
    PATH_FILE_TEMPLATE_REGISTRATION_ON_EXAM_XLSX,
    PATH_FILE_REGISTRATION_ON_EXAM_XLSX,
    PATH_DIR_DOWNLOAD_FILES_INPUT,
    PATH_DIR_DOWNLOAD_FILES_TELEGRAM,
    FONT_PATH_GEOMETRIA_LIGHT,
    FONT_PATH_RUBIK_REGULAR,
]

def is_exist_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f'Путь не существует: {path}')

    try:
        if path.is_dir():
            next(path.iterdir(), None)
        else:
            with path.open('rb'):
                pass
    except OSError as e:
        raise PermissionError(f'Путь недоступен для чтения: {path}') from e


for path in paths:
    is_exist_path(path)
