import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

category_name = []
dict_from_csv = pd.read_csv('categories_url.csv', header=None, index_col=0, squeeze=True).to_dict()

for i in range(len(category_name)):
    links = []
    url = dict_from_csv.replace("index.html", "page-") + str(1) + ".html" 
    reponse = requests.get(url)
    page = reponse.content
    if reponse.ok:
        for y in range(9):
            url = dict_from_csv[category_name[i]].replace("index.html", "page-") + str(y) + ".html"   
            reponse = requests.get(url)
            page = reponse.content  
            soup = BeautifulSoup(page, "html.parser")

            h3s = soup.find_all("h3")
            for h3 in h3s:
                a = h3.find('a')
                link = a['href']
                links.append(url.replace("page-", "").replace(".html", "").replace(str(y), "") + link)
    else :
        url = dict_from_csv[category_name[i]]
        reponse = requests.get(url)
        page = reponse.content
        soup = BeautifulSoup(page, "html.parser")

        h3s = soup.find_all("h3")
        for h3 in h3s:
            a = h3.find('a')
            link = a['href']
            links.append(url.replace("index.html", "") + link)
            
    print(links)