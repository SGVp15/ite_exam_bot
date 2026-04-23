import asyncio
import sys
from pathlib import Path
from unittest import TestCase

import Moodle.config
from Moodle.parser_html import create_all_report


class Test(TestCase):
    def set_var(monkeypatch):
        test_path = Path("./data/reports").resolve()
        test_path.mkdir(exist_ok=True, parents=True)
        monkeypatch.setattr(Moodle.config, "DIR_REPORTS", test_path)

        # 2. ПЕРЕЗАПИСЫВАЕМ значение во всех уже загруженных модулях
        # Проходим по всем модулям, которые уже успели импортировать root_config
        for name, module in sys.modules.items():
            if hasattr(module, "DIR_REPORTS"):
                monkeypatch.setattr(f"{name}.DIR_REPORTS", test_path, raising=False)

    def test_create_all_report(monkeypatch):
        # set_var(monkeypatch)
        base_path = Path(
            '//192.168.20.100/Administrative server/РАБОТА АДМИНИСТРАТОРА/ОРГАНИЗАЦИЯ IT ЭКЗАМЕНОВ/ЭКЗАМЕНЫ ЦИФРОВОЙ ПУТЬ/Результаты HTML/')

        files = list(base_path.glob('*_80.html'))

        for f in files:
            print(f.name)
            # f.unlink(missing_ok=True)

        async def main():
            await create_all_report(is_only_new_report=True)

        asyncio.run(main())

