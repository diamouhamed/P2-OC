import requests
from bs4 import BeautifulSoup
import csv

def categ_name_links(url):
    #liste: liens des catégories.
    categs_links = []
    #liste: noms des catégories.
    categs_names = []

    #Extraction de la page.
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    #print(soup)

    #Récupérer les liens et noms des catégories.
    for ultag in soup.find_all('ul', class_='nav nav-list'):
        for litag in ultag.find_all('li'):    
            a = litag.find('a')
            #Liens catégories/
            link = a['href']
            categs_links.append(url + link)
            #Noms catégories/
            category = a.text
            categs_names.append(category.replace("\n","").replace(" ",""))
    #Suppression 1ére ligne (books)
    del categs_links[0]
    del categs_names[0]

    #Creation fichier CSV avec les noms des catégories + liens des catégories
    en_tete = ['name_of_categs', 'links_of_categs']
    with open('category_books_urls.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(en_tete)
        for category, link in zip(categs_names, categs_links):
            writer.writerow([category, link])
            
def main():
    url = "https://books.toscrape.com/"
    categs = categ_name_links(url)
    
if __name__ == '__main__':
    main()