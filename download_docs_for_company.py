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

    for document_type in soup.find_all('type'):
        doc_type_list.append(document_type.string)

    # delete this later
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

    return doc_list, doc_name_list, doc_type_list

def save_in_directory(cik, doc_list, doc_name_list, doc_type_list):
    '''
    this saves the documents their correct directory. For example, TSlA/10-k/filename
    '''

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

        print(doc_type, doc_name, base_url)


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

def grab_filings(cik, tickr=""):
    '''
    goes through every page in online listing for documents
    saves all documents
    '''
    page = 0
    num_doc_on_page = 100

    while(num_doc_on_page == 100):
        base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + str(cik) + "&type=&dateb=&owner=&start=" + str(page*100) + "&count=100&output=xml"
        r = requests.get(base_url)
        data = r.text

        # get doc list data
        doc_list, doc_name_list, doc_type_list = create_document_list(data)
        num_doc_on_page = len(doc_list)

        make_directory(cik, doc_type_list)
        save_in_directory(cik, doc_list, doc_name_list, doc_type_list)

        page += 1

        print("Finished page " + str(page))
        print("Number of docs found on page: " + str(num_doc_on_page))
        print("-------------------------------------------------")

    print ("Downloaded all files for CIK: " + str(cik))


grab_filings(1318605, "TSLA")