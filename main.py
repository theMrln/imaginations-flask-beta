#!/usr/bin/env python3

#  this module handles the main file operations
import pprint
from flask import Flask, render_template, request, redirect, flash

from werkzeug.utils import secure_filename

# from flask_cors import CORS
import json
import os.path
import pathlib
import os
import sys
import shutil
import unidecode
import markdownify
import pubssg
import requests

# the blueprint import
from app_json import app_json

# todo: put in helper_modules
from pubssg import populate_list, replace_string

from helper_modules.exe_article_covers import article_with_cover

# import gunicorn

app = Flask(__name__)
app.secret_key = "9324u23ondq;2o3o4jdmn23;o4nmd2"
app.register_blueprint(app_json)

# the home page
@app.route("/", methods=["GET", "POST"])
def index():
    files = [
        "json/" + os.path.basename(f) for f in pathlib.Path("json/").glob("*.json")
    ]
    the_json_dict = dict()
    the_json_dict_list = list()
    for file in files:
        with open(file) as jfile:
            the_json_dict = json.load(jfile)
        the_json_dict["fileidentstr"] = os.path.basename(file).split(".")[0]
        the_json_dict_list.append(the_json_dict)
    the_json_dict_list.sort(key=lambda item: item.get("fileidentstr"))
    return render_template(
        "index.html",
        the_passed_json_dict_list=the_json_dict_list,
        the_passed_issue_file="issue.json",
    )


# the about page
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/docx2md", methods=["GET", "POST"])
def docx2md():
    return render_template(
        "docx2md.html",
        the_passed_docx_list=populate_list("*.docx", "docx/"),
        the_passed_md_list=populate_list("*.md", "markdown/"),
        )

@app.route("/md2html", methods=["GET", "POST"])
def md2html():
    return render_template(
        "md2html.html",
        the_passed_md_list=populate_list("*.md", "markdown/"),
        the_passed_html_list=populate_list("*.html", "html/"),
        )

@app.route("/html2pdf", methods=["GET", "POST"])
def html2pdf():
    return render_template(
        "html2pdf.html",
        the_passed_html_list=populate_list("*.html", "html/"),
        the_passed_pdf_list=populate_list("*.pdf", "static/PDF/"),
        )

# endpoints for the document conversion scripts
# docx to markdown
@app.route("/convert2md/<the_file>")
def convert2md(the_file):
    the_file_stem = the_file.split(".")[0]
    my_pandoc_command = f"pandoc -f docx -t markdown-smart --markdown-headings=atx --wrap=none --no-highlight --lua-filter=lua/fiximage.lua --lua-filter=lua/clean_word.lua --extract-media=static/media/{the_file_stem}-media docx/{the_file} -o markdown/{the_file_stem}.md"
    if os.path.exists(f"markdown/{the_file_stem}.md"):
        flash(
            f"File markdown/{the_file_stem}.md already exists. Please delete existing file before performing conversion!"
        )
    else:
        os.system(my_pandoc_command)
        flash(f"conversion to markdown/{the_file_stem}.md completed")
    # make sure a json metadata file exists, but don't overwrite an existing one
    if os.path.exists(f"json/{the_file_stem}.json"):
        flash(f"json/{the_file_stem}.json already exists, no metadata file created")

    else:
        the_author = pubssg.Author()
        the_author_list = []
        the_author_list.append(the_author)
        the_article = pubssg.Article({})
        the_article.fileidentstr = the_file_stem
        the_article.contributors = the_author_list

        the_article.save_as_json()

    return redirect("/docx2md")

# markdown to html
@app.route("/convert2html/<the_file>")
def convert2html(the_file):
    the_file_stem = the_file.split(".")[0]

    if not os.path.exists('html'):
        os.makedirs('html')
    # todo: find a better solution for embed resources
    my_pandoc_command = f"pandoc -f markdown -t html --wrap=none --resource-path=.:static --embed-resources --standalone --template=static/pandoc-template/pandoc-templ.html --metadata-file=json/{the_file_stem}.json markdown/{the_file_stem}.md -o html/{the_file_stem}.html"

    if os.path.exists(f"html/{the_file_stem}.html"):
        flash(
            f"File html/{the_file_stem}.html already exists. Please delete existing file before performing conversion!"
        )
    if os.path.exists(f"json/{the_file_stem}.json"):
        os.system(my_pandoc_command)
        replace_string(
            f"html/{the_file_stem}.html", f"html/{the_file_stem}.html", "↩︎", "↲"
        )
        flash(f"Conversion to html/{the_file_stem}.html successful")
    else:
        flash("No corresponding metadata/json file. Please enter metadata")
    return redirect("/md2html")

# html to pdf, with cover pages (import from exe_article_with_cover)

@app.route("/convert2pdf/<the_file>")
def convert2pdf(the_file):

    the_file_stem = the_file.split(".")[0]

    my_prince_command = f"prince the_file -o static/PDF/{the_file_stem}.pdf -s static/css/article.css -s static/css/article_print.css"

    if os.path.exists(f"static/PDF/{the_file_stem}.pdf"):
        flash(
            "PDF File already exists. Please delete existing file before performing conversion!"
        )
    else:
        os.system(my_prince_command)
        flash(f"Conversion to static/PDF/{the_file_stem}.pdf successful")
        # note: article_with_cover() is imported from exe_article_covers.py

        article_with_cover(f"{the_file_stem}.json")
        flash("cover added to article")
    return redirect("/html2pdf")


# endpoint for deleting files
@app.route("/delete/<the_file>")
def delete(the_file):
    if os.path.exists(f"json/{the_file}"):
        os.remove(f"json/{the_file}")
        return redirect("/")
    if os.path.exists(f"markdown/{the_file}"):
        os.remove(f"markdown/{the_file}")
        return redirect("/docx2md")
    if os.path.exists(f"static/PDF/{the_file}"):
        os.remove(f"static/PDF/{the_file}")
        return redirect("/html2pdf")
    if os.path.exists(f"html/{the_file}"):
        os.remove(f"html/{the_file}")
        return redirect("/md2html")


# endpoint for displaying raw json files
@app.route("/show_json/<the_file>", methods=["GET"])
def show_json(the_file):
    if os.path.exists(f"json/{the_file}"):
        with open(f"json/{the_file}") as data_file:
            my_file = json.load(data_file)
    else:
        flash(f"{my_file} not found")


# endpoint for uploading word files
# todo: add a check to see if the file already exists
# todo: move a lot of this to helper modules so that it can be used for other file formats
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "docx"
ALLOWED_EXTENSIONS = {"docx", "doc"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files["file"]
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect("/document_conversion")
        else:
            flash("Invalid file format. Only .docx and .doc files are allowed.")
    return redirect("/document_conversion")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# update issue data from OJS through API
@app.route("/update_from_ojs_id/<the_id>", methods=["GET", "POST"])
def update_from_ojs_id(the_id):
    import requests
    import pubssg
    import json
    from helper_modules import API_TOKEN, CALL_URL


    url = f"{CALL_URL}issues/{the_id}?{API_TOKEN}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    response_json = response.json()

    # create an instance of the Issue class
    the_issue = pubssg.Issue({})

    #  get the data into the issue object
    the_issue.ojs_id = response_json["id"]
    the_issue.doi = response_json["pub-id::doi"]
    the_issue.description = markdownify.markdownify(
        response_json["description"]["en_US"]
    )
    the_issue.description_fr = markdownify.markdownify(
        response_json["description"]["fr_CA"]
    )
    the_issue.issue_title = response_json["title"]["en_US"]
    the_issue.issue_title_fr = response_json["title"]["fr_CA"]
    the_issue.publication_date = response_json["id"]
    the_issue.vol = response_json["volume"]
    the_issue.issue = response_json["number"]
    the_issue.year = response_json["year"]
    the_issue.ojs_identification = response_json["identification"]

    #  dictionary from object
    the_issue_dict = the_issue.__dict__

    # todo: this overwrites any edits already made in the form (such as editors!)
    # rather than writing back to json, it should fill the form data!
    # ? can I pass an object into issue_edit.html?
    # ! alternative: update json
    pubssg.update_json(
        "issue.json",
        doi=the_issue.doi,
        description=the_issue.description,
        description_fr=the_issue.description_fr,
        issue_title=the_issue.issue_title,
        issue_title_fr=the_issue.issue_title_fr,
        vol=the_issue.vol,
        issue=the_issue.issue,
        year=the_issue.year,
        ojs_identification=the_issue.ojs_identification,
    )
    # with open('issue.json', 'w') as f:
    #     json.dump(the_issue_dict, f)

    return redirect("/issue_edit")

# ! this needs a rewrite
@app.route("/update_article_metadata", methods=["GET", "POST"])
def update_article_metadata():

    # ! import the constants from helper_modules
    from helper_modules import API_TOKEN, CALL_URL

    # ! part 1
    # get the submissions for a particular issue
    #  note: the information in submissions is incomplete; it is attached to "publications", hence the need to do this in 2 stages
    # TODO: get this from issue.json!

    with open('./issue.json', 'r') as json_file:
        data = json.load(json_file)
        my_issue_id = data["ojs_id"]

        print(my_issue_id)

    url = f"{CALL_URL}submissions?apiToken={API_TOKEN}&issueIds={my_issue_id}&orderBy=id&orderDirection=ASC"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    response_json = response.json()

    # ! part 2a: align submission and publication ids
    list_of_publication_dicts = []

    # get a list of dicts that contains each of the volume's submission and publication ids
    for item in response_json["items"]:
        publication_dict = {}

        publication_dict["submission_id"] = item["id"]
        publication_dict["publication_id"] = item["publications"][0]["id"]
        publication_dict["fullTitle"] = item["publications"][0]["fullTitle"]["en_US"]

        list_of_publication_dicts.append(publication_dict)

    # ! part 2b: this is where the magic happens: loop through publications and create/modify json metadata files

    article_list = []

    n = 1  # for filenames

    for publication in list_of_publication_dicts:
        article_meta_dict = {}

        url = (
            f"{CALL_URL}submissions/"
            + str(publication["submission_id"])
            + "/publications/"
            + str(publication["publication_id"])
            + f"?apiToken={API_TOKEN}"
        )
        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        response_json = response.json()

        article_meta_dict["title"] = response_json["title"]["en_US"]
        article_meta_dict["title_fr"] = response_json["title"]["fr_CA"]
        article_meta_dict["abstract"] = markdownify.markdownify(
            response_json["abstract"]["en_US"]
        )
        article_meta_dict["abstract_fr"] = markdownify.markdownify(
            response_json["abstract"]["fr_CA"]
        )
        article_meta_dict["keywords"] = response_json["keywords"]["en_US"]
        article_meta_dict["keywords_fr"] = response_json["keywords"]["fr_CA"]
        article_meta_dict["pages"] = response_json["pages"]
        article_meta_dict["doi"] = response_json["pub-id::doi"]
        article_meta_dict["ojs_id"] = response_json["id"]
        article_meta_dict["url_published"] = response_json["urlPublished"]
        article_meta_dict["date_published"] = response_json["datePublished"]
        # loop to get the appropriate contributor information
        the_author_list = []
        for author in response_json["authors"]:
            the_author = {}
            the_author["first"] = author["givenName"]["en_US"]
            the_author["last"] = author["familyName"]["en_US"]
            the_author["email"] = author["email"]
            the_author["orcid"] = author["orcid"]
            the_author["affiliation"] = author["affiliation"]["en_US"]
            the_author_list.append(the_author)

        article_meta_dict["contributors"] = the_author_list

        article_list.append(article_meta_dict)

        # write out the json file here

        file_name = unidecode.unidecode(article_meta_dict["contributors"][0]["last"])
        # eliminate white space in file_name
        file_name = file_name.replace(" ", "_")
        # get position in volume from last digit of DOI
        file_number = str(n)
        if len(file_number) == 1:
            article_meta_dict["fileidentstr"] = (
                "0" + file_number + "-" + file_name.lower().strip()
            )
            my_file = "json/0" + file_number + "-" + file_name.lower().strip() + ".json"
        else:
            article_meta_dict["fileidentstr"] = file_number + "-" + file_name
            my_file = "json/" + file_number + "-" + file_name.lower().strip() + ".json"

        n = n + 1

        # ! update rather than write out if files already exist
        # update json is a utility function defined in pub.ssg
        if os.path.exists(my_file):
            pubssg.update_json(
                my_file,
                title=article_meta_dict["title"],
                title_fr=article_meta_dict["title_fr"],
                abstract=article_meta_dict["abstract"],
                abstract_fr=article_meta_dict["abstract_fr"],
                keywords=article_meta_dict["keywords"],
                keywords_fr=article_meta_dict["keywords_fr"],
                pages=article_meta_dict["pages"],
                doi=article_meta_dict["doi"],
                ojs_id=article_meta_dict["ojs_id"],
                url_published=article_meta_dict["url_published"],
                date_published=article_meta_dict["date_published"],
                contributors=article_meta_dict["contributors"],
            )

        else:  # the json file does not yet exist:
            with open(my_file, "w") as f:
                print(json.dumps(article_meta_dict, indent=2), file=f)

    flash("all article metadata created/updated from OJS")

    return redirect("/issue_edit")


# note: the endpoints for generating cover and front matter from issue.json rely on methods in pubssg module
@app.route("/generate_issue_cover", methods=["GET", "POST"])
def generate_issue_cover():
    from pubssg import Issue

    the_issue = Issue
    the_issue.generate_issue_cover(the_issue)
    flash("cover.pdf created")
    return redirect("/issue_edit")


@app.route("/generate_front_matter", methods=["GET", "POST"])
def generate_front_matter():
    from pubssg import Issue

    the_issue = Issue
    the_issue.generate_issue_cover(the_issue)
    the_issue.generate_front_matter(the_issue)
    flash("front_matter.htm created")
    return redirect("/issue_edit")


@app.route("/generate_whole_issue", methods=["GET", "POST"])
def generate_whole_issue():
    from pubssg import Issue

    the_issue = Issue

    the_issue.generate_issue_cover(the_issue)
    the_issue.generate_front_matter(the_issue)
    the_issue.generate_whole_issue(the_issue)
    flash("issue PDF created")
    return redirect("/issue_edit")


# ! the following needs to be commented out when uploaded to server

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
