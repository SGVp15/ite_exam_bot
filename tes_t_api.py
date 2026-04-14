import asyncio
import datetime
import json
import time
from pprint import pprint
from Contact import Contact
import dateparser

from Itexpert.ite_api import ITEXPERT_API, update_cert_lk, sent_report_and_cert_lk
from ProctorEDU.selenium_for_proctoredu import ProctorEduSelenium

# async def test_proctoredu():
#     drive = ProctorEduSelenium()
#     await drive.authorization()
#     drive.quit()
#     print("[test] ProctorEDU OK")


# async def main():
#     task1 = asyncio.create_task(test_proctoredu())
#     await task1


if __name__ == '__main__':
    ite_api = ITEXPERT_API()
    all_exam = ite_api.get_list_exams()

    # # Обновить экзамен
    ite_api.add_exam_in_to_exam_by_id(id=28774, exam_in='21008')
    raise 'end'
#
#     # # 4. Тестирование удаления экзамена
#     # for id_exam_delete in (28562,):
#     #     time.sleep(1)
#     #     print(f"\n[4. delete_exam_by_id({id_exam_delete})]")
#     #     r_delete = ITEXPERT_API().delete_exam_by_id(id_exam_delete)
#     #     print("Результат удаления:", r_delete.status_code)
#
    # 2. Тестирование получения экзамена по ID
    ids_itsm = []
    exams = [28558,
             28552,
             28516,
             28515,
             28514,
             28513,
             28512,
             28511,
             28499,
             28498,
             28497,
             28496,
             28495,
             28481,
             28480,
             28348,
             28347,
             28313,
             28312,
             27574,
             27573,
             27572,
             27571,
             27463,
             27462,
             27403,
             27371,
             27349,
             27348,
             27337,
             27084,
             27083,
             26704,
             26703,
             26702,
             26701,
             26700,
             26699,
             26698,
             26697,
             26696,
             26695,
             26694,
             26693,
             26692,
             26691,
             26495,
             26494,
             26338,
             26285,
             ]


#
    for id_exam in [28708, 28499, 26700]:
        print(f"\n[2. get_exam_by_id({id_exam})]")
        r_id = ite_api.get_exam_by_id(id_exam)
        if r_id and r_id.ok:
            try:
                d = json.loads(r_id.text)
                pprint(json.loads(r_id.text))
                pprint(d.get('data').get('exam_in'))
                id_exam = d.get('data').get('exam_in') == '19691'
                print(id_exam)
                if id_exam in ('19691',):
                    ids_itsm.append(id_exam)
            except Exception as e:
                pass
        else:
            print("Не удалось получить экзамен по ID.")
        time.sleep(1)

#     print(ids_itsm)
#     #
#     # # 3. Тестирование создания экзамена
#     # print(f"\n[3. create_exam({contact})]")
#     # r_create = ite_api.create_exam(contact)
#     # if r_create:
#     #     print("Результат создания:", r_create.status_code)
#     #
#     # # 4. Тестирование удаления экзамена
#     # for id_exam_delete in (28505,28506,28507,28508,28509,28510):
#     #     print(f"\n[4. delete_exam_by_id({id_exam_delete})]")
#     #     r_delete = ite_api.delete_exam_by_id(id_exam_delete)
#     #     print("Результат удаления:", r_delete.status_code)
#     # print(f"\n[get_exam_by_email({email})]")
#     # r_id = ite_api.get_exam_by_email(email)
#     # if r_id and r_id.ok:
#     #     pprint(json.loads(r_id.text))
#     # else:
#     #     print("Не удалось получить экзамен по ID.")
#
# #
def main():
    asyncio.run(sent_report_and_cert_lk(date=datetime.datetime(year=2026, month=3, day=20)))
#
#     # contacts = []
#     # contact_list = []
#     # for num in contact_list:
#     #     c = Contact()
#     #     c.date_exam = dateparser.parse(num[0])
#     #     c.exam = num[1]
#     #     c.last_name_rus = num[2]
#     #     c.first_name_rus = num[3]
#     #     c.last_name_eng = num[4]
#     #     c.first_name_eng = num[5]
#     #     c.email = num[6]
#     #     c.exam_id_itexpert = num[7]
#     #     contacts.append(c)
#     # update_cert_lk(contacts=contacts)
#
#
# if __name__ == '__main__':
#     main()
