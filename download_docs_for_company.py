import requests
import os
import errno
from bs4 import BeautifulSoup
CURRENT_FOLDER_PATH = os.path.abspath(os.path.dirname(__file__))

def create_document_list(data):
    '''
    this takes the lxml data scrapped and returns three dictionaries with info about files
    '''

    # parse fetched data using beatifulsoup
    soup = BeautifulSoup(data, "lxml")
    # store the link in the list
    link_list = list()

    # List of url to the text documents
    doc_list = list()
    # List of document names
    doc_name_list = list()
    # List of document types
    doc_type_list = list()
    # date filed
    doc_date_list = list()

    for document_type in soup.find_all('type'):
        doc_type_list.append(document_type.string)

    for document_date in soup.find_all('datefiled'):
        doc_date_list.append(document_date.string)

    # #delete this later
    # text_file = open("search.txt", "w")
    # text_file.write(data)
    # text_file.close()

    # If the link is .htm convert it to .html
    for link in soup.find_all('filinghref'):
        url = link.string
        if link.string.split(".")[len(link.string.split("."))-1] == "htm":
            url += "l"
        link_list.append(url)
    link_list_final = link_list

    # Get all the doc
    for k in range(len(link_list_final)):
        required_url = link_list_final[k].replace('-index.html', '')
        txtdoc = required_url + ".txt"
        docname = txtdoc.split("/")[-1]
        doc_list.append(txtdoc)
        doc_name_list.append(docname)

    return doc_list, doc_name_list, doc_type_list, doc_date_list

def save_in_directory(cik, doc_list, doc_name_list, doc_type_list, doc_date_list, docs_json):
    '''
    this saves the documents their correct directory. For example, TSlA/10-k/filename
    '''

    quarter_count = 1
    # loops over each document in list and downloads from online.
    for j in range(len(doc_list)):
        doc_name = doc_name_list[j]
        doc_type = doc_type_list[j]

        base_url = doc_list[j]
        r = requests.get(base_url)
        data = r.text


        path = os.path.join(CURRENT_FOLDER_PATH, str(cik), doc_type, doc_name)

        text_file = open(path, "w")
        text_file.write(data)
        text_file.close()

        # creates a dictionary to store in docs_json
        temp = {}
        temp["path"] = os.path.join(str(cik), doc_type, doc_name)
  
        temp["type"] = doc_type_list[j]

        # adjusts temp to include name and ending date for 10-Ks and 10-Qs
        temp = grab_doc_name(temp)

        temp["date"] = doc_date_list[j]

        docs_json.append(temp)

        # print(docs_json)
        print(doc_type, doc_name, base_url)

    # print(docs_json)
    # exit()
    return docs_json


def make_directory(cik, doc_type_list):
    '''
    makes a directory for each document type
    '''
    for doc_type in doc_type_list:
        # Making the directory to save comapny filings
        path = os.path.join(CURRENT_FOLDER_PATH, str(cik), doc_type)

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

def grab_doc_name(temp):
    doc_type = temp["type"]

    # figures out when the document actually starts
    sec_doc_start = 0

    with open(temp["path"]) as f:
        lines = f.readlines()
    for count, line in enumerate(lines):
        if "SEC-DOCUMENT" in line:
            sec_doc_start = count
            break

    # records information for "Financials" category
    if doc_type in {"10-K", "10-Q", "NT 10-K", "10-K/A"}:
        temp["end_date"] = lines[sec_doc_start + 6].split()[4]

        ending_year = temp["end_date"][:4]
        ending_month = temp["end_date"][4:6]

        if doc_type in {"10-K", "10-K/A"}:
            if doc_type == "10-K":
                temp["name"] = ending_year + "Annual Report"
            if doc_type =="10-K/A":
                temp["name"] = ending_year + "Annual Report, amended"
            if doc_type == "10-K405":
                temp["name"] = temp["name"] = ending_year + "Annual Report, disclosure of delinquent filers"

        if doc_type == "10-Q":
            # TODO
            # # for Q2
            # if ending_month in {12, 01, 02, 03, 04, 05}:
            temp["name"] = "Q1"

        #TODO: FIGURE OUT THE REST ACCORDING
    else:
        temp["name"] = "insert name"

    return temp

def grab_filings(cik, tickr=""):
    '''
    goes through every page in online listing for documents
    saves all documents
    '''
    page = 0
    num_doc_on_page = 100
    docs_json = []

    while(num_doc_on_page == 100):
        base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + str(cik) + "&type=&dateb=&owner=&start=" + str(page*100) + "&count=100&output=xml"
        r = requests.get(base_url)
        data = r.text

        # get doc list data
        doc_list, doc_name_list, doc_type_list, doc_date_list= create_document_list(data)
        num_doc_on_page = len(doc_list)

        # print(len(doc_list), len(doc_name_list), len(doc_type_list), len(doc_date_list))
        # print(doc_date_list)
        # exit()

        make_directory(cik, doc_type_list)
        docs_json = save_in_directory(cik, doc_list, doc_name_list, doc_type_list, doc_date_list, docs_json)

        print(docs_json)

        page += 1

        print("Finished page " + str(page))
        print("Number of docs found on page: " + str(num_doc_on_page))
        print("-------------------------------------------------")

    print ("Downloaded all files for CIK: " + str(cik))
    print("Saving as json now...")

    with open(os.path.join(CURRENT_FOLDER_PATH, "docs.json"), "w") as json_file:
        json_file.write("docs: [")
        for doc_dict in docs_json:
            json_file.write("\n")
            doc_string = str(doc_dict) + ","
            json_file.write(doc_string)

        json_file.write("]")

if __name__ == "__main__":
    grab_filings(1318605, "TSLA")