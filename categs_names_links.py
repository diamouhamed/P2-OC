import requests
from bs4 import BeautifulSoup

#liste: liens des catégories.
categs_links = []
#liste: noms des catégories.
categs_names = []

#Extraction de la page.
url = "https://books.toscrape.com/"
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
        
print(categs_links)
print(categs_names)