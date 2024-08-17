from tabulate import tabulate as _tabulate
import re as _regex
import io
import base64
import matplotlib.pyplot as plt

pwd = __file__.replace("report.py", "")
template_file = "template.html"
template_file = f"{pwd}/{template_file}"

def _html_table(obj, showindex="default"):
    obj = _tabulate(
        obj, headers="keys", tablefmt="html", floatfmt=".2f", showindex=showindex
    )
    obj = obj.replace('<table>', '<table style="margin-left: auto; margin-right: auto;">')
    obj = obj.replace(' style="text-align: right;"', ' style="text-align: center;"')
    obj = obj.replace(' style="text-align: left;"', ' style="text-align: center;"')
    obj = obj.replace(' style="text-align: center;"', ' style="text-align: center;"')
    obj = _regex.sub("<td> +", "<td>", obj)
    obj = _regex.sub(" +</td>", "</td>", obj)
    obj = _regex.sub("<th> +", "<th>", obj)
    obj = _regex.sub(" +</th>", "</th>", obj)
    return obj

class HtmlTpl:
    def __init__(self, template_file=template_file):
        with open(template_file, "r") as f:
            self.html = f.read()

    def addTable(self, table, title, showindex="default"):
        table = _html_table(table, showindex)
        self.html = self.html.replace(title, table)

    def addElement(self, figure, title):
        self.html = self.html.replace(title, figure)

    def addFigure(self, buf, title):
        figdata_png = base64.b64encode(buf.read()).decode('utf8')
        html_img = f'<img src="data:image/png;base64,{figdata_png}">'
        self.html = self.html.replace(title, html_img)

    
    def save(self, file):
        with open(file, "w") as f:
            f.write(self.html)

    def __str__(self) -> str:
        return self.html
    
    def __repr__(self) -> str:
        return self.html