import datetime
import random
import re

import dateparser

from Utils.log import log
from Utils.translit import transliterate, replace_ru_char_to_eng_char
from Utils.utils import to_md5, clean_string
from root_config import LOG_FILE


class Contact:
    def __init__(self):
        self.name_eng: str | None = None
        self.ru_last_name: str | None = None
        self.ru_first_name: str | None = None
        self.eng_last_name: str | None = None
        self.eng_first_name: str | None = None
        self.email: str | None = None
        self.email_cc: list = []
        self.username: str | None = None
        self.password: str | None = None
        self.exam: str | None = None

        self.pattern_time = "%Y-%m-%dT%H:%M:%SZ"
        self.date_exam: datetime.datetime | None = None
        self.date_exam_connect: datetime.datetime | None = None
        self.open_at: str | None = None
        self.close_at: str | None = None
        self.remove_at: str | None = None
        self.deadline: str | None = None
        self.scheduled_at: str | None = None
        self.online: str | None = None
        self.subject: str | None = None
        self.url: str | None = None

        self.identifier: str | None = None
        self.status = 'Error'

        self.moodle_id_exam = None
        self.moodle_id_user = None

    def parser_str_to_contact(s: str):
        """
        Парсит строку лога прокторинга, извлекая статус, дату/время и все пары ключ=значение.

        :param s: Строка для парсинга.
        :return: Словарь с извлеченными данными.
        """
        result = {}
        if not s:
            return {}

        # Разделяем строку, которая содержит только пары 'ключ=значение',
        # но только по пробелам, чтобы не испортить URL.
        key_value_pairs = s.split('\t')

        for item in key_value_pairs:
            if '=' in item:
                try:
                    key, value = item.split('=', 1)
                    result[key.strip()] = value.strip()
                except ValueError:
                    continue

        if result.get('status', '').lower() != 'ok':
            return {}

        contact = Contact()
        attributes = contact.__dict__
        for attr_name in attributes:
            if attr_name in result.keys():
                if 'date' in attr_name:
                    v = result.get(attr_name, '')
                    d = dateparser.parse(v)
                    setattr(contact, attr_name, dateparser.parse(result.get(attr_name, '')))
                    continue
                setattr(contact, attr_name, result.get(attr_name, ''))
        try:
            if not contact.url:
                contact.url = result.get('url', '')
            if not contact.exam:
                contact.exam = re.findall(r'_([A-Z0-9]+)_', contact.subject)[0]
        except IndexError:
            pass
        return contact

    def normalize(self) -> bool:
        self.ru_first_name = clean_string(self.ru_first_name).capitalize()
        self.eng_last_name = clean_string(self.eng_last_name).capitalize()
        self.eng_first_name = clean_string(self.eng_first_name).capitalize()
        self.email = replace_ru_char_to_eng_char(clean_string(self.email).lower())

        if not self.eng_first_name:
            self.eng_first_name = transliterate(f'{self.ru_first_name}').capitalize()
        else:
            self.eng_first_name = replace_ru_char_to_eng_char(self.eng_first_name)

        if not self.eng_last_name:
            self.eng_last_name = transliterate(f'{self.ru_last_name}').capitalize()
        else:
            self.eng_last_name = replace_ru_char_to_eng_char(self.eng_last_name)

        self.email = replace_ru_char_to_eng_char(self.email.strip())

        self.name_eng = f'{self.eng_first_name} {self.eng_last_name}'

        if not self.date_exam_connect:
            self.date_exam_connect = self.date_exam + datetime.timedelta(minutes=-5)
        if not self.scheduled_at:
            self.scheduled_at = self.date_exam + datetime.timedelta(hours=-3)
        else:
            self.scheduled_at = dateparser.parse(self.scheduled_at)
        deadline = self.scheduled_at + datetime.timedelta(hours=2)
        remove_at = self.scheduled_at + datetime.timedelta(days=90)
        open_at = self.scheduled_at - datetime.timedelta(minutes=20)
        close_at = self.scheduled_at + datetime.timedelta(hours=2, minutes=20)

        self.deadline = deadline.strftime(self.pattern_time)
        self.open_at = open_at.strftime(self.pattern_time)
        self.close_at = close_at.strftime(self.pattern_time)
        self.remove_at = remove_at.strftime(self.pattern_time)

        self.username = re.sub(r'\s+', '_', self.name_eng.strip().lower())

        if not self.password:
            self.password = f'{self.username}_P{random.randint(1000, 9999):04d}'

        self.subject = f'{self.date_exam.strftime(self.pattern_time)}_{self.username}_' \
                       f'{self.exam}_online-{self.online}'

        self.identifier = to_md5(f'{self.date_exam.strftime(self.pattern_time)}_{self.username}_{self.exam}')
        return True

    def __str__(self) -> str:
        return (
            f"status={self.status}\t"
            f"timestamp={datetime.datetime.now().strftime("%Y-%m-%d T%H:%M:%S")}\t"
            f"subject={self.subject}\t"
            f"name_eng={self.name_eng}\t"
            f"ru_last_name={self.ru_last_name}\t"
            f"ru_first_name={self.ru_first_name}\t"
            f"eng_last_name={self.eng_last_name}\t"
            f"eng_first_name={self.eng_first_name}\t"
            f"email={self.email}\t"
            f"username={self.username}\t"
            f"password={self.password}\t"
            f"exam={self.exam}\t"
            f"online={self.online}\t"
            f"url={self.url}\t"
            f"date_exam={self.date_exam}\t"
            f"date_exam_connect={self.date_exam_connect}\t"
            f"scheduled_at={self.scheduled_at}\t"
            f"open_at={self.open_at}\t"
            f"close_at={self.close_at}\t"
            f"deadline={self.deadline}\t"
            f"remove_at={self.remove_at}\t"
            f"identifier={self.identifier}\t"
            f"email_cc={self.email_cc}\t"
            f"moodle_id_exam={self.moodle_id_exam}\t"
            f"moodle_id_user={self.moodle_id_user}\n"
        )

    def __eq__(self, other):
        try:
            if self.email == other.email:
                if self.exam == other.exam:
                    if self.date_exam == other.date_exam:
                        return True
        except AttributeError:
            pass
        return False


def load_contacts_from_log_file(
        file=LOG_FILE,
        date_start: datetime.datetime | None = None,
        date_end: datetime.datetime | None = None,
) -> [Contact]:
    contacts = []
    s = ''

    try:
        with open(file, 'r', encoding='utf-8') as f:
            s = f.read()
    except Exception as e:
        log.error(e)

    if not s:
        return contacts

    for row in s.split('\n'):
        if not row.strip():
            continue

        c = Contact.parser_str_to_contact(row)
        if not c or not c.date_exam:
            continue

        # Логика фильтрации по диапазону
        # Извлекаем только дату для сравнения (без времени), если это необходимо
        current_date = c.date_exam.date()

        is_after_start = True
        if date_start:
            is_after_start = current_date >= date_start.date()

        is_before_end = True
        if date_end:
            is_before_end = current_date <= date_end.date()

        if is_after_start and is_before_end:
            if c not in contacts:
                contacts.append(c)

    return contacts
