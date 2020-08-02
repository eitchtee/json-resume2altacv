import yaml
import sys
import json
import datetime
import locale


class Configs:
    def __init__(self, path):
        self.config_path = path

        with open(path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        self.json_resume_path = data["json_resume_path"]
        self.colors = data["colors"]
        self.left_composition = data["composition"]["first-column"]
        self.right_composition = data["composition"]["second-column"]
        self.name = data["name"] if data["name"] else None
        self.strings = data['strings']

        self.language = data["language"]
        self.change_lang()

        self.resume = self.load_json()

    def load_json(self):
        with open(self.json_resume_path, encoding="utf-8") as f:
            return json.load(f)

    def change_lang(self):
        if self.language == 'en':
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        elif self.language == 'pt':
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
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
    result.append(f"  \\homepage{{{configs.resume['basics']['website'].replace('https://', '')}}}")

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


def work():
    result.append(f"\\cvsection{{{configs.strings['work']}}}")

    for index, work in enumerate(configs.resume['work']):
        start_date = parse_date(work['startDate'])
        start_date = start_date.strftime("%B %Y").title() if start_date else work['startDate']

        end_date = parse_date(work['endDate'])
        end_date = end_date.strftime("%B %Y").title() if end_date else work['endDate']

        result.append(f"\\cvevent{{{work['position']}}}{{{work['company']}}}{{{start_date + ' -- ' + end_date}}}{{}}")
        result.append(replace_html(work["summary"])) if work['summary'] else None

        if work['highlights']:
            result.append("\\begin{itemize}")
            for highlight in work['highlights']:
                result.append("\\item " + highlight)
            result.append('\\end{itemize}')

        if index < len(configs.resume['work']) - 1:
            result.append('\n\\divider\n')


def builder():
    start_doc()
    build_header()

    for section in configs.left_composition:
        if section == "new-page":
            new_page()
        elif section == "work":
            work()
        elif section == "technical-skills":
            pass
        elif section == "certificates":
            pass
        elif section == "education":
            pass
        elif section == "volunteer":
            pass
        elif section == "languages":
            pass
        elif section == "soft-skills":
            pass
        elif section == "awards":
            pass

    switch()

    for section in configs.right_composition:
        pass


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
    print('\n'.join(result))
