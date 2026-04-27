import datetime
from asyncio import sleep

from Contact import Contact, load_contacts_from_log_file
from Email import EmailSending, template_email_registration_exam_offline, template_email_registration_exam_online
from Email.config import EMAIL_BCC
from Itexpert.ite_api import ITEXPERT_API
from Moodle.API.moodleapi import MoodleApi
from My_jinja.my_jinja import MyJinja
from ProctorEDU.gen_link import generate_proctoring_link
from Utils.log import log
from Utils.utils import all_exception
from parser import get_contact_from_excel
from root_config import LOG_FILE, ALLOWED_EXAMS, TEMPLATE_SERVER_FILE_XLSX


def generate_new_proctoring_link_by_contact(contact):
    url = generate_proctoring_link(subject=contact.subject,
                                   nickname=contact.email,
                                   username=contact.username)
    contact.url = url
    return url


@all_exception
async def server_file_registration():
    print(' ---> START [server_file_registration]')
    contacts = get_contact_from_excel(filename=TEMPLATE_SERVER_FILE_XLSX)
    await registration(contacts)


@all_exception
async def registration(contacts: [Contact], send_to_itexpert=True) -> str:
    contacts = contacts[:]
    out_str = ''
    exams = [contact.exam for contact in contacts]
    for exam in exams:
        if exam.lower() not in (item.lower() for item in ALLOWED_EXAMS):
            return 'Проверьте курс'

    contacts_from_log_file = load_contacts_from_log_file(date_start=datetime.datetime.now())
    c: Contact
    new_contacts = [c for c in contacts if c not in contacts_from_log_file and c.date_exam >= datetime.datetime.now()]
    if not new_contacts:
        return 'Проверьте файл. Нет новых пользователей.'

    await sleep(0.1)
    # -------------- Moodle --------------
    moodle_api = MoodleApi()
    for contact in new_contacts:
        moodle_api.process_user_and_enrollment(contact=contact)

    await sleep(0.1)
    # -------------- ProctorEDU --------------
    contacts_proctoring = [c for c in new_contacts if c.online]
    if contacts_proctoring:
        for contact in contacts_proctoring:
            if contact.online:
                contact.url = ''
                generate_new_proctoring_link_by_contact(contact)

    await sleep(0.1)
    # -------------- SEND EMAIL --------------
    log.info(f'[ start ] SEND EMAIL ')
    for contact in new_contacts:
        if contact.online:
            log.info(f'MyJinja start template_email_registration_exam_online')
            text = MyJinja(template_file=template_email_registration_exam_online).render_document(user=contact)
        else:
            log.info(f'MyJinja start template_email_registration_exam_online')
            text = MyJinja(template_file=template_email_registration_exam_offline).render_document(user=contact)
        subject = f'Вы зарегистрированы на экзамен {contact.exam} {contact.date_exam}'
        if contact.online and not contact.url:
            out_str += f'[Error] URL {contact}\n'
            log.error(f'[Error] URL {contact}')
            continue
        EmailSending(subject=subject, to=contact.email, cc=contact.email_cc, bcc=EMAIL_BCC, text=text).send_email()
        contact.status = 'Ok'
    log.info(f'[ end ] SEND EMAIL ')
    # Write Log
    with open(LOG_FILE, mode='a', encoding='utf-8') as f:
        for contact in contacts:
            f.write(str(contact))
            log.info(contact)

    # ITEXPERT
    if send_to_itexpert:
        ite_api = ITEXPERT_API()
        for contact in new_contacts:
            ite_api.create_exam(contact)

    # OUT STRING
    for contact in contacts:
        out_str += (f'{contact.ru_last_name} {contact.ru_first_name} '
                    f'{contact.email} {contact.exam} {contact.date_exam}\n')
    return out_str


async def send_new_link_proctoredu(contacts: [Contact]) -> str:
    return await registration(contacts, send_to_itexpert=False)
