import csv

from ProctorEDU.config import CSV_HEADER_SESSION, CSV_HEADER_USER, SESSIONS_CSV_FILE, USERS_CSV_FILE
from Contact import Contact


async def create_csv_files(contacts: list[Contact]):
    with open(SESSIONS_CSV_FILE, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = CSV_HEADER_SESSION.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for contact in contacts:
            CSV_HEADER_SESSION.update({
                'student.username': contact.username,
                'members': f'proctor-{contact.online}',
                'subject': contact.subject,
                'identifier': contact.identifier,
                'scheduledAt': contact.scheduled_at,
                'openAt': contact.open_at,
                'closeAt': contact.close_at,
                'deadline': contact.deadline,
                'removeAt': contact.remove_at,
            })

            writer.writerow(CSV_HEADER_SESSION)

    with open(USERS_CSV_FILE, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = CSV_HEADER_USER.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for contact in contacts:
            CSV_HEADER_USER.update({
                'nickname': contact.email,
                'username': contact.username,
                'password': contact.password,
            })
            writer.writerow(CSV_HEADER_USER)
