import yaml
import sys
import json
import datetime
import locale
from pathlib import Path


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
        self.ignore_certificates = data["ignore-certificates-of"] if \
            data["ignore-certificates-of"] else []
        self.strings = data['strings']

        self.language = data["language"]
        self.change_lang()

        self.resume = self.load_json()

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


def replace_html(string):
    string = string.replace("<i>", ' \\emph{').replace("</i>", '}')
    string = string.replace('<a href="', '\\href{').replace(
        '" target="_blank">', '}{').replace("</a>", '}')
    return string


def parse_date(date):
    try:
        return datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return None


def start_doc():
    result.append("""%% If you need to pass whatever options to xcolor
\\PassOptionsToPackage{dvipsnames}{xcolor}
\\documentclass[10pt,a4paper,ragged2e,withhyper]{altacv}

% Change the page layout if you need to
\\geometry{left=1.25cm,right=1.25cm,top=1.5cm,bottom=1.5cm,columnsep=1.2cm}

\\usepackage{paracol}

% Change the font if you want to, depending on whether
% you're using pdflatex or xelatex/lualatex
\\ifxetexorluatex
    % If using xelatex or lualatex:
    \\setmainfont{Roboto Slab}
    \\setsansfont{Lato}
    \\renewcommand{\\familydefault}{\\sfdefault}
\\else
    % If using pdflatex:
    \\usepackage[rm]{roboto}
    \\usepackage[defaultsans]{lato}
    % \\usepackage{sourcesanspro}
    \\renewcommand{\\familydefault}{\\sfdefault}
\\fi
""")

    result.append("\\definecolor{SlateGrey}{HTML}{2E2E2E}")
    for color in configs.colors:
        result.append(
            f"\\definecolor{{{color}Color}}{{HTML}}{{"
            f"{configs.colors[color]}}}")
        result.append(
            f"\\colorlet{{{color}}}{{{color}Color}}")

    result.append("""\\renewcommand{\\namefont}{\\Huge\\rmfamily\\bfseries}
\\renewcommand{\\personalinfofont}{\\small}
\\renewcommand{\\cvsectionfont}{\\LARGE\\rmfamily\\bfseries}
\\renewcommand{\\cvsubsectionfont}{\\large\\bfseries}

\\renewcommand{\\itemmarker}{{\\small\\textbullet}}
\\renewcommand{\\ratingmarker}{\\faCircle}

\\begin{document}
""")


def build_header():
    name = configs.name if configs.name else configs.resume['basics']['name']
    email = configs.resume['basics']['email']
    phone = configs.resume['basics']['phone']
    location = configs.resume['basics']['location']['city'] + ', ' + \
               configs.resume['basics']['location']['region'] + \
               ', ' + \
               configs.resume['basics']['location']['countryCode']

    result.append(f"\n\\name{{{name}}}")
    result.append("\\tagline{}")
    result.append("\\photoL{2.5cm}{photo}")

    result.append(f"""\\personalinfo{{%
  \\email{{{email}}}
  \\phone{{{phone}}}
  \\location{{{location}}}
}}""")

    result.append("\\personalinfotwo{%")
    result.append("  \\NewInfoField{stackoverflow}{\\faStackOverflow}"
                  "[https://stackoverflow.com/users/3042266/]")
    result.append("  \\NewInfoField{instagram}{\\faInstagram}"
                  "[https://www.instagram.com/]")
    result.append(
        f"  \\homepage{{"
        f"{configs.resume['basics']['website'].replace('https://', '')}}}")

    for profile in configs.resume['basics']['profiles']:
        result.append(f"  \\{profile['network'].replace(' ', '')}"
                      f"{{{profile['username']}}}")

    result.append('}')

    result.append('\\makecvheader')
    result.append("""\\AtBeginEnvironment{itemize}{\\small}
%% Set the left/right column width ratio to 6:4.
\\columnratio{0.6}
\\begin{paracol}{2}
""")


def new_page():
    result.append("\n\\newpage\n")


def switch():
    result.append("\n\\switchcolumn\n")


def end():
    result.append("\n\\end{paracol}\n\\end{document}\n")


def work():
    result.append(f"\\cvsection{{{configs.strings['work']}}}")

    for index, work in enumerate(configs.resume['work']):
        start_date = parse_date(work['startDate'])
        start_date = start_date.strftime("%B %Y").title() if start_date else \
            work['startDate']

        end_date = parse_date(work['endDate'])
        end_date = end_date.strftime("%B %Y").title() if end_date else work[
            'endDate']

        result.append(
            f"\\cvevent{{{work['position']}}}{{{work['company']}}}{{"
            f"{start_date + ' -- ' + end_date}}}{{{work['location']}}}")
        result.append(replace_html(work["summary"])) if work[
            'summary'] else None

        if work['highlights']:
            result.append("\\begin{itemize}")
            for highlight in work['highlights']:
                result.append("\\item " + highlight)
            result.append('\\end{itemize}')

        if index < len(configs.resume['work']) - 1:
            result.append('\n\\divider\n')

    result.append("\\medskip")


def technical_skills():
    result.append(f"\\cvsection{{{configs.strings['technical-skills']}}}")

    result.append("\\begin{itemize}")

    for skill in configs.resume['skills']:
        result.append(
            '\\item ' + "\\textbf{" + skill['name'] + ":} " + ', '.join(
                [x[0] for x in skill['keywords']]))

    result.append("\\end{itemize}")

    result.append("\n\\medskip\n")


def certificates():
    result.append(f"\\cvsection{{{configs.strings['certificates']}}}")

    certificates_ls = [x for x in configs.resume['certificates'] if
                       x.get('category') not in configs.ignore_certificates]

    for index, certificate in enumerate(certificates_ls):
        if certificate.get('url', False):
            result.append(
                f"\\cvevent{{\\href{{{certificate['url']}}}{{"
                f"{certificate['title']}}}}}{{{certificate['issuer']}}}{{"
                f"{certificate['date']}}}{{}}")
        else:
            result.append(
                f"\\cvevent{{{certificate['title']}}}{{"
                f"{certificate['issuer']}}}{{{certificate['date']}}}{{}}")
        result.append(replace_html(certificate['summary']))

        if index < len(configs.resume['certificates']) - 1:
            result.append('\n\\divider\n')

    result.append("\n\\medskip\n")


def education():
    result.append(f"\\cvsection{{{configs.strings['education']}}}")

    for index, school in enumerate(configs.resume['education']):
        start_date = parse_date(school['startDate'])
        start_date = start_date.strftime("%B %Y").title() if start_date else \
            school['startDate']

        end_date = parse_date(school['endDate'])
        end_date = end_date.strftime("%B %Y").title() if end_date else school[
            'endDate']

        if school.get('website', False):
            result.append(
                f"\\cvevent{{\\href{{{school['website']}}}"
                f"{{{school['area'] + ', ' + school['studyType']}}}}}"
                f"{{{school['institution']}}}{{"
                f"{start_date + ' -- ' + end_date}}}{{}}")
        else:
            result.append(
                f"\\cvevent{{{school['area'] + ', ' + school['studyType']}}}"
                f"{{{school['institution']}}}"
                f"{{{start_date + ' -- ' + end_date}}}{{}}")

        if index < len(configs.resume['education']) - 1:
            result.append('\n\\divider\n')

    result.append("\n\\medskip\n")


def volunteer():
    result.append(f"\\cvsection{{{configs.strings['volunteer']}}}")

    for index, job in enumerate(configs.resume['volunteer']):
        start_date = parse_date(job['startDate'])
        start_date = start_date.strftime("%Y").title() if start_date else \
            job['startDate']

        end_date = parse_date(job['endDate'])
        end_date = end_date.strftime("%Y").title() if end_date else job[
            'endDate']

        if job.get('website', False):
            result.append(
                f"\\cvevent{{\\href{{{job['website']}}}"
                f"{{{job['position']}}}}}"
                f"{{{job['organization']}}}{{"
                f"{start_date + ' -- ' + end_date}}}"
                f"{{{job['location']}}}")
        else:
            result.append(
                f"\\cvevent{{{job['position']}}}"
                f"{{{job['organization']}}}{{"
                f"{start_date + ' -- ' + end_date}}}"
                f"{{{job['location']}}}")

        result.append(replace_html(job['summary']))

        if index < len(configs.resume['volunteer']) - 1:
            result.append('\n\\divider\n')

    result.append("\n\\medskip\n")


def language():
    result.append(f"\\cvsection{{{configs.strings['language']}}}")

    for index, lang in enumerate(configs.resume['languages']):
        result.append(
            f"\\cvskill{{{lang['name']}}}{{"
            f"{lang['level'] + 1 if lang['level'] > 1 else lang['level']}}}")

        if index < len(configs.resume['languages']) - 1:
            result.append('\n\\divider\n')

    result.append("\n\\medskip\n")


def soft_skills():
    result.append(f"\\cvsection{{{configs.strings['soft-skills']}}}")

    result.append("\\begin{itemize}")

    for skill in configs.resume['other_skills']:
        result.append(f"\\item {{{skill['name']}}}")

    result.append("\\end{itemize}")

    result.append("\n\\medskip\n")


def interests():
    result.append(f"\\cvsection{{{configs.strings['interests']}}}")

    for interest in configs.resume['interests']:
        result.append(f"\\cvtag {{{interest['name'].title()}}}")

    result.append("\n\\medskip\n")


def awards():
    result.append(f"\\cvsection{{{configs.strings['awards']}}}")

    for index, award in enumerate(configs.resume['awards']):
        result.append(
            f"\\cvevent{{{award['title']}}}"
            f"{{{award['awarder']}}}{{"
            f"{award['date']}}}{{}}")

        result.append(replace_html(award['summary']))

        if index < len(configs.resume['awards']) - 1:
            result.append('\n\\divider\n')

    result.append("\n\\medskip\n")


def builder():
    start_doc()
    build_header()

    for section in configs.left_composition:
        if section == "new-page":
            new_page()
        elif section == "work":
            work()
        elif section == "technical-skills":
            technical_skills()
        elif section == "certificates":
            certificates()
        elif section == "education":
            education()
        elif section == "volunteer":
            volunteer()
        elif section == "languages":
            language()
        elif section == "soft-skills":
            soft_skills()
        elif section == "interests":
            interests()
        elif section == "awards":
            awards()

    switch()

    for section in configs.right_composition:
        if section == "new-page":
            new_page()
        elif section == "work":
            work()
        elif section == "technical-skills":
            technical_skills()
        elif section == "certificates":
            certificates()
        elif section == "education":
            education()
        elif section == "volunteer":
            volunteer()
        elif section == "languages":
            language()
        elif section == "soft-skills":
            soft_skills()
        elif section == "interests":
            interests()
        elif section == "awards":
            awards()

    end()


if __name__ == '__main__':
    # Try to get option config path from args
    # set to config.yaml if none present
    try:
        config_path = sys.argv[1]
    except IndexError:
        config_path = "config.yaml"

    # load configurations on a global variable
    configs = Configs(config_path)
    result = []

    builder()

    result_path = Path(__file__).parent / f"./{configs.language}/main.tex"
    with result_path.open(mode='w', encoding='utf-8') as f:
        f.write('\n'.join(result))
