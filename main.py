import requests
from bs4 import BeautifulSoup

def get_categories(url):
    """return categories names & links"""
    categories = []

    #Extraction of page.
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    #print(soup)

    #Récupérer les liens et noms des catégories.
    for ultag in soup.find_all('ul', class_='nav nav-list'):
        for litag in ultag.find_all('li'):    
            a = litag.find('a')
            #Liens catégories/
            link = a['href']
            link = url + link
            #Noms catégories/
            category = a.text
            name = (category.replace("\n","").replace(" ",""))
            
            categs_dict = {"name" : name, "link" : link}
            categories.append(categs_dict)
            
    return categories
 
def main():
    url = "https://books.toscrape.com/"
    categories = get_categories(url)
        
    for category in categories:
        print(category)
    
if __name__ == '__main__':
    main()
    
