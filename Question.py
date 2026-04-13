import re


class Question:
    def __init__(self,
                 id_question: str = '',
                 text_question: str = '',
                 ans_a: str = '',
                 ans_b: str = '',
                 ans_c: str = '',
                 ans_d: str = '',
                 image: str = '',
                 box_question: int = 0,
                 category: str = '',
                 exam: str = '',
                 ):
        self.id_question: str = id_question
        self.text_question: str = text_question
        self.ans_a: str = ans_a
        self.ans_b: str = ans_b
        self.ans_c: str = ans_c
        self.ans_d: str = ans_d
        self.image: str = image
        self.box_question: int = box_question
        self.category: str = category
        self.exam: str = exam
        self.__post_init__()

    def __post_init__(self):
        if self.id_question and not self.exam:
            self.exam = self.id_question.split('.')[0]

    def __str__(self):
        return (
            f'\nexam=[{self.exam}]\n'
            f'text_question=[{self.text_question}]\n'
            f'id_question=[{self.id_question}]\n'
            f'ans_a=[{self.ans_a}]\n'
            f'ans_b=[{self.ans_b}]\n'
            f'ans_c=[{self.ans_c}]\n'
            f'ans_d=[{self.ans_d}]\n'
            f'image=[{self.image}]\n'
        )

    # def __hash__(self):
    #     # Вспомогательные функции очистки должны быть доступны внутри или вынесены в статические методы/модуль.
    #     # Используем ту же логику очистки, что и в __eq__
    #     def clean(s):
    #         if not s:
    #             return ""
    #         s = re.sub(r'\s', '', s)
    #         s = re.sub(r'[^\wа-яА-Я]', '', s)
    #         s = s.strip().lower()
    #         # Удаление текста изображения (как в del_image_text)
    #         s = re.sub(r'\[[\w_.]+\]', '', s)
    #         return s
    #
    #     def clean_text_question(s):
    #         return clean(s)
    #
    #     # 1. Хешируем текст вопроса
    #     q_hash = clean_text_question(self.text_question)
    #
    #     # 2. Хешируем ответы.
    #     # Так как в __eq__ вы сравниваете их как множества (порядок не важен),
    #     # мы должны использовать frozenset, который является неизменяемым и хешируемым.
    #     answers = frozenset({
    #         clean(self.ans_a),
    #         clean(self.ans_b),
    #         clean(self.ans_c),
    #         clean(self.ans_d)
    #     })
    #
    #     # Возвращаем хеш от кортежа основных признаков
    #     return hash((q_hash, answers))

    def __eq__(self, other):
        def clean_text_question(s):
            s = clean(s)
            s = re.sub(r'[^\wа-яА-Я]', '', s)
            return s

        def clean(s):
            s = re.sub(r'\s', '', s)
            s = re.sub(r'[^\wа-яА-Я]', '', s)
            s = s.strip()
            s = s.lower()
            s = del_image_text(s)
            return s

        def del_image_text(s):
            s = re.sub(r'\[[\w_.]+\]', '', s)
            s = s.strip()
            return s

        if not isinstance(other, Question):
            return NotImplemented

        # 2. Сравниваем текст вопроса
        a,b=clean_text_question(self.text_question) , clean_text_question(other.text_question)
        question_text_equal = clean_text_question(self.text_question) == clean_text_question(other.text_question)
        if not question_text_equal:
            return False

        # 3. Сравниваем варианты ответов как множества
        # Создаём множества из вариантов ответов для каждого объекта
        self_answers = set()
        other_answers = set()
        self_answers = {clean(self.ans_a), clean(self.ans_b), clean(self.ans_c), clean(self.ans_d)}
        other_answers = {clean(other.ans_a), clean(other.ans_b), clean(other.ans_c), clean(other.ans_d)}

        # Варианты ответов равны, если множества равны
        answers_set_equal = self_answers == other_answers
        if not answers_set_equal:
            return False

        return True
