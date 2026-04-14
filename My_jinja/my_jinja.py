from jinja2 import Environment, FileSystemLoader
from Email.config import TEMPLATE_FOLDER


class MyJinja:
    def __init__(self, template_folder: str = None, template_file: str = 'course_registration.html'):
        if template_folder:
            self.template_folder = template_folder
        else:
            self.template_folder = TEMPLATE_FOLDER

        self.environment = Environment(auto_reload=True, loader=FileSystemLoader(self.template_folder))
        self.template_file = self.environment.get_template(template_file)

    def render_document(self, user) -> str:
        return self.template_file.render(user=user)
