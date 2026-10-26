import urllib.parse
from random import choice

import requests

from Contact import Contact
from Utils.log import log
from ..config import MOODLE_URL, MOODLE_TOKEN


class MoodleApi:
    RESPONSE_FORMAT = 'json'
    API_URL = f'{MOODLE_URL}/webservice/rest/server.php'

    def __get_url_with_params(self, function_name: str):
        """Формирует полный URL с токеном и функцией Moodle."""
        url_params = {
            'wstoken': MOODLE_TOKEN,
            'wsfunction': function_name,
            'moodlewsrestformat': self.RESPONSE_FORMAT
        }
        url_with_params = self.API_URL + '?' + urllib.parse.urlencode(url_params)
        return url_with_params

    @staticmethod
    def __format_post_array(data: dict, array_name: str = 'users') -> dict:
        """
        Преобразует словарь в формат POST-данных Moodle-массива:
        {'username': 'test'} -> {'users[0][username]': 'test'}
        """
        return {
            f'{array_name}[0][{key}]': value
            for key, value in data.items()
        }

    def _get_id_shortname_course(self) -> dict:
        d = {}
        for course in self.core_course_get_courses():
            d[course.get('shortname')] = course.get('id')
        return d

    # --- ОСНОВНЫЕ МЕТОДЫ API ---

    def core_user_get_users_by_field(self, value: str, field='email') -> dict:
        # ... (Код core_user_get_users_by_field без изменений) ...
        function_name = "core_user_get_users_by_field"
        url_with_params = self.__get_url_with_params(function_name)
        post_data_dict = {'field': field, 'values[0]': value}
        try:
            response = requests.post(url_with_params, data=post_data_dict)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list) and data:
                return data[0]
            elif isinstance(data, dict) and 'exception' in data:
                log.error(f"❌ Ошибка Moodle API при поиске: {data.get('errorcode')}. Сообщение: {data.get('message')}")
                return {}
            else:
                return {}
        except requests.exceptions.RequestException as e:
            log.error(f"❌ Произошла ошибка запроса (Сеть/HTTP) при поиске: {e}")
            return {}

    def core_user_create_users(self, user: Contact):
        function_name = "core_user_create_users"
        url_with_params = self.__get_url_with_params(function_name)
        new_user_data = {
            'username': f'{user.username.strip()}', 'password': f'{user.password}',
            'firstname': f'{user.ru_first_name.strip()}', 'lastname': f'{user.ru_last_name.strip()}',
            'email': f'{user.email}',
        }
        post_data_dict = self.__format_post_array(new_user_data, array_name='users')
        log.info(f"Попытка создать пользователя: {new_user_data['username']}")
        try:
            response = requests.post(url_with_params, data=post_data_dict)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0 and 'id' in data[0]:
                new_user_info = data[0]
                log.info(f"✅ Пользователь успешно создан! ID: {new_user_info.get('id')}")
                return new_user_info.get('id')
            elif isinstance(data, dict) and 'exception' in data:
                log.error(
                    f"❌ Ошибка Moodle API при создании: {data.get('errorcode')}. Сообщение: {data.get('message')}")
                return None
            else:
                log.error(f"⚠️ Получен неожиданный формат ответа при создании: {data}")
                return None
        except requests.exceptions.RequestException as e:
            log.error(f"❌ Произошла ошибка запроса (Сеть/HTTP) при создании: {e}")
            return None

    def core_user_update_password(self, user_id: int, new_password: str) -> bool:
        function_name = "core_user_update_users"
        url_with_params = self.__get_url_with_params(function_name)
        update_data = {'id': user_id, 'password': new_password}
        post_data_dict = self.__format_post_array(update_data, array_name='users')
        log.info(f"Попытка обновить пароль для пользователя ID: {user_id}")
        try:
            response = requests.post(url_with_params, data=post_data_dict)
            if response.status_code == 200:
                return True
            log.error(
                f"❌ Ошибка Moodle API при обновлении пароля: HTTP {response.status_code}. "
                f"Ответ: {response.text}"
            )
            return False
        except requests.exceptions.RequestException as e:
            log.error(f"❌ Произошла ошибка запроса (Сеть) при обновлении пароля: {e}")
            return False

    def enrol_manual_enrol_users(self, course_id: int, user_id_to_enrol: int) -> bool:
        """list of (
            object {
                roleid int   //Role to assign to the user
                userid int   //The user that is going to be enrolled
                courseid int   //The course to enrol the user role in
                timestart int  Необязательно //Timestamp when the enrolment start
                timeend int  Необязательно //Timestamp when the enrolment end
                suspend int  Необязательно //set to 1 to suspend the enrolment
                }
        )

        enrolments[0][roleid]= int
        enrolments[0][userid]= int
        enrolments[0][courseid]= int
        enrolments[0][timestart]= int
        enrolments[0][timeend]= int
        enrolments[0][suspend]= int

        """
        function_name = "enrol_manual_enrol_users"
        ROLE_ID_STUDENT = 5
        url_with_params = self.__get_url_with_params(function_name)
        enrolment_record = {'roleid': ROLE_ID_STUDENT, 'userid': user_id_to_enrol, 'courseid': course_id}
        post_data_dict = self.__format_post_array(enrolment_record, array_name='enrolments')
        log.info(f"Попытка зачислить пользователя (ID: {user_id_to_enrol}) на курс (ID: {course_id})")
        try:
            response = requests.post(url_with_params, data=post_data_dict)
            response.raise_for_status()
            data = response.json() if response.text else []
            if response.status_code == 200:
                log.info(f"✅ Зачисление ID {user_id_to_enrol} на курс {course_id} успешно.")
                return True
            elif isinstance(data, dict) and 'exception' in data:
                log.error(
                    f"❌ Ошибка Moodle API при зачислении: {data.get('errorcode')}. Сообщение: {data.get('message')}")
                return False
            else:
                log.error(f"⚠️ Получен неожиданный формат ответа при зачислении: {data}")
                return False
        except requests.exceptions.RequestException as e:
            log.error(f"❌ Произошла ошибка запроса (Сеть/HTTP) при зачислении: {e}")
            return False

    def core_course_get_courses(self) -> []:
        function_name = "core_course_get_courses"
        url_with_params = self.__get_url_with_params(function_name)
        try:
            response = requests.post(url_with_params)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'exception' in data:
                log.error(f"❌ Ошибка Moodle API: {data.get('errorcode')}")
            else:
                log.error(f"⚠️ Неожиданный формат ответа: {data}")
        except requests.exceptions.RequestException as err:
            log.error(f"❌ Произошла ошибка: {err}")
        return []

    def process_user_and_enrollment(self, contact: Contact):
        '''
        1. Поиск пользователя по email.
        2. Если найден - обновляет пароль. Если не найден - создает пользователя.
        3. Случайным образом выбирает курс, если указан только префикс (например, 'BAFC').
        4. Зачисляет пользователя на выбранный курс.
        '''
        requested_shortname = contact.exam
        log.info(
            f"--- Запуск процесса для пользователя: {contact.email} и запрошенного курса: {requested_shortname} ---")

        # 1. ПОДГОТОВКА КУРСА: Поиск ID курса (с учетом случайного выбора)

        course_map = self._get_id_shortname_course()

        # 1.1. Находим все курсы, которые начинаются с запрошенного имени
        possible_courses = [
            shortname for shortname in course_map.keys()
            if shortname.startswith(requested_shortname)
        ]

        if not possible_courses:
            log.error(f"❌ Курсы, начинающиеся с '{requested_shortname}', не найдены. Процесс остановлен.")
            return False

        # 1.2. Случайный выбор одного короткого имени курса
        final_shortname = choice(possible_courses)
        course_id = course_map[final_shortname]
        contact.moodle_id_exam = course_id

        log.info(f"Выбран случайный курс для зачисления: '{final_shortname}' (ID: {course_id}).")

        # 2. ПРОЦЕСС ПОЛЬЗОВАТЕЛЯ: Проверка и создание/обновление

        user_data = self.core_user_get_users_by_field(contact.email, field='email')
        user_id = None

        if user_data:
            # Пользователь найден
            user_id = user_data.get('id')
            log.info(f"✅ Пользователь {contact.email} найден (ID: {user_id}).")

            update_success = self.core_user_update_password(user_id, contact.password)
            if update_success:
                log.info("✅ Пароль успешно обновлен.")
            else:
                log.error("❌ Не удалось обновить пароль.")

        else:
            # Пользователь не найден -> Создание
            log.info(f"⚠️ Пользователь {contact.email} не найден. Создание нового пользователя...")
            user_id = self.core_user_create_users(contact)

            if not user_id:
                log.error(f"❌ Не удалось создать пользователя {contact.email}. Процесс остановлен.")
                return False

        contact.moodle_id_user = user_id
        # 3. ЗАЧИСЛЕНИЕ
        if user_id:
            log.info(f"Начало зачисления пользователя (ID: {user_id}) на курс '{final_shortname}' (ID: {course_id}).")
            enrollment_successful = self.enrol_manual_enrol_users(
                course_id=course_id,
                user_id_to_enrol=user_id
            )
            return enrollment_successful

        return False

