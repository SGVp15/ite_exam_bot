from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

from Moodle.parser_html import parse_exam_percent, send_failed_exam_notification


class TestFailedExamNotification(TestCase):
    def test_parse_exam_percent(self):
        """Проверяет разбор процентов в формате Moodle.

        На вход подаются дробный процент с запятой, целые проценты с точкой
        или без дробной части, а также строка без числового результата.
        Ожидается число типа float для найденного процента и None, если процента нет.
        """
        for grade, expected in [
            ('68,5%', 68.5), ('69%', 69.0), ('75.00%', 75.0), ('not available', None)
        ]:
            with self.subTest(grade=grade):
                self.assertEqual(parse_exam_percent(grade), expected)


    def test_failed_report_sends_email_to_exam_mailbox_once(self):
        """Проверяет письмо при несдаче и защиту от повторной отправки.

        Для оценки 68,5% создаётся временный отчёт, а SMTP и рендер шаблона
        заменяются mock-объектами. Ожидается одно письмо участнику с отчётом
        во вложении и exam@itexpert.ru в скрытой копии. Повторный вызов для
        того же отчёта не отправляет второе письмо и оставляет отметку отправки.
        """
        with TemporaryDirectory() as folder:
            report = Path(folder) / 'report.html'
            report.write_text('<html>report</html>', encoding='utf-8')
            test_info = {
                'Оценка': '68,5%', 'user': 'Иван Иванов', 'test_name': 'ITSMC ТЕСТ',
                'email': 'g.savushkin@itexpert.ru',
            }
            rendered = Mock(render_document=Mock(return_value='<p>failed</p>'))

            with patch('Moodle.parser_html.MyJinja', return_value=rendered), patch(
                'Moodle.parser_html.EmailSending'
            ) as email_sending:
                self.assertTrue(send_failed_exam_notification(test_info, report))
                self.assertFalse(send_failed_exam_notification(test_info, report))

            email_sending.assert_called_once_with(
                to='g.savushkin@itexpert.ru', bcc=['exam@itexpert.ru'],
                subject='Экзамен не сдан: ITSMC', html='<p>failed</p>',
                files_path=[str(report)],
            )
            email_sending.return_value.send_email.assert_called_once_with()
            self.assertTrue(report.with_name(f'{report.name}.failed_notice_sent').is_file())


    def test_passed_or_unknown_grade_does_not_send(self):
        """Проверяет, что успешный или неизвестный результат не вызывает письмо.

        Проверяются оценки 69%, 70,1% и пустая оценка. Ожидается False для
        каждого случая и отсутствие вызова EmailSending.
        """
        with TemporaryDirectory() as folder:
            report = Path(folder) / 'report.html'
            report.write_text('<html>report</html>', encoding='utf-8')
            for grade in ('69%', '70,1%', ''):
                with self.subTest(grade=grade), patch('Moodle.parser_html.EmailSending') as email_sending:
                    self.assertFalse(send_failed_exam_notification({'Оценка': grade}, report))
                    email_sending.assert_not_called()


    def test_email_failure_removes_marker_and_allows_retry(self):
        """Проверяет восстановление после ошибки отправки через SMTP.

        Первая отправка для оценки 40% искусственно завершается исключением.
        Ожидается, что отметка отправки будет удалена. При следующем вызове
        отправка проходит успешно, функция возвращает True, а отметка создаётся.
        """
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
