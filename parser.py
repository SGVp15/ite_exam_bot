import re
import xml.etree.ElementTree as ET

import dateparser

from Contact import Contact
from EXCEL.my_excel import read_excel_file
from root_config import TEMPLATE_FILE_XLSX, PAGE_NAME


def get_all_courses(xml: str) -> dict:
    root = ET.fromstring(xml)
    courses: dict = {}
    list_courses = []
    for i, group1 in enumerate(root.findall('contentItem')):
        _ = group1.find('contentItemId').text
        list_courses.append({group1.find('title').text: group1.find('contentItemId').text})
    for course_dict in list_courses:
        course_name = list(course_dict.keys())[0]
        if course_name in list(courses.keys()):
            courses[course_name].append(course_dict[course_name])
        else:
            courses[course_name] = [course_dict[course_name]]

    return courses


def get_all_users(xml: str) -> list[dict]:
    root = ET.fromstring(xml)
    users: list[dict] = []
    for i, group1 in enumerate(root.findall('userProfile')):
        users.append({'userId': group1.find('userId').text})
        for group2 in group1.findall('fields'):
            for group3 in group2.findall('field'):
                users[i].update({group3.find('name').text: group3.find('value').text})
    return users


def get_contact_from_array(data_list) -> list[Contact]:
    contacts = []
    for data in data_list:
        # 'Дата экзамена', 'Экзамен', 'Фамилия рус', 'Имя рус', 'Фамилия англ', 'Имя анг', 'Email', 'Password', 'Часы', 'Минуты', 'Online', 'Страховой сертификат', 'Копия письма'
        # 'exam_date', 'exam', 'last_name_rus', 'first_name_rus', 'last_name_eng', 'first_name_eng', 'email', 'password', 'hours', 'minutes', 'online', 'insurance_certificate', 'copy_email'

        if not data[0]:
            continue
        if len(data) < 13:
            continue
        (exam_date, exam, last_name_rus, first_name_rus, last_name_eng, first_name_eng,
         email, password, hours, minutes, online, insurance_certificate, copy_email) = data[:13]
        if '@' not in email or not exam or not exam_date:
            continue

        contact = Contact()
        contact.ru_last_name = last_name_rus
        contact.ru_first_name = first_name_rus
        contact.eng_last_name = last_name_eng
        contact.eng_first_name = first_name_eng
        contact.email = email
        contact.password = password
        contact.exam = exam
        contact.online = online
        contact.date_exam = dateparser.parse(
            f'{exam_date.strip()} {str(hours).strip()}:{str(minutes).strip()}',
            settings={'DATE_ORDER': 'DMY'}
        )
        if copy_email:
            copy_email = re.sub(r'[\s,;|]+', ' ', copy_email).strip()
            row = list(set(str(copy_email).strip().split(' ')))
            contact.email_cc = [w for w in row if '@' in w]
        if contact.normalize():
            contacts.append(contact)
    return contacts


def get_contact_from_excel(filename=TEMPLATE_FILE_XLSX):
    sheet_data: dict = read_excel_file(filename=filename, sheet_names=(PAGE_NAME,))
    sheet_data = sheet_data.get(PAGE_NAME)

    contacts: list[Contact] = get_contact_from_array(sheet_data)
    if not contacts:
        return None
    return contacts
