from types import NoneType
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError,
)
from pdf2image import convert_from_path, convert_from_bytes
from dataclasses import dataclass
from typing import List
import os
import json
from json import JSONEncoder
import shutil
import pathlib
from bs4 import BeautifulSoup as bs
from cssutils import parseStyle
import os

# utility functions

def update_json(the_file, **kwargs):
    with open(the_file) as f:
        the_json = json.load(f)
    for k, v in kwargs.items():
        the_json[k] = v
    with open(the_file, 'w') as f:
        json.dump(the_json, f, indent=2)


def populate_list(this_pattern, this_path):
    generated_list = list()
    file_directory = pathlib.Path(this_path)
    file_pattern = this_pattern

    for the_file in file_directory.glob(file_pattern):
        generated_list.append(os.path.basename(the_file))

    generated_list.sort()

    return (generated_list)


def replace_string(the_file_in, the_file_out, search_text, replace_text):
    with open(the_file_in, 'r+') as f:
        # read file
        file_source = f.read()
        replace_string = file_source.replace(search_text, replace_text)
        # save output
    with open(the_file_out, "w") as f:
        print(replace_string, file=f)

# subclass JSONEncoder (the subclass is to be used for serializing composite classes by returning the __dict__)

class CompClassEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


@dataclass
class Author:
    last: str = ''
    middle: str = ''
    first: str = ''
    email: str = ''
    orcid: str = ''
    affiliation: str = ''
    bio: str = ''
    bio_fr: str = ''
    is_editor: bool = False
    is_author: bool = True
    is_copyeditor: bool = False
    is_copyeditor_fr: bool = False

    def get_full_name(self):
        return self.first + ' ' + self.last

    def get_full_name_reverse(self):
        return self.last + ', ' + self.first

    # make a property
    full_name = property(get_full_name)

    full_name_reverse = property(get_full_name_reverse)

    # the str representation for printing:
    def __str__(self) -> str:
        return (self.first + ' ' + self.last)

@dataclass
class Article:
    fileidentstr: str = ''
    title: str = ''
    title_fr: str = ''
    abstract: str = ''
    abstract_fr: str = ''
    short_title: str = ''
    short_author: str = ''
    keywords: str = ''
    keywords_fr: str = ''
    pages: str = ''
    start_page: str = ''
    number_in_issue: str = ''
    doi: str = ''
    ojs_id: str = ''
    submission_id: str = ''
    zot_id: str = ''
    coins: str = ''
    contributors = List[Author]

    #  allow loading a dictionary into the class instances to initialize it
    # def __init__(self, dictionary):
    #     self.__dict__.update(dictionary)

    def __str__(self):
        # returns the object description when printing, should be the MLA quote
        # TODO: use the function that returns MLA formatted entry
        return f"article title: {self.title}"


    def save_as_json(self):
        with open(f'json/{self.fileidentstr}.json', 'w') as f:
            print(json.dumps(self, indent=2,
                             cls=CompClassEncoder), file=f)

    def update_html_from_json(self):
# ! the issue here is that raw html is escaped in BS4, so the html tags are not rendered
        the_html_file = 'html/' + self.fileidentstr + '.html'
        soup = bs(open(the_html_file, encoding="utf8"), "html.parser")
        # the BS4 methods
        the_html_file_abstract = soup.find("div", {"id": "abstract"})
        if the_html_file_abstract is not None:
            the_html_file_abstract.string = self.abstract
            # one could try here: the_html_file_abstract.string = bs(self.abstract, "html.parser")
        the_html_file_abstract_fr = soup.find("div", {"id": "abstract_fr"})
        if the_html_file_abstract_fr is not None:
            the_html_file_abstract_fr.string = self.abstract_fr
        the_html_file_short_title = soup.find(
            "span", {"id": "short_title"})
        the_short_title = self.short_title
        the_html_file_short_title.string = self.short_title
        the_html_file_short_author = soup.find(
            "span", {"id": "short_author"})
        the_html_file_short_author.string = self.short_author

        style = parseStyle(soup.find('h1')['style'])
        style['counter-reset'] = f'page {self.start_page}'
        soup('h1')[0]['style'] = style.cssText

        with open(the_html_file, "w") as f:
            print(soup, file=f)

    def convert_html_to_pdf_plus_cover(self):
        if os.path.isfile(f"html-covers/{self.fileidentstr}-cover.html"):
            my_prince_command = f"prince html-covers/{self.fileidentstr}-cover.html html/{self.fileidentstr}.html -o PDF-complete/{self.fileidentstr}.pdf"
            os.system(my_prince_command)
        else:
            print("No cover page for this file exists in the directory html-covers")


@dataclass
class Issue:
    cover_image: str = ''
    doi: str = ''
    internal_id: str = ''
    description: str = ''
    description_fr: str = ''
    issue_title: str = ''
    issue_title_fr: str = ''
    publication_date: str = ''
    vol: str = ''
    issue: str = ''
    year: str = ''
    image_credit: str = ''
    ojs_id: str = ''
    ojs_identification: str = ''
    ojs_publishedUrl: str = ''
    editors = List[Author]
    authors = List[Author]

    def get_contributors(self):
        the_author_list = list()
        the_author_list_reversed = list()
        files = [i for i in os.listdir("json") if (i.endswith("json"))]
        for file in files:
            with open("json/" + file) as json_file:
                json_data = json.load(json_file)
            authors = json_data["contributors"]
            for author in authors:
                if author['last'] != "Contributors":
                    the_author_list.append(
                        author['last'] + ', ' + author['first'])
        the_author_list = list(set(the_author_list))
        # the_author_list.sort(key=lambda x: x.split(" ")[-1])
        the_author_list.sort()
        for author in the_author_list:
            author_reversed = author.split(
                ', ')[-1] + ' ' + author.split(', ')[0]
            the_author_list_reversed.append(author_reversed)
        return the_author_list_reversed

    def generate_issue_cover(self):
        with open("issue.json") as issue_file:
            issue_data = json.load(issue_file)
        self.vol = issue_data["vol"]
        self.issue = issue_data["issue"]
        self.year = issue_data["year"]
        self.publication_date = issue_data["publication_date"]
        self.issue_title = issue_data["issue_title"]
        self.image_credit = issue_data["image_credit"]
        self.cover_image = issue_data["cover_image"]
        self.issue_editors = issue_data["editors"]
        self.doi = issue_data["doi"]

        the_editors = ""

        for editor in issue_data['editors']:
            the_editors += editor['first'] + " " + editor['last'] + ', '

        the_editors = "".join(the_editors[:-2])

        # open the front page template here
        soup = bs(open("00a-front-page.html", encoding="utf8"), "html.parser")

        the_new_title = soup.find("title")
        the_new_issue_title = soup.find("div", {"id": "issue-title"})
        the_new_editors = soup.find("div", {"id": "issue-editor"})
        the_new_issue = soup.find("div", {"id": "issue"})
        the_new_contributors = soup.find("div", {"id": "contributorlist"})

        the_new_title.string = self.issue_title  # in the head section
        the_new_issue_title.string = self.issue_title
        # todo: check whether singular or plural
        the_new_editors.string = f"Guest Editors: {the_editors}"
        the_new_issue.string = f"Issue {self.vol}-{self.issue}, {str(self.year)}"
        the_new_contributors.string = ""

        list_of_contributors = self.get_contributors(self)
        # loop to write to the file object with bs4:
        for contributor in list_of_contributors:
            the_new_contributors.append(
                bs("\n<p>" + contributor + "</p>", "html.parser")
            )

        # saves as new file, substituting the existing one
        with open("cover.htm", "w") as f:
            print(soup, file=f)
        os.system('prince cover.htm; open cover.pdf')

        # create a png thumbnail file from the generated PDF
        images = convert_from_path("cover.pdf",
                                   dpi=300, output_folder="static/css/")

        images[0].save("static/css/00a-front-page.png", "PNG")
        # delete *.ppm that is created by the library
        #  todo: replace with pathlib, glob
        # get current directory!
        #  dir_path = os.path.dirname(os.path.realpath(__file__))
        #  directory_path = os.getcwd()
        #  list('/Users/mrln/gitlab/imaginations-14-1/static/css'.glob('*.ppm'))

        directory = 'static/css'
        for filename in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, filename)):
                # Process the file here
                if filename.endswith('.ppm'):
                    print(filename)
                    os.remove(os.path.join('static/css', filename))

        # for the_file in os.listdir('../static/css'):
        #     if the_file.endswith('.ppm'):
        #         os.remove(os.path.join(
        #             '/Users/mr/gitlab/imaginations-14-1/static/css', the_file))

        # delete the file cover.htm
        # file_path = "./cover.htm"
        # if os.path.exists(file_path):
        #     os.remove(file_path)
        # else:
        #     print("File does not exist.")

    def generate_front_matter(self):
        with open("issue.json") as issue_file:
            issue_data = json.load(issue_file)
        self.vol = issue_data["vol"]
        self.issue = issue_data["issue"]
        self.year = issue_data["year"]
        self.publication_date = issue_data["publication_date"]
        self.issue_title = issue_data["issue_title"]
        self.image_credit = issue_data["image_credit"]
        self.cover_image = issue_data["cover_image"]
        self.issue_editors = issue_data["editors"]
        self.doi = issue_data["doi"]
        self.image_credit = issue_data["image_credit"]

        the_editors = ""

        for editor in issue_data['editors']:
            the_editors += editor['first'] + " " + editor['last'] + ', '

        the_editors = "".join(the_editors[:-2])

        # get the toc entries
        '''
        assuming that the file sequence is correct, this renders files INCLUDING json extension:
        files = [i for i in os.listdir('json') if (i.endswith("json"))]
        files.sort()
        '''

        files = [i for i in os.listdir('json') if (i.endswith("json"))]
        files.sort()

        #  ! custom file sequence:
        # files = ['03-ferrao', '01-haque', '04-narayanamoorthy', '02-uddin', '05-ahmed', '06-rogers', '07-contributors']

        toc_html = '<p class="toc-heading">Sommaire/Contents</p>\n'
        for file in files:
            with open(f'json/{file}') as json_file:
                json_data = json.load(json_file)
            toc_title = json_data["title"]
            toc_page = json_data["pages"].split('-')[0]
            the_author_list = []
            for au in (json_data["contributors"]):
                the_author_list.append(au['first'] + ' ' + au['last'])
            toc_author = ", ".join(the_author_list)

            html_file_name = file.split(".json")[0] + ".html"

            # construct the whole entry
            toc_entry = f'<p class="toc-title"><a href=html/{html_file_name}>{toc_title}</a><span class="page-number"> • {toc_page}</span></p><p class="toc-author">{toc_author}</p>\n'

            toc_html += toc_entry

        # ! open the front page template here; the templates should not be in the root folder!
        soup = bs(open('00b-front-matter.htm',
                  encoding="utf8"), "html.parser")

        the_new_title = soup.find("title")
        the_new_issue_title = soup.find("div", {"id": "issue-title"})
        the_new_issue_title_top = soup.find("div", {"id": "issue-title-top"})
        the_new_editors = soup.find("div", {"id": "issue-editor"})
        the_new_guest_editor = soup.find("div", {"id": "guest-editor"})
        the_new_issue = soup.find("div", {"id": "issue"})
        the_new_contributors = soup.find("div", {"id": "contributorList"})
        the_new_doi = soup.find("div", {"id": "doi"})
        the_new_toc = soup.find("div", {"id": "table-of-contents"})
        the_new_image_credit = soup.find("div", {"id": "image-credit"})

# something like this should work:
        the_new_title.string = ''
        the_new_title.append = bs(self.issue_title, "html.parser")
        # replaced: the_new_title.string = self.issue_title  # in the head section
        the_new_issue_title.string = self.issue_title
        the_new_issue_title_top.string = self.issue_title
        # todo: check whether singular or plural
        the_new_editors.string = f"Guest Editors: {the_editors}"
        the_new_guest_editor.string = f"Guest Editors: {the_editors}"
        the_new_issue.string = f"Issue {self.vol}-{self.issue}, {str(self.year)}"
        the_new_image_credit.string = f"{self.image_credit}"

        # the_new_doi.string = f'http://dx.doi.org/{self.doi}'
        the_new_doi.replace_with(
            bs(f'<div id="doi"><a href="http://dx.doi.org/{self.doi}">http://dx.doi.org/{self.doi}</a></div>', 'html.parser'))
        # todo: surrround the doi with a link tag
        the_new_contributors.string = ""

        list_of_contributors = self.get_contributors(self)
        # loop to write to the file object with bs4:
        for contributor in list_of_contributors:
            the_new_contributors.append(
                bs("\n<p>" + contributor + "</p>", "html.parser")
            )
        the_new_toc.replace_with(
            bs(f'<div id="table-of-contents">{toc_html}</div>', 'html.parser'))

        # saves as new file, substituting the existing one
        with open("front_matter.htm", "w") as f:
            print(soup, file=f)

    def generate_whole_issue(self):

        file_list = ""
        # note: The custom order file list in case the files are not in the right sort order in the html directory; otherwise, just loop through the directory like so:
        files = [f for f in os.listdir('html') if (f.endswith("html"))]
        files.sort()

        # files = ["cover.htm", "front_matter.htm", "html/03-ferrao.html", "html/01-haque.html", "html/04-narayanamoorthy.html", "html/02-uddin.html", "html/05-ahmed.html", "html/06-rogers.html", "html/07-contributors.html"]

        for file in files:
            file_list += "html/" + file + " "
        file_list = "cover.htm front_matter.htm " + file_list
        print(file_list)
        os.system("prince " + file_list + " -o imaginations-14-2.pdf; open imaginations-14-2.pdf")
