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
        contact = Contact()

        # LastName_column: str = 'A'	0
        # FirstName_column: str = 'B'	1
        # LastNameEng_column: str = 'C'	2
        # FirstNameEng_column: str = 'D'	3
        # Email_column: str = 'E'	4
        # Password_column: str = 'F'	5
        # Exam_column: str = 'G'	6
        # Date_column: str = 'H'	7
        # Hour_column: str = 'I'	8
        # Minute_column: str = 'J'	9
        # Online_column: str = 'K'	10
        # Cert_save: str = 'L'	11
        # Email_CC_column: str = 'M'	12

        if not data[0]:
            continue
        contact.ru_last_name = data[0]
        contact.ru_first_name = data[1]
        contact.eng_last_name = data[2]
        contact.eng_first_name = data[3]

        contact.email = data[4]
        if '@' not in contact.email:
            continue

        contact.password = data[5]

        contact.exam = data[6]
        if not contact.exam:
            continue

        contact.online = data[10]
        contact.date_exam = dateparser.parse(
            f'{data[7].strip()} {str(data[8]).strip()}:{str(data[9]).strip()}',
            settings={'DATE_ORDER': 'DMY'}
        )
        if data[12]:
            row = str(data[12]).strip().split(' ')
            contact.email_cc = [w for w in row if '@' in w]
        if contact.normalize():
            contacts.append(contact)
    return contacts


def get_contact_from_excel(filename=TEMPLATE_FILE_XLSX):
    sheet_data: dict = read_excel_file(filename=filename, sheet_names=(PAGE_NAME,))
    sheet_data = sheet_data.get(PAGE_NAME)

    contacts: list[Contact] = get_contact_from_array(sheet_data[1:])
    if not contacts:
        return None
    return contacts
