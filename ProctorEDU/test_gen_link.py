from unittest import TestCase

from ProctorEDU.gen_link import generate_proctoring_link


class Test(TestCase):
    def test_generate_proctoring_link(self):
        provider = "jwt"

        expires = 500
        subject: str = '2026-05-22T12:00:00Z_boris_kamalov_SCMC_online-1'
        username: str = 'boris_kamalov'
        nickname: str = 'boris_kamalov'

        # Генерация ссылки
        link = generate_proctoring_link(subject=subject, username=username,
                                        nickname=nickname, provider=provider, expires_in_hours=expires)
        print(link)


if __name__ == '__main__':
    import unittest

    unittest.main()
