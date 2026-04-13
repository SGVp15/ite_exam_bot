import re

import dateparser
from ..CertContact import CertContact
from ..UTILS.log import log
from ..XLSX.my_excel import read_excel_file
from ..config_cert_exam import FILE_XLSX, SHEETNAME


def get_contact_from_cert_excel(filename=FILE_XLSX) -> list[CertContact]:
    data = read_excel_file(filename)
    rows = data.get(SHEETNAME, [])

    cert_contacts = []
    date_settings = {'DATE_ORDER': 'DMY'}

    for row in rows:
        if not row or len(row) < 9:
            continue
        clean_row = [clean_export_excel(str(item)) for item in row]

        try:
            cert_contact = CertContact()

            (num,
             date,
             abr_exam,
             ru_last_name,
             ru_first_name,
             eng_last_name,
             eng_first_name,
             email,
             can_create_cert,
             exam_ru,) = clean_row[:10]

            cert_contact.number = int(num)
            cert_contact.date_exam = dateparser.parse(date, settings=date_settings)

            if not cert_contact.date_exam:
                continue

            cert_contact.abr_exam = abr_exam
            cert_contact.ru_last_name = ru_last_name
            cert_contact.ru_first_name = ru_first_name
            cert_contact.eng_last_name = eng_last_name
            cert_contact.eng_first_name = eng_first_name
            cert_contact.email = email
            cert_contact.exam_ru = exam_ru
            cert_contact.can_create_cert = can_create_cert

            cert_contact.create_path_file()

            cert_contacts.append(cert_contact)

        except (ValueError, IndexError) as e:
            log.debug(f"Skip row due to error: {e}")
            continue
        except FileNotFoundError:
            log.error(f'No template file {getattr(cert_contact, "template", "unknown")}')
            continue

    return cert_contacts


def clean_export_excel(s):
    s = str(s)
    s = s.replace(',', ', ')
    s = re.sub(r'\s{2,}', ' ', s)
    s = s.strip()
    if s in ('None', '#N/A'):
        s = ''
    return s
