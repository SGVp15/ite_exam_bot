from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

from Moodle.parser_html import parse_exam_percent, send_failed_exam_notification


class TestFailedExamNotification(TestCase):
    def test_parse_exam_percent(self):
        for grade, expected in [
            ('68,5%', 68.5), ('69%', 69.0), ('75.00%', 75.0), ('not available', None)
        ]:
            with self.subTest(grade=grade):
                self.assertEqual(parse_exam_percent(grade), expected)


    def test_failed_report_sends_email_to_exam_mailbox_once(self):
        with TemporaryDirectory() as folder:
            report = Path(folder) / 'report.html'
            report.write_text('<html>report</html>', encoding='utf-8')
            test_info = {
                'Оценка': '68,5%', 'user': 'Иван Иванов', 'test_name': 'ITSMC ТЕСТ',
                'email': 'student@example.com',
            }
            rendered = Mock(render_document=Mock(return_value='<p>failed</p>'))

            with patch('Moodle.parser_html.MyJinja', return_value=rendered), patch(
                'Moodle.parser_html.EmailSending'
            ) as email_sending:
                self.assertTrue(send_failed_exam_notification(test_info, report))
                self.assertFalse(send_failed_exam_notification(test_info, report))

            email_sending.assert_called_once_with(
                to='student@example.com', bcc=['exam@itexpert.ru'],
                subject='Экзамен не сдан: ITSMC', html='<p>failed</p>',
                files_path=[str(report)],
            )
            email_sending.return_value.send_email.assert_called_once_with()
            self.assertTrue(report.with_name(f'{report.name}.failed_notice_sent').is_file())


    def test_passed_or_unknown_grade_does_not_send(self):
        with TemporaryDirectory() as folder:
            report = Path(folder) / 'report.html'
            report.write_text('<html>report</html>', encoding='utf-8')
            for grade in ('69%', '70,1%', ''):
                with self.subTest(grade=grade), patch('Moodle.parser_html.EmailSending') as email_sending:
                    self.assertFalse(send_failed_exam_notification({'Оценка': grade}, report))
                    email_sending.assert_not_called()


    def test_email_failure_removes_marker_and_allows_retry(self):
        with TemporaryDirectory() as folder:
            report = Path(folder) / 'report.html'
            report.write_text('<html>report</html>', encoding='utf-8')
            test_info = {'Оценка': '40%', 'user': 'Иван Иванов', 'test_name': 'ITSMC'}
            rendered = Mock(render_document=Mock(return_value='<p>failed</p>'))
            with patch('Moodle.parser_html.MyJinja', return_value=rendered), patch(
                'Moodle.parser_html.EmailSending'
            ) as email_sending:
                email_sending.return_value.send_email.side_effect = [RuntimeError('SMTP error'), None]
                with self.assertRaisesRegex(RuntimeError, 'SMTP error'):
                    send_failed_exam_notification(test_info, report)
                self.assertFalse(report.with_name(f'{report.name}.failed_notice_sent').exists())
                self.assertTrue(send_failed_exam_notification(test_info, report))
