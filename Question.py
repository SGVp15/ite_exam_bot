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

    def __str__(self):
        return (f'[{self.text_question=}]\n'
                f'[{self.id_question=}]\n'
                f'[{self.ans_a=}]\n'
                f'[{self.ans_b=}]\n'
                f'[{self.ans_c=}]\n'
                f'[{self.ans_d=}]\n'
                f'[{self.image=}]\n'
                )

    def __eq__(self, other):
        def clean(s):
            s = re.sub(r'\s', '', s)
            s = s.strip()
            return s

        if not isinstance(other, Question):
            return NotImplemented

        # 2. Сравниваем текст вопроса
        question_text_equal = clean(self.text_question) == clean(other.text_question)
        if not question_text_equal:
            return False

        # 3. Сравниваем варианты ответов как множества
        # Создаём множества из вариантов ответов для каждого объекта
        self_answers = {clean(self.ans_a), clean(self.ans_b), clean(self.ans_c), clean(self.ans_d)}
        other_answers = {clean(other.ans_a), clean(other.ans_b), clean(other.ans_c), clean(other.ans_d)}

        # Варианты ответов равны, если множества равны
        # (т.е. содержат одинаковые строки, независимо от того, какой из них был ans_a, ans_b, и т.д.)
        answers_set_equal = self_answers == other_answers
        if not answers_set_equal:
            return False

        return True
