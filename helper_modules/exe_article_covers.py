# 1. generates html cover pages from a list of json files
# 2. converts the cover pages to PDF via prince
# 3. puts the generated html's in a folder html-covers/
# 4. puts the generated PDFs in a folder PDF-covers/
# note: this module is loaded by convert2pdf route in main.py
import json
import os
import pubssg
import pathlib
from bs4 import BeautifulSoup as bs

def article_with_cover(the_file):

    if not os.path.exists('html-covers'):
        os.makedirs('html-covers')
        print('Created \'html-covers\' directory')

    if not os.path.exists('static/PDF'):
        os.makedirs('static/PDF')
        print('Created \'PDF\' directory')

    if not os.path.exists('static/PDF-covers'):
        os.makedirs('static/PDF-covers')
        print('Created \'PDF-covers\' directory')
    # get the issue data from json file to insert into each generated file
    with open('issue.json') as issue_file:
        issue_data = json.load(issue_file)
    the_issue = pubssg.Issue
    the_issue.vol = issue_data['vol']
    the_issue.issue = issue_data['issue']
    the_issue.year = issue_data['year']
    the_issue.publication_date = issue_data['publication_date']
    the_issue.issue_title = issue_data['issue_title']
    the_issue.image_credit = issue_data['image_credit']
    the_issue.issue_editors = ''

    for editor in issue_data['editors']:
        editor_full = editor['first'] + ' ' + editor['last'] + ', '
        the_issue.issue_editors += editor_full

    the_editors = ''.join(the_issue.issue_editors[:-2])
    the_cover = ''

    with open(f'json/{the_file}') as json_file:
        json_data = json.load(json_file)
        the_doi = json_data["doi"]  # get the DOI from the dictionary
        # add authors to the citation!
        the_authors = ""
        if len(json_data["contributors"]) > 0:
            the_authors = json_data["contributors"][0]["last"] + \
                ", " + json_data["contributors"][0]["first"]
        if len(json_data["contributors"]) == 1:
            the_authors += '.'
        if len(json_data["contributors"]) == 2:
            the_authors += ", and " + \
                json_data["contributors"][1]["first"] + " " + \
                json_data["contributors"][1]["last"] + "."
        if len(json_data["contributors"]) > 2:
            the_authors += ", et al."

        the_citation = f'“{json_data["title"]}.” <i>Imaginations: Journal of Cross-Cultural Image Studies</i>, vol. {the_issue.vol}, no. {the_issue.issue}, {the_issue.publication_date.split("-")[0]}, pp. {json_data["pages"]}, doi: {json_data["doi"]}.'
        # load individual_cover.html, insert the variables
        soup = bs(open('individual_cover.html',
                  encoding="utf8"), "html.parser")

        the_new_title = soup.find('title')
        the_new_title.string = the_issue.issue_title
        the_new_issue_title = soup.find('span', {'id': 'the_issue_title'})
        the_new_issue_title.string = the_issue.issue_title
        the_new_editors = soup.find('span', {'id': 'the_editors'})
        the_new_editors.string = the_editors
        the_new_authors = soup.find('span', {'id': 'the_authors'})
        the_new_authors.string = the_authors
        the_new_publication_date = soup.find(
            'span', {'id': 'the_publication_date'})
        the_new_publication_date.string = the_issue.publication_date
        the_new_image_credit = soup.find('span', {'id': 'the_image_credit'})
        the_new_image_credit.string = the_issue.image_credit
        the_new_citation = soup.find('span', {'id': 'the_citation'})
        the_new_citation.string = ''
        # note: this prevents escaping of angular brackets etc
        the_new_citation.append(bs(the_citation, 'html.parser'))

        the_new_url = soup.find('a', {'id': 'doi_id'})
        the_new_url.string = ''
        the_new_url.replace_with(
            bs(f'<a href="http://dx.doi.org/{the_doi}">http://dx.doi.org/{the_doi}</a>', 'html.parser'))

        # with open("individual_cover.htm", 'w') as f:
        #     print(soup, file=f)
        cover_file = f'html-covers/{pathlib.Path(the_file).stem}.html'
        # print(cover_file)
        with open(cover_file, "w") as f:
            print("creating html file")
            print(soup, file=f)
        # note: the following line would produce individual pdf cover files
        # pdf_file = f'{pathlib.Path(the_file).stem}-test.pdf'
        # os.system(f'prince {cover_file} -o {pdf_file}')
        my_prince_command = f"prince {cover_file} html/{pathlib.Path(the_file).stem}.html -o static/PDF/{pathlib.Path(the_file).stem}.pdf"
        os.system(my_prince_command)

# note: the function gets imported into main.py to produce individual cover pages; it could also run as a batch like so:
# files = [file for file in os.listdir("json") if file.endswith("json")]
# # read the json files:
# for the_file in files:
#     article_with_cover(the_file)
