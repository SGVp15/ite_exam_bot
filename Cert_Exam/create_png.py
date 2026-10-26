from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from root_config import FONT_PATH_GEOMETRIA_LIGHT, FONT_PATH_RUBIK_REGULAR
from .CertContact import CertContact

from .config_cert_exam import TEMPLATE_FOLDER


def create_png(cert_contact: CertContact):
    img = Image.open(f'{TEMPLATE_FOLDER}/{cert_contact.template}')

    image_draw = ImageDraw.Draw(img)

    geometria_70 = ImageFont.truetype(FONT_PATH_GEOMETRIA_LIGHT, 70)
    image_draw.text((647, 1220),
                    f'№ {cert_contact.number:06}   {cert_contact.date_exam.strftime('%d.%m.%Y')}', font=geometria_70,
                    fill=(16, 21, 84))

    rubik_115 = ImageFont.truetype(FONT_PATH_RUBIK_REGULAR, 115, )
    image_draw.text((round(0.59 * img.width), 1550),
                    f'{cert_contact.ru_last_name} {cert_contact.ru_first_name}', font=rubik_115, fill=(16, 21, 84),
                    anchor='mm')

    rubik_70 = ImageFont.truetype(FONT_PATH_RUBIK_REGULAR, 70)
    image_draw.text((round(0.59 * img.width), 1700),
                    f'{cert_contact.eng_last_name} {cert_contact.eng_first_name}', font=rubik_70, fill=(16, 21, 84),
                    anchor='mm')

    img.save(cert_contact.file_out_png)
