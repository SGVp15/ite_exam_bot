import datetime
from pathlib import Path

from aiogram import types, F
from aiogram.types import message

from Contact import load_contacts_from_log_file
from Itexpert.ite_api import sent_report_and_cert_lk
from Moodle.main import download_reports_moodle
from Moodle.parser_html import create_all_report
from Telegram.Call_Back_Data import CallBackData
from Telegram.keybords.inline import inline_kb_main
from Telegram.main import bot, dp
from Utils.log import log
from main_registration import registration, send_new_link_proctoredu
from parser import get_contact_from_excel
from root_config import USERS_ID, ADMIN_ID, PATH_DOWNLOAD_FILE, LOG_FILE


@dp.message(F.document & F.from_user.id.in_({*ADMIN_ID, *USERS_ID}))
async def download_document_handle(message: message):
    # Get the file ID from the document object
    file_id = message.document.file_id
    # Download the file
    file = await bot.get_file(file_id)
    print(type(file))

    file_path = file.file_path
    path = Path(PATH_DOWNLOAD_FILE) / file_path

    # Read the contents of the file
    await bot.download_file(file_path, destination=path)
    await message.answer('Добавил файл', reply_markup=inline_kb_main)
    log.info(f'ADD FILE {path} {message.message_id=} {message.chat=}')

    contacts_from_file = get_contact_from_excel(path)
    contacts_from_log = load_contacts_from_log_file(LOG_FILE)
    contacts = [c for c in contacts_from_file if c not in contacts_from_log]

    if not contacts:
        text_answer = 'No contact'
        await message.answer(text_answer, reply_markup=inline_kb_main)
    else:
        text_answer = await registration(contacts)
        await message.answer(text_answer, reply_markup=inline_kb_main)
        # asyncio.create_task(registration(contacts))


@dp.callback_query(F.data.in_({CallBackData.DOWNLOAD_REPORT_MOODLE_AND_CREATE_FOR_LK}))
async def btn_download_reports_moodle(callback_query: types.callback_query):
    await download_reports_moodle()
    await create_all_report()
    await bot.send_message(text='DOWNLOAD_REPORT_MOODLE_AND_CREATE_FOR_LK end', chat_id=callback_query.from_user.id,
                           reply_markup=inline_kb_main)

@dp.callback_query(F.data.in_({CallBackData.CREATE_REPORT}))
async def btn_create_report(callback_query: types.callback_query):
    await create_all_report()
    await bot.send_message(text='DOWNLOAD_REPORT_MOODLE_AND_CREATE_FOR_LK end', chat_id=callback_query.from_user.id,
                           reply_markup=inline_kb_main)



@dp.callback_query(F.data.in_({CallBackData.SENT_REPORT_AND_CERT_LK}))
async def btn_sent_report_and_cert_lk(callback_query: types.callback_query):
    text = await sent_report_and_cert_lk(date=datetime.datetime.now())
    await bot.send_message(text=text, chat_id=callback_query.from_user.id,
                           reply_markup=inline_kb_main)


@dp.callback_query(F.data.in_({CallBackData.SEND_NEW_LINK_PROCTOREDU}))
async def btn_send_new_link_proctoredu(callback_query: types.callback_query):
    text = await send_new_link_proctoredu()
    await bot.send_message(text=text, chat_id=callback_query.from_user.id,
                           reply_markup=inline_kb_main)

# @dp.callback_query(F.data.in_({CallBackData.EDIT_REGISTRATION}) & F.from_user.id.in_({*ADMIN_ID, *USERS_ID}))
# async def show_registration(callback_query: CallbackQuery):
#     sessions = get_session_in_enrollments_users_contents()
#     sessions = sorted(sessions)
#     for session in sessions:
#         await bot.send_message(
#             chat_id=callback_query.from_user.id,
#             text=f'{session}',
#             reply_markup=del_enrollment(session.enrollment_id),
#         )
#
#     await bot.send_message(
#         chat_id=callback_query.from_user.id,
#         text=f'End',
#         reply_markup=inline_kb_main
#     )


# @dp.callback_query(F.data.in_({CallBackData.SHOW_REGISTRATION}) & F.from_user.id.in_({*ADMIN_ID, *USERS_ID}))
# async def show_registration(callback_query: CallbackQuery):
#     sessions = get_session_in_enrollments_users_contents()
#     sessions = sorted(sessions)
#     text = 'Ругистрация Ispring:\n'
#     if sessions:
#         for session in sessions:
#             text += f'{session}\n'
#     else:
#         text += 'Никого нет.'
#
#     await bot.send_message(
#         chat_id=callback_query.from_user.id,
#         text=text,
#         reply_markup=inline_kb_main
#     )


# @dp.callback_query(
#     F.data.regexp(f'{CallBackData.DEL_REGISTRATION}' + r'.*')
#     & F.from_user.id.in_({*ADMIN_ID, *USERS_ID}))
# async def del_registration(callback_query: CallbackQuery):
#     delete_id = callback_query.data.replace(CallBackData.DEL_REGISTRATION, '')
#     log.info(f'{delete_id=}')
#     if IspringApi().delete_enrollment(delete_id):
#         text = 'Сессия удалена'
#     else:
#         text = 'Не получилось удалить сессию'
#     await bot.send_message(
#         chat_id=callback_query.from_user.id,
#         text=text,
#         reply_markup=inline_kb_main
#     )
