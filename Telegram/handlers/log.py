import datetime
from pathlib import Path

from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile

from Contact import load_contacts_from_log_file, Contact
from Telegram.Call_Back_Data import CallBackData as call_back
from Telegram.keybords.inline import inline_kb_main
from Telegram.main import dp, bot
from Utils.check_time import check_time_interval
from Utils.log import log
from root_config import USERS_ID, ADMIN_ID, LOG_FILE, TEMPLATE_FILE_XLSX, DOCUMENTS, SYSTEM_LOG


def is_empty_file(file) -> bool:
    file = Path(file)
    if not file.exists():
        return True

    try:
        with open(file=file, mode="r", encoding='utf-8') as f:
            s = f.read()
            return len(s) <= 10
    except UnicodeDecodeError:
        log.error('UnicodeDecodeError')
    return False


@dp.message(Command('id'))
async def send_id(message: types.Message):
    await message.answer(str(message.chat.id))


@dp.callback_query(
    F.data.in_(
        {call_back.GET_LOG, call_back.GET_LOG_PROGRAM, call_back.GET_TEMPLATE_FILE_XLSX, call_back.GET_LAST_EXCEL_FILE})
    & F.from_user.id.in_({*ADMIN_ID, *USERS_ID})
)
async def get_file(callback_query: types.callback_query):
    query = callback_query.data

    if query == call_back.GET_LOG_PROGRAM:
        file = FSInputFile(SYSTEM_LOG, 'systemlog.txt')
    elif query == call_back.GET_LOG:
        file = FSInputFile(LOG_FILE, 'log_file.txt')
    elif query == call_back.GET_TEMPLATE_FILE_XLSX:
        file = FSInputFile(TEMPLATE_FILE_XLSX, 'template_file.xlsx')
    elif query == call_back.GET_LAST_EXCEL_FILE:
        path_dir = Path(DOCUMENTS)

        # 1. Получаем список всех файлов в папке (исключая директории)
        files = [f for f in path_dir.iterdir() if f.is_file()]

        if files:
            # 2. Находим файл с максимальным временем создания
            # f.stat().st_ctime — время создания файла
            last_file = max(files, key=lambda f: f.stat().st_ctime)

            # 3. Создаем FSInputFile. .name заменяет os.path.basename
            file = FSInputFile(last_file, filename=last_file.name)
        else:
            # Обработка ситуации, если файлов в папке нет
            print("Файлы не найдены в директории DOCUMENTS")
            file = None

    try:
        if is_empty_file(file.path):
            await bot.send_message(chat_id=callback_query.from_user.id, text=f'✅ Файл пустой',
                                   reply_markup=inline_kb_main)
        else:
            await bot.send_document(chat_id=callback_query.from_user.id, document=file, reply_markup=inline_kb_main)
    except UnicodeDecodeError:
        log.error('UnicodeDecodeError')


@dp.callback_query(
    F.data.in_({call_back.SHOW_EXAM_TODAY, }) & F.from_user.id.in_({*ADMIN_ID, *USERS_ID})
)
async def show_exam_now(callback_query: types.callback_query):
    'subject=2024-12-25T11:00:00Z_Vitaliy_Stepanov_ITIL4FC_proctor-1'
    try:
        contacts = load_contacts_from_log_file()
        contacts = [c for c in contacts if check_time_interval(check_dt=c.date_exam,
                                                               start_dt=datetime.datetime.now(),
                                                               delta_dt=datetime.timedelta(days=1))]
        c: Contact
        rows = []

        for c in contacts:
            offline = ''
            if c.online in (0, '0', False, None):
                offline = 'offline'

            rows.append(
                f'{c.date_exam.strftime("%H:%M")} {c.exam} {c.email} {c.ru_last_name} {c.ru_first_name} {offline}')

        if rows:
            rows = [f'{i + 1}. {v}' for i, v in enumerate(sorted(rows))]

        text = '\n'.join(rows)
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'Экзамены сегодня:\n{text}',
                               reply_markup=inline_kb_main)
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'Error {e}', reply_markup=inline_kb_main)


@dp.callback_query(
    F.data.in_({call_back.SHOW_ALL_EXAMS, }) & F.from_user.id.in_({*ADMIN_ID, *USERS_ID})
)
async def show_all_exams(callback_query: types.callback_query):
    'subject=2024-12-25T11:00:00Z_Vitaliy_Stepanov_ITIL4FC_proctor-1'
    try:
        contacts = load_contacts_from_log_file()
        contacts = [c for c in contacts if check_time_interval(check_dt=c.date_exam,
                                                               start_dt=datetime.datetime.now(),
                                                               delta_dt=datetime.timedelta(days=60))]
        c: Contact
        rows = []
        for c in contacts:
            offline = ''
            if c.online in (0, '0', False, None):
                offline = 'offline'
            rows.append(
                f'{c.date_exam.strftime("%Y.%m.%d %H:%M")} {c.exam} {c.email} {c.ru_last_name} {c.ru_first_name} {offline}')

        if rows:
            rows = [f'{i + 1}. {v}' for i, v in enumerate(sorted(rows))]

        text = '\n'.join(rows)

        await bot.send_message(chat_id=callback_query.from_user.id, text=f'Экзамены:\n{text}',
                               reply_markup=inline_kb_main)
    except Exception as e:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'Error {e}', reply_markup=inline_kb_main)
