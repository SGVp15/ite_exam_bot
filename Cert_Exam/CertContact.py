import datetime
from pathlib import Path

from Utils.translit import replace_ru_char_to_eng_char, transliterate
from Utils.utils import clean_string
from .config_cert_exam import DIR_CERTS, TEMPLATE_FOLDER


class CertContact:
    def __init__(self, number: int = 0,
                 exam: str = '',
                 email: str = '',
                 last_name_ru: str = '',
                 first_name_ru: str = '',
                 last_name_eng: str = '',
                 first_name_eng: str = '',
                 date_exam: datetime.datetime | None = None,
                 exam_ru: str = '', exam_eng: str = '',
                 file_out_png: Path = '',
                 can_create_cert=0,
                 ):
        self.can_create_cert = can_create_cert or 0
        self.number = number
        self.exam: str = exam.upper()
        self.email: str = email.lower()
        self.ru_last_name: str = last_name_ru.strip()
        self.ru_first_name: str = first_name_ru.strip()
        self.eng_last_name: str = last_name_eng.strip()
        self.eng_first_name: str = first_name_eng.strip()
        self.date_exam: datetime.datetime = date_exam
        self.exam_ru: str = exam_ru.strip()
        self.exam_eng: str = exam_eng.strip()
        self.file_out_png: Path = file_out_png
        self.template: str = ''
        self.create_path_file()
        self.normalize()

    def create_path_file(self):
        self.template = self.exam + '.png'
        if not Path(TEMPLATE_FOLDER, self.template).exists():
            raise FileNotFoundError
        date_exam = f"{self.date_exam.strftime('%Y.%m.%d')}"
        self.file_out_png = Path(DIR_CERTS, self.date_exam.strftime('%Y'),
                                 self.date_exam.strftime('%m'),
                                 f"{self.exam}_{date_exam}_{self.ru_last_name}_{self.ru_first_name}"
                                 f"_{self.number}_{self.email}.png")

    def __eq__(self, other):
        try:
            if (
                    self.number == other.number and
                    self.exam == other.exam and
                    self.email == other.email and
                    self.ru_last_name == other.ru_last_name and
                    self.ru_first_name == other.ru_first_name and

                    self.eng_last_name == other.eng_last_name and
                    self.eng_first_name == other.eng_first_name and

                    self.date_exam == other.date_exam
            ):
                return True
        except AttributeError:
            pass
        return False

    def normalize(self):
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
