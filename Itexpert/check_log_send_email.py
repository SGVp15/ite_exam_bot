import datetime
from asyncio import sleep

from Contact import Contact
from Email import EmailSending
from Email.config import EMAIL_LOGIN, SMTP_SERVER, SMTP_PORT, EMAIL_PASSWORD, EMAIL_BCC
from Utils.check_time import check_time_interval
from root_config import LOG_FILE


def get_contacts_from_logs() -> [Contact]:
    rows = ''
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            rows = f.read()
    except Exception as e:
        print(e)
    contacts = []
    for row in rows.split('\n'):
        c = Contact.parser_str_to_contact(row)
        if c:
            contacts.append(c)
    return contacts


async def check_log_and_send_email_to_manager():
    contact_for_email_ = []
    contacts = get_contacts_from_logs()
    for c in contacts:
        c: Contact
        if check_time_interval(
                check_dt=datetime.datetime.now().time(),
                start_dt=datetime.time(hour=9, minute=0),
                delta_dt=datetime.timedelta(minutes=1)):
            # if datetime.time(hour=9, minute=0) <= datetime.datetime.now().time() <= datetime.time(hour=9, minute=1,
            #                                                                                       second=0):
            if datetime.datetime.now().date() == c.date_exam.date():
                contact_for_email_.append(c)
                continue
        try:
            if check_time_interval(
                    check_dt=datetime.datetime.now(),
                    start_dt=c.date_exam - datetime.timedelta(hours=1),
                    delta_dt=datetime.timedelta(minutes=1)
            ):
                contact_for_email_.append(c)
        except TypeError:
            pass

    subject = 'Экзамен '
    if contact_for_email_:
        text = ''
        for c in contact_for_email_:
            if c.online:
                text += 'Online '
            else:
                text += 'Offline '
            text += (
                f'{c.date_exam.strftime(c.pattern_time)}\n'
                f'{c.exam}\n'
                f'{c.ru_last_name} {c.ru_first_name} {c.email}\n'
                f'Логин={c.username}\n'
                f'Пароль={c.password}\n'
                f'url={c.url_proctor}\n'
                f'\n{"-" * 30}\n'
            )
            subject += f'{c.exam} {c.date_exam} '

        email = EmailSending(
            subject=f'{subject}', from_email=EMAIL_LOGIN, to=EMAIL_BCC, cc='', bcc='',
            text=text, html='', smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT,
            login=EMAIL_LOGIN, password=EMAIL_PASSWORD, manager=None)
        email.send_email()


if __name__ == '__main__':
    contacts = get_contacts_from_logs()
    # 1. Создание интервала
    start_time = datetime.datetime(2025, 12, 1, 16, 30, 0)
    # Продолжительность: 1 час 30 минут
    interval_duration = datetime.timedelta(hours=1, minutes=30)

    # 2. Время для проверки
    # Время внутри интервала (10:00:00 + 01:30:00 = 11:30:00)
    time_to_check_in = datetime.datetime(2025, 12, 1, 16, 0, 0)
    # Время вне интервала
    time_to_check_out = datetime.datetime(2025, 12, 1, 17, 0, 0)

    # 3. Тестирование
    print(f"Интервал: {start_time} — {start_time + interval_duration}")
    print("-" * 40)
    print(f"Проверка {time_to_check_in}: {check_time_interval(time_to_check_in, start_time, interval_duration)}")
    print(f"Проверка {time_to_check_out}: {check_time_interval(time_to_check_out, start_time, interval_duration)}")
