import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from root_config import DOCUMENTS
from Telegram.Call_Back_Data import CallBackData

inline_btn_logs = InlineKeyboardButton(text='Скачать Логи', callback_data=CallBackData.DOWNLOAD_LOGS)


def del_enrollment(enrollment_id: str):
    inline_kb_del = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🗑 Delete', callback_data=f'{CallBackData.DEL_REGISTRATION}{enrollment_id}'), ],
    ])
    return inline_kb_del


def button_return_main_menu():
    return [InlineKeyboardButton(text='🔙 Назад', callback_data=CallBackData.BACK_TO_MAIN), ]


inline_kb_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📅 Покажи экзамены сегодня?', callback_data=CallBackData.SHOW_EXAM_TODAY)],
    [InlineKeyboardButton(text='📅 Покажи Все Экзамены', callback_data=CallBackData.SHOW_ALL_EXAMS)],
    [InlineKeyboardButton(text='📊 Скачать Шаблон Excel', callback_data=CallBackData.GET_TEMPLATE_FILE_XLSX)],
    [InlineKeyboardButton(text='📑 Скачать Логи 📑', callback_data=CallBackData.GET_LOG)],
    [InlineKeyboardButton(text='📩 Вышли новую ссылку proctorEdu', callback_data=CallBackData.SEND_NEW_LINK_PROCTOREDU)],
    [InlineKeyboardButton(text='📂 Покажи входящие файлы 📂', callback_data=CallBackData.SHOW_LIST_FILE)],
    [InlineKeyboardButton(text='🚀 Отправить в ЛК отчеты и сертификаты 🎓',
                          callback_data=CallBackData.SENT_REPORT_AND_CERT_LK)],
    [InlineKeyboardButton(text='⚙️ Admin Menu >>', callback_data=CallBackData.ADMIN_MENU)],
])

k_admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='? Версия бота?', callback_data=CallBackData.SHOW_VERSION)],
    [InlineKeyboardButton(text='📄 Скачать Логи Программные 📄', callback_data=CallBackData.GET_LOG_PROGRAM), ],
    [InlineKeyboardButton(text='🆕 Создай сертификаты 🆕', callback_data=CallBackData.CREATE_CERT), ],
    [InlineKeyboardButton(text='🆕 Создай отчеты 🆕', callback_data=CallBackData.CREATE_REPORT), ],
    [InlineKeyboardButton(text='⏬ Скачай отчеты moodle и создай отчеты \n(без загрузки)⏬',
                          callback_data=CallBackData.DOWNLOAD_REPORT_MOODLE_AND_CREATE_FOR_LK)],
    button_return_main_menu(),
])


def get_list_files_keyboard(path=DOCUMENTS) -> [InlineKeyboardButton]:
    out_buttons = []
    files = os.listdir(path)
    for file in files:
        out_buttons.append(
            [
                InlineKeyboardButton(text=f'⏬ {file}', callback_data=f'{CallBackData.FILE_DOWNLOAD_}{file}'),
                InlineKeyboardButton(text=f'🗑 {file}', callback_data=f'{CallBackData.FILE_DELETE_}{file}'),
            ]
        )
    out_buttons.append(button_return_main_menu())
    return InlineKeyboardMarkup(inline_keyboard=[*out_buttons])
