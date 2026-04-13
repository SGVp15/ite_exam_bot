import asyncio

from Moodle.main import download_reports_moodle


def test_download_reports_moodle():
    try:
        asyncio.run(download_reports_moodle(is_only_new=False, start_num=50))
    except KeyboardInterrupt:
        print("Программа остановлена пользователем")
