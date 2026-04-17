from unittest import TestCase

from Itexpert.check_log_send_email import get_contacts_from_logs


class Test(TestCase):
    def test_get_contacts_from_logs(self):
        contacts = get_contacts_from_logs()
        print(contacts)