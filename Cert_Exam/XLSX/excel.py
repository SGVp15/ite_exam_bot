import re

import dateparser
from ..CertContact import CertContact
from ..UTILS.log import log
from ..XLSX.my_excel import read_excel_file
from ..config_cert_exam import FILE_XLSX, SHEETNAME


def get_contact_from_cert_excel(filename=FILE_XLSX) -> list[CertContact]:
    data = read_excel_file(filename)
    rows = data.get(SHEETNAME, [])

    contact_list = []
    date_settings = {'DATE_ORDER': 'DMY'}

    for row in rows:
        if not row or len(row) < 9:
            continue
        clean_row = [clean_export_excel(str(item)) for item in row]

        try:
            (num,
             date,
             exam,
             ru_last_name,
             ru_first_name,
             eng_last_name,
             eng_first_name,
             email,
             can_create_cert,
             exam_ru,) = clean_row[:10]

            number = int(num)
            date_exam = date
            if not date_exam or not email:
                continue

            contact = CertContact(
                number=number,
                exam=exam,
                date_exam=dateparser.parse(date, settings=date_settings),
                last_name_ru=ru_last_name,
                first_name_ru=ru_first_name,
                last_name_eng=eng_last_name,
                first_name_eng=eng_first_name,
                email=email,
                exam_ru=exam_ru,
                can_create_cert=can_create_cert
            )

            contact_list.append(contact)

        except (ValueError, IndexError) as e:
            log.debug(f"Skip row due to error: {e}")
            continue
        except FileNotFoundError:
            log.error(f'No template file {getattr(contact, "template", "unknown")}')
            continue
        except Exception as e:
            log.error(f'Exception {e}')
            continue

    return contact_list


def clean_export_excel(s):
    s = str(s)
    s = s.replace(',', ', ')
    s = re.sub(r'\s{2,}', ' ', s)
    s = s.strip()
    if s in ('None', '#N/A'):
        s = ''
    return s
