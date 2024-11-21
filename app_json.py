#  this module handles the json form

import os
import re

from flask import Blueprint, render_template, request, redirect, flash

import json
import pubssg

app_json = Blueprint("app_json", __name__)


# edit article metadata
# todo: could be a method of Article() class
@app_json.route("/jedit", methods=["GET", "POST"])
@app_json.route("/jedit/<json_file>", methods=["GET", "POST"])
def jedit(json_file):
    # the next condition should theoretically never be true, but just in case
    if not os.path.exists(f"json/{json_file}"):
        flash(f"{json_file}not found")

    if request.method == "POST":  # if the save button is clicked, save the form data as json
        form_data = request.form
        contributor_count = 0
        the_contributors = list()
        for key in form_data.keys():
            # find out how many contributors there are
            if key.startswith("last"):
                contributor_count += 1
        # what is returned from form is immutable (tuples), must be converted to dict
        the_title_dict = {k: v for k, v in form_data.items()}
        # loop through contributors, unflatten them into a list of dicts, to be appended to entry
        if contributor_count > 0:
            for i in range(0, contributor_count):
                the_contributors.append(
                    {
                        "last": form_data[f"last{i}"],
                        "middle": form_data[f"middle{i}"],
                        "first": form_data[f"first{i}"],
                        "email": form_data[f"email{i}"],
                        "bio": form_data[f"bio{i}"],
                        "bio_fr": form_data[f"bio_fr{i}"],
                        "orcid": form_data[f"orcid{i}"],
                        "sequence": form_data[f"sequence{i}"],
                        "affiliation": form_data[f"affiliation{i}"],
                    }
                )
                # delete the flattened keys from returned form data
                for key in [
                    f"last{i}",
                    f"middle{i}",
                    f"first{i}",
                    f"email{i}",
                    f"bio{i}",
                    f"bio_fr{i}",
                    f"orcid{i}",
                    f"sequence{i}",
                    f"affiliation{i}",
                ]:
                    del the_title_dict[key]
        # add the list of contributors to the entry
        the_title_dict["contributors"] = the_contributors
        # delete the save button from POST
        del the_title_dict["save"]
        the_fileidentstr = the_title_dict['fileidentstr']

        # create a new instance of the article class with default values
        my_article = pubssg.Article()

        # update my_article with the values of the form if the key exists and is not empty
        for key in the_title_dict.keys():
            if the_title_dict[key] != "" and key in my_article.__dict__:
                my_article.__dict__[key] = the_title_dict[key]
            # add the list of contributors to the entry
            my_article.contributors = the_contributors

        print(my_article.__dict__)

        # create an instance of the article class to save the json file
        # save the article class instance to json file
        my_article.save_as_json()

        # update all the pagenumbers in the json files

        # todo: make sure this works
        # from helper_modules import repaginate_issue
        # repaginate_issue.repaginate_issue()
        flash(f"json/{json_file} saved; article metadata repaginated")

        # if html file exists, update
        if os.path.isfile(f"html/{the_fileidentstr}.html"):
            # flash(f'html/{the_fileidentstr}.html')
            my_article.update_html_from_json()

        # Delete the PDF file if it exists
        # if os.path.isfile(f"static/PDF/{the_fileidentstr}.pdf"):
        #     os.remove(f"static/PDF/{the_fileidentstr}.pdf")
        #     print(f"Deleted {f"static/PDF/{the_fileidentstr}.pdf"}")

        # else:
        #     print(f"{f"static/PDF/{the_fileidentstr}.pdf"} does not exist")

    with open("json/" + json_file) as data_file:
        form_data = json.load(data_file)

    return render_template("jedit.html", data=form_data, json_file=json_file)


# add article author to metadata input form by creating empty author entry
@app_json.route("/add_contributor/<json_file>", methods=["GET", "POST"])
def add_contributor(json_file):
    with open("json/" + json_file) as data_file:
        form_data = json.load(data_file)
        # todo: this should be a class instance (for defaults)
        #  create instance of Author class
        author = pubssg.Author()
        print(author.__dict__)
        form_data['contributors'].append(author.__dict__)

    with open(f"json/{json_file}", "w") as write_file:
        json.dump(form_data, write_file, indent=2)

    return redirect(f'../jedit/{json_file}')


# edit issue metadata
@app_json.route("/issue_edit", methods=["GET", "POST"])
def issue_edit():
    # check whether issue.json exists; if it does not, create it with empty fields/properties

    if not os.path.exists('issue.json'):
        the_issue = pubssg.Issue({})
        the_issue.doi = ''
        the_issue.internal_id = ''
        the_issue.description = ''
        the_issue.description_fr = ''
        the_issue.the_editors = []
        the_issue.issue_title = ''
        the_issue.issue_title_fr = ''
        the_issue.publication_date = ''
        the_issue.vol = ''
        the_issue.issue = ''
        the_issue.year = ''
        the_issue.image_credit = ''
        the_issue.ojs_id = ''
        the_issue.ojs_identification = ''
        the_issue.ojs_publishedUrl = ''

        the_issue_dict = the_issue.__dict__
        with open('issue.json', 'w') as f:
            json.dump(the_issue_dict, f)

    if request.method == 'POST':
        form_data = request.form

        # update my_issue with the values of the form if the key exists and is not empty
        my_issue = pubssg.Issue()
        print(my_issue.__dict__)

        for key in form_data.keys():
            if form_data[key] != "" and key in my_issue.__dict__:
                my_issue.__dict__[key] = form_data[key]
                print(my_issue.__dict__)

        # add the list of editor objects to the entry
        the_editors = list()
        editor_count = 0

        for key in form_data.keys():
            # find out how many contributors there are
            if key.startswith('first'):
                editor_count += 1

        if editor_count > 0:
            for i in range(0, editor_count):
                the_editor = pubssg.Author()
                the_editor.last = form_data[f'last{i}']
                the_editor.first = form_data[f'first{i}']
                the_editor.is_editor = True
                the_editor.is_author = False
                the_editors.append(the_editor.__dict__)

        print(the_editors)

        my_issue.editors = the_editors

        # save the issue object to json file
        with open('issue.json', 'w') as f:
            json.dump(my_issue.__dict__, f)

    #  TODO: the same for copyeditor, French copy editor, but make sure keys in form are not duplicated, eg cp_last instead of last etc.
    with open('issue.json') as data_file:
        form_data = json.load(data_file)
        # todo: update the css here
        issue_string = f"ISSUE {form_data['vol']}-{form_data['issue']}, {form_data['year']}"
    with open('static/css/article_print.css') as f:
        print_css_string = f.read()

    with open('static/css/article_print.css', 'w') as f:
        f.write(re.sub(r"ISSUE\s\d{2}-\d,\s\d{4}",
                       issue_string, print_css_string))

    return render_template('issue_edit.html', data=form_data, json_file='issue.json')


# add issue editor
@app_json.route("/add_editor", methods=["GET", "POST"])
def add_editor():
    the_editor = pubssg.Author()
    the_editor.is_author = False
    the_editor.is_editor = True

    with open('issue.json', 'r') as data_file:
        issue_data = json.load(data_file)

    if 'editors' not in issue_data.keys():
        issue_data['editors'] = []

    issue_data['editors'].append(the_editor.__dict__)

    with open(f'issue.json', 'w') as write_file:
        json.dump(issue_data, write_file, indent=2)

    return redirect('../issue_edit')


#  create empty json objects from word files
@app_json.route("/add_json_files", methods=["GET", "POST"])
def add_json_files():
    files = [(i.split('.')[0] + '.json')
             for i in os.listdir("docx") if (i.endswith("docx"))]
    for file in files:
        if os.path.exists(f'json/{file}'):
            flash(f'json/{file} already exists!')
            continue
        else:
            # pubssg.save_as_json
            the_author = pubssg.Author()
            the_author_list = []
            the_author_list.append(the_author)

            the_article = pubssg.Article()
            the_article.fileidentstr = file.split('.')[0]
            the_article.contributors = the_author_list

            the_article.save_as_json()

    return redirect('/')


# generate contributors' page
@app_json.route("/generate_contributors_page", methods=["GET", "POST"])
def generate_contributors_page():
    the_json_file_list = pubssg.populate_list('*.json', 'json/')
    the_contributor_list_collected = []
    the_contributor_list = []
    the_contributors = ''
    for file in the_json_file_list:
        with open(f'json/{file}') as file:
            the_contributor_dict = json.load(file)
        for contributor in the_contributor_dict['contributors']:
            # create a list of contributor dicts, but not from the contributors' file
            the_contributor_list_collected.append(contributor)
    #  sort the dict by last name
    the_contributor_list_collected_sorted = sorted(
        the_contributor_list_collected, key=lambda d: d['last'])
    # create a file
    for contributor in the_contributor_list_collected_sorted:
        if contributor['last'] == "Contributors":
            the_contributor_list_collected_sorted.remove(contributor)

            # the_contributor_list.append(contributor['bio'])
        the_contributors += (contributor['bio'] + '\n' +
                             '\n::: {lang="fr" class="contributorFrench"}\n\n' + contributor['bio_fr'] + '\n\n:::\n\n')
    # write out the contributor file
    with open('markdown/09-contributors.md', 'w') as f:
        f.write(the_contributors)

    flash('contributors page generated')

    return redirect('/')
