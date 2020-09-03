from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import json
import datetime
import locale
import yaml
import sys


def parse_date(date):
    try:
        return datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return None


def replace_html(string):
    string = string.replace("<i>", ' \\emph{').replace("</i>", '}')
    string = string.replace('<a href="', '\\href{').replace(
        '" target="_blank">', '}{').replace("</a>", '}')
    return string


class Configs:
    def __init__(self, path):
        self.config_path = path

        with open(path, encoding='utf8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        self.json_resume_path = data["json_resume_path"]
        self.colors = data["colors"]
        self.left_composition = data["composition"]["first-column"]
        self.right_composition = data["composition"]["second-column"]
        self.name = data["name"] if data["name"] else None
        self.ignore_certificates = data.get("ignore-certificates-of", [])
        self.strings = data['strings']

        self.language = data["language"]
        self.change_lang()

        self.resume = self.load_json()

        for work in self.resume['work']:
            start_date = parse_date(work['startDate'])
            end_date = parse_date(work['endDate'])
            work['startDate'] = start_date.strftime("%B %Y").title() if \
                start_date else work['startDate']
            work['endDate'] = end_date.strftime("%B %Y").title() if \
                end_date else work['endDate']

            work['summary'] = replace_html(work["summary"])

        for school in self.resume['education']:
            start_date = parse_date(school['startDate'])
            end_date = parse_date(school['endDate'])
            school['startDate'] = start_date.strftime("%B %Y").title() if \
                start_date else school['startDate']
            school['endDate'] = end_date.strftime("%B %Y").title() if \
                end_date else school['endDate']

        for work in self.resume['volunteer']:
            start_date = parse_date(work['startDate'])
            end_date = parse_date(work['endDate'])
            work['startDate'] = start_date.strftime("%Y").title() if \
                start_date else work['startDate']
            work['endDate'] = end_date.strftime("%Y").title() if \
                end_date else work['endDate']

            work['summary'] = replace_html(work["summary"])

        for award in self.resume['awards']:
            award['summary'] = replace_html(award["summary"])

        self.certificates = [x for x in self.resume['certificates'] if
                             x.get('category') not in self.ignore_certificates]

        for certificate in self.certificates:
            certificate['summary'] = replace_html(certificate['summary'])

        self.tech_skills = {}
        for skill in self.resume['skills']:
            self.tech_skills[skill['name']] = ', '.join([x[0] for x
                                                         in skill['keywords']])

    def load_json(self):
        with open(self.json_resume_path, encoding="utf-8") as file:
            return json.load(file)

    def change_lang(self):
        if self.language == 'en':
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        elif self.language == 'pt':
            locale.setlocale(locale.LC_TIME, 'pt_BR')
        else:
            locale.setlocale(locale.LC_TIME, '')


if __name__ == '__main__':
    # Try to get option config path from args
    # set to config.yaml if none present
    try:
        config_path = sys.argv[1]
    except IndexError:
        config_path = "config.yaml"

    # load configurations on a global variable
    configs = Configs(config_path)

    file_loader = FileSystemLoader(Path(__file__).parent / f"./templates")
    env = Environment(loader=file_loader,
                      variable_start_string='\\VAR{',
                      variable_end_string='}',
                      trim_blocks=True,
                      autoescape=False, )

    template = env.get_template('cv.jinja2')

    output = template.render(config=configs, resume=configs.resume)

    result_path = Path(__file__).parent / f"./{configs.language}/main.tex"
    with result_path.open(mode='w', encoding='utf-8') as f:
        f.write(output)
