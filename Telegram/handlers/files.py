import asyncio
from pathlib import Path

from aiogram import types, F
from aiogram.types import FSInputFile

from Cert_Exam.main_cert_exam import main_create_exam_cert
from Telegram.Call_Back_Data import CallBackData
from Telegram.keybords.inline import inline_kb_main, get_list_files_keyboard
from Telegram.main import dp, bot
from Utils.log import log
from root_config import USERS_ID, ADMIN_ID, PATH_DIR_DOWNLOAD_FILES_TELEGRAM


def is_empty_file(file_path) -> bool:
    with open(file=file_path, mode="r", encoding='utf-8') as f:
        s = f.read()
    return len(s) <= 10


async def background_worker(user_id: int, status_msg: types.Message):
    """
    Эта функция работает отдельно от основного потока бота.
    Она выполняет тяжелую задачу и сама присылает результат.
    """
    try:
        # Запускаем тяжелую синхронную функцию в отдельном потоке.
        # Это не дает боту "зависнуть" для других пользователей.
        # Если в функцию нужно передать аргументы: asyncio.to_thread(func, arg1, arg2)
        await asyncio.to_thread(main_create_exam_cert)

        # Когда сертификаты готовы, редактируем старое сообщение или шлем новое
        await bot.send_message(
            chat_id=user_id,
            text='✅ Сертификаты созданы и готовы к выдаче!',
            reply_markup=inline_kb_main,
        )

        # Удаляем временное сообщение "⏳ Создаю..."
        await status_msg.delete()

    except Exception as e:
        log.error(f"Ошибка в воркере: {e}")
        await bot.send_message(chat_id=user_id, text=f"❌ Произошла ошибка: {e}")


@dp.callback_query(
    F.data.startswith(CallBackData.FILE_DOWNLOAD_) & F.from_user.id.in_({*ADMIN_ID, *USERS_ID})
)
async def download_file(callback_query: types.callback_query):
    query = callback_query.data
    file_name = str(query).replace(CallBackData.FILE_DOWNLOAD_, '')
    path = Path(PATH_DIR_DOWNLOAD_FILES_TELEGRAM) / file_name
    if path.exists():
        file = FSInputFile(path, file_name)
        await bot.send_document(chat_id=callback_query.from_user.id, document=file, reply_markup=inline_kb_main)
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text='Файла не существует',
                               reply_markup=get_list_files_keyboard())


@dp.callback_query(
    F.data.startswith(CallBackData.CREATE_CERT) & F.from_user.id.in_({*ADMIN_ID,})
)
async def create_cert(callback_query: types.CallbackQuery):
    # 1. Отвечаем Телеграму сразу (убирает крутилку на кнопке)
    await callback_query.answer()

    # 2. Отправляем уведомление, что процесс пошел
    status_msg = await callback_query.message.answer(
        "⏳ Запущена генерация сертификатов...\n"
        "Вы можете пользоваться другими функциями бота, я напишу по готовности. \n"
        "/help"
    )

    # 3. Самое важное: Запускаем задачу "в воздух" через create_task.
    # Хендлер тут же завершается, а background_worker продолжает шуршать.
    asyncio.create_task(background_worker(callback_query.from_user.id, status_msg))


async def run_background_cert_creation(user_id: int, status_msg: types.Message):
    try:

        await main_create_exam_cert()

        # 4. Уведомляем об успехе
        await status_msg.edit_text(
            text='✅ Все сертификаты созданы!',
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Произошла ошибка при создании: {e}")



@dp.callback_query(
    F.data.startswith(CallBackData.FILE_DELETE_) & F.from_user.id.in_({*ADMIN_ID, *USERS_ID})
)
async def delete_file(callback_query: types.callback_query):
    query = callback_query.data
    file_name = str(query).replace(CallBackData.FILE_DELETE_, '')
    path = Path(PATH_DIR_DOWNLOAD_FILES_TELEGRAM) / file_name
    if path.exists():
        path.unlink(missing_ok=True)
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'Файл {file_name} удален',
                               reply_markup=get_list_files_keyboard())
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'Файл {file_name} не существует',
                               reply_markup=get_list_files_keyboard())


@dp.callback_query(F.data.in_({CallBackData.SHOW_LIST_FILE}) & F.from_user.id.in_({*ADMIN_ID, *USERS_ID}))
async def show_list_files(callback_query: types.callback_query):
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text='Список файлов',
        reply_markup=get_list_files_keyboard()
    )
