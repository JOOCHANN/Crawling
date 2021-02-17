import requests as rq
from bs4 import BeautifulSoup, NavigableString, Tag
import re
import json
import numpy as np
import os.path
import time

def get_html(url):
    _html = ""
    resp = rq.get(url)
    if resp.status_code == 200:
        _html = resp.text
        # print("Successfully read URL :", url)
        return _html
    else:
        return 0

def get_numpage(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    area = soup.find("small")

    for index in area:
        total_page = index
        total_page = int(total_page.split(' ')[3])
        break

    return total_page

def get_info(url):
    title = []
    abstract = []
    subjects = []

    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    area = soup.find_all(title="Abstract")

    for index in area:
        _url = index.attrs["href"] 
        _url = 'https://arxiv.org' + _url
        # print(_url)

        sub_html = get_html(_url)
        sub_soup = BeautifulSoup(sub_html, 'html.parser')

        sub_title = sub_soup.head.title
        sub_abstract = sub_soup.find("meta", {"property" : "og:description"})
        sub_subjects = sub_soup.find("span", {"class" : "primary-subject"})

        title.append(sub_title.get_text().split('] ')[1])
        abstract.append(sub_abstract.attrs['content'])
        subjects.append(sub_subjects.get_text())

    return title, abstract, subjects

def check_file_exist(file_path):
    if os.path.isfile(file_path) == False:
        print("{} file does not exist".format(file_path.split("/")[-1]))
        data = {}
        with open(file_path, 'w') as outfile:
            json.dump(data, outfile)
    else:
        print("{} file exists".format(file_path.split("/")[-1]))
    print()

def make_year_jsonlist(file_path, year):
    json_data = {}

    with open(file_path, "r") as json_file:
        json_data = json.load(json_file)
    json_data[year] = []

    with open(file_path, 'w') as outfile:
        json.dump(json_data, outfile)

def save_json(file_path, page, title, abstract, subject):
    json_data = {}

    with open(file_path, "r") as json_file:
        json_data = json.load(json_file)

    for k in range(page, page + per_page):
        json_data[str(i)].append({
            "idx" : k,
            "title" : title[k-page],
            "abstract" : abstract[k-page],
            "subject" : subject[k-page]
        })
    
    with open(file_path, 'w') as outfile:
        json.dump(json_data, outfile)

if __name__ == "__main__":

    base_url = 'https://arxiv.org/list/cs/'
    year = [16, 17, 18, 19, 20] # year
    per_page = 100 # Paper per page

    file_path = './arXiv_Crawling.json'
    check_file_exist(file_path) # Check if the file exists

    for i in year:
        page = 0 # Starting page
        url = base_url + str(i) + '?skip=' + str(page) + '&show=1' # Starting URL
        total_page = get_numpage(url) # Maximum number of pages
        # total_page = 200 # 없애야함
        make_year_jsonlist(file_path, str(i)) # Create a list of years to be saved in jsonfile
        print('-------------year:{}, total_page:{} start-------------'.format(i, total_page))

        while page <= total_page:
            url = base_url + str(i) + '?skip=' + str(page) + '&show=' + str(per_page) # Current page URL
            title, abstract, subject = get_info(url) # Get all paper information(title, abstract, subject) on the current page
            save_json(file_path, page, title, abstract, subject) # Save jsonfile

            print('year:{}, current_page:{:5}\t Progress:{:0.4%}'.format(i, page, page/total_page))
            page = page + per_page # Go to the next page

        print()
        print()
            
            
            
