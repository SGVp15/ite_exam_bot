import datetime
import pickle

from Email import EmailSending
from Email.config import EMAIL_BCC
from Email.template import template_email_exam_result_passed
from Itexpert.ite_api import sent_report_and_cert_lk
from My_jinja import MyJinja
from Utils.log import log
from .XLSX.excel import get_contact_from_cert_excel
from .config_cert_exam import PICKLE_USERS, DIR_CERTS, DELTA_DAYS
from .create_png import create_png

time_file_modify = 0


def load_old_users():
    old_users = []
    try:
        old_users = pickle.load(open(PICKLE_USERS, 'rb'))
    except FileNotFoundError as e:
        log.error(e)
    return old_users


def main_create_exam_cert(can_send_email=True):
    # old_users = load_old_users()
    # print(f'old_users: {len(old_users)}\n')
    users_from_cer_excel = get_contact_from_cert_excel()
    print(f'excel_users: {len(users_from_cer_excel)}\n')
    certs_files = [f for f in DIR_CERTS.rglob('*') if f.is_file() and f.suffix == '.png']
    print(f'old_certs_files: {len(certs_files)}\n')
    # new_users = [user for user in users_from_cer_excel if user not in old_users]
    new_users = users_from_cer_excel
    new_users = [u for u in new_users
                 if (datetime.datetime.now() >= u.date_exam + datetime.timedelta(days=DELTA_DAYS)
                     or u.can_create_cert in (1, '1'))]
    new_users = [u for u in new_users if u.file_out_png not in certs_files]

    print(f'new_users: {len(new_users)}\n')

    for contact in new_users:
        contact.file_out_png.parent.mkdir(parents=True, exist_ok=True)

    successful_users = []
    for i, contact in enumerate(new_users):
        try:
            create_png(contact)
            html = MyJinja(template_file=template_email_exam_result_passed).render_document(user=contact)
            if can_send_email:
                EmailSending(
                    to=[contact.email, ],
                    bcc=EMAIL_BCC,
                    subject='Поздравляем с успешной сдачей экзамена!',
                    # text='text',
                    html=html,
                ).send_email()

            log.info(f'[{i + 1}/{len(new_users)}]\t{contact.file_out_png}')
            successful_users.append(contact)
        except FileNotFoundError as e:
            log.error(f'{e} [{i + 1}/{len(new_users)}]\t{contact.file_out_png}')

    if successful_users:
        all_users = [*successful_users, *old_users]
        pickle.dump(all_users, open(PICKLE_USERS, 'wb'))
        log.info('[Create PICKLE_USERS]')
        sent_report_and_cert_lk()


def create_exam_cert(can_send_email=True):
    try:
        main_create_exam_cert(can_send_email)
    except Exception as e:
        log.error(e)
