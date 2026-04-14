from pathlib import Path

from dotenv import dotenv_values, find_dotenv

VERSION = '1.5.1'

config = dotenv_values(find_dotenv())

BOT_TOKEN: str | None = config.get('BOT_TOKEN')
ADMIN_ID: list[int] = [int(x) for x in config['ADMIN_ID'].split(',')]
USERS_ID: list[int] = [int(x) for x in config['USERS_ID'].split(',')]

if not BOT_TOKEN:
    raise f'ERROR .ENV {BOT_TOKEN=}'

DIR_DATA = Path('./data').resolve()
DIR_DATA.mkdir(parents=True, exist_ok=True)
LOG_FILE = Path(DIR_DATA / 'log.txt')

#  ====================================================================================================================
#  -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL -- EXCEL

DIR_template = DIR_DATA / 'output' / 'template'
DIR_template.mkdir(parents=True, exist_ok=True)
TEMPLATE_FILE_XLSX = DIR_template / 'template.xlsx'
PAGE_NAME: str = 'Экзамены'

TEMPLATE_SERVER_FILE_XLSX = "//192.168.20.100/Administrative server/РАБОТА АДМИНИСТРАТОРА/ОРГАНИЗАЦИЯ IT ЭКЗАМЕНОВ/ЭКЗАМЕНЫ ЦИФРОВОЙ ПУТЬ/Регистрация_На_Экзамен.xlsx"

# LastName_column: str = 'A'
# FirstName_column: str = 'B'
# LastNameEng_column: str = 'C'
# FirstNameEng_column: str = 'D'
# Email_column: str = 'E'
# Password_column: str = 'F'
# Exam_column: str = 'G'
# Date_column: str = 'H'
# Hour_column: str = 'I'
# Minute_column: str = 'J'
# Online_column: str = 'K'
# Certificate_insurance_column: str = 'L'

#  == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL == EXCEL
#  ====================================================================================================================

PATH_DOWNLOAD_FILE = DIR_DATA / 'input'
DOCUMENTS = PATH_DOWNLOAD_FILE / 'documents'
DOCUMENTS.mkdir(parents=True, exist_ok=True)
SYSTEM_LOG = DIR_DATA / 'systemlog.txt'

ALLOWED_EXAMS: list = [
    'BAFC',
    'BASRMC',
    'CPIC',
    'Cobit2019C',
    'ICSC',
    'ITAMC',
    'ITHRC',
    'ITIL4FC',
    'OPSC',
    'RCVC',
    'RISKC',
    'SCMC',
    'SOAC',
    'SYSAC',
    'ITSMC',
]
