import asyncio
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from Cert_Exam.main_cert_exam import create_exam_cert
from Itexpert.check_log_send_email import check_log_and_send_email_to_manager
from Itexpert.ite_api import sent_report_and_cert_lk
from Moodle.main import download_reports_moodle
from Moodle.parser_html import create_all_report
from Telegram.main import start_bot
from Utils.chromedriver_autoupdate import ChromedriverAutoupdate
from Utils.git_update import git_update
from Utils.log import log
from main_registration import server_file_registration


async def main():
    scheduler = AsyncIOScheduler()

    # Запуск проверки логов и отправки писем менеджерам
    scheduler.add_job(
        check_log_and_send_email_to_manager,
        CronTrigger(minute='0,30'),
        id='check_log_and_send_email_to_manager'
    )

    # Запуск скачивание страницы отчета из moodle в 00 минут
    scheduler.add_job(
        download_reports_moodle,
        CronTrigger(minute='0,30'),
        id='download_reports_moodle',
        next_run_time=datetime.datetime.now(),  # при старте
        replace_existing=True,
    )

    # # Запуск создание отчетов
    # scheduler.add_job(
    #     create_all_report,
    #     CronTrigger(minute='10'),
    #     id='create_all_report',
    #     next_run_time=datetime.datetime.now() + datetime.timedelta(minutes=10),  # при старте
    #     replace_existing=True,
    # )

    # Запуск Создание сертификатов
    scheduler.add_job(
        create_exam_cert,
        CronTrigger(minute='5,35'),
        id='scheduler_main_create_exam_cert'
    )

    # Запуск Отправка отчетов и сертификатов
    scheduler.add_job(
        sent_report_and_cert_lk,
        CronTrigger(minute='10,40'),
        id='sent_report_and_cert_lk',
    )

    # Запуск файла на сервере для регистрации на экзамен
    scheduler.add_job(
        server_file_registration,
        IntervalTrigger(seconds=120),
        id='server_file_registration',
        next_run_time=datetime.datetime.now(),  # Проверить сразу при старте
        replace_existing=True,
    )

    # Запуск проверки обновлений Git каждые 60 секунд
    scheduler.add_job(
        git_update,
        IntervalTrigger(seconds=120),
        id='git_check',
        # next_run_time=datetime.datetime.now(),  # Проверить сразу при старте
        replace_existing=True,
    )

    scheduler.start()
    log.info("Планировщик запущен успешно.")

    await start_bot()


if __name__ == '__main__':
    ChromedriverAutoupdate(operatingSystem="win").check()

    try:
        log.info('Exam_Registration_bot START')
        # asyncio.run сам создаст loop и запустит main()
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Бот остановлен")
    finally:
        log.error('Exam_Registration_bot STOP')
