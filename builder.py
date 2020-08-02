import yaml
import sys
import json


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

        self.resume = self.load_json()

    def load_json(self):
        with open(self.json_resume_path, encoding="utf-8") as f:
            return json.load(f)


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
    \\renewcommand{\familydefault}{\\sfdefault}
\\else
    % If using pdflatex:
    \\usepackage[rm]{roboto}
    \\usepackage[defaultsans]{lato}
    % \\usepackage{sourcesanspro}
    \\renewcommand{\familydefault}{\\sfdefault}
\\fi
""")

    for color in configs.colors:
        result.append(
            f"\\definecolor{{{color}Color}}{{HTML}}{{"
            f"{configs.colors[color]}}}\n")
        result.append(
            f"\\colorlet{{{color}}}{{{configs.colors[color]}}}\n")

    result.append("""\\renewcommand{\\namefont}{\\Huge\\rmfamily\\bfseries}
\\renewcommand{\\personalinfofont}{\\small}
\\renewcommand{\\cvsectionfont}{\\LARGE\\rmfamily\\bfseries}
\\renewcommand{\\cvsubsectionfont}{\\large\\bfseries}

\\renewcommand{\\itemmarker}{{\\small\\textbullet}}
\\renewcommand{\\ratingmarker}{\\faCircle}

\\begin{document}
""")

    print(''.join(result))


def build_header():
    name = configs.name if configs.name else configs.resume['basics']['name']
    email = configs.resume['basics']['email']
    phone = configs.resume['basics']['phone']
    location = configs.resume['basics']['location']['city'] + ', ' + \
               configs.resume['basics']['location']['region'] + \
               ', ' + \
               configs.resume['basics']['location']['countryCode']

    result.append(f"\n\\name{{{name}}}\n")
    result.append("\\photoL{2.5cm}{photo}")

    result.append(f"""\\personalinfo{{%
  \\email{{{email}}}
  \\phone{{{phone}}}
  \\location{{{location}}}""")


def builder():
    start_doc()
    build_header()


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
    print(''.join(result))
