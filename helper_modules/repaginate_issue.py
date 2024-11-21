import os
import glob
from pypdf import PdfReader
from pubssg import update_json
import pubssg
import json
from main import convert2pdf

def repaginate_issue():
    pdf_directory = "./static/PDF"
    json_directory = "./json"
    html_directory = "./html"

    page_number_first = 5
    page_number_last = 5
    page_length = 1

    pdf_files = [filename for filename in os.listdir(pdf_directory) if filename.endswith(".pdf")]
    pdf_files.sort()

    for filename in pdf_files:
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_directory, filename)
            with open(filepath, "rb") as file:
                pdf = PdfReader(file)
                page_count = len(pdf.pages) -2 # cover pages are not counted
                print(f"{filename} has {page_count} pages")
                print(f"page_number_first: {page_number_first}")
                page_number_last = page_number_first + page_count - 1
                print(f"page_number_last: {page_number_last}")
                page_range = f"{page_number_first}-{page_number_last}"
                print(page_range)


                file_stem = os.path.splitext(filename)[0]
                json_file = glob.glob(os.path.join(json_directory, file_stem + ".*"))
                if json_file:
                    # update the appropriate json fields in json_file[0]
                    print(f"Matching JSON file: {json_file[0]}")
                    update_json(json_file[0], start_page=page_number_first, pages=page_range)

                if page_number_last % 2 == 0:
                    page_number_first = page_number_last + 1
                else:
                    page_number_first = page_number_last + 2
repaginate_issue()

