from urllib import response
import requests
from bs4 import BeautifulSoup
import pandas as pd

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
    
    del categories[0]
    return categories

def get_books_urls(category_url):
    """return les urls des livres d'une catégorie"""
    books_url = []
    response = requests.get(category_url)
    soup = BeautifulSoup(response.content, "html.parser")
    print(soup)
    return books_url

def get_book_data(book_url):
    """return un dictionnaire contenant les informations d'un livre"""
    
    
    

def main():
    url = "https://books.toscrape.com/"

    categories = get_categories(url)
    
    for category in categories:
        books_urls = get_books_urls(category["link"])
        print(books_urls)
        
        books_data = []
        for book_url in books_urls:
            book_data = get_book_data(book_url)
            books_data.append(book_data)
        #fonction de sauvegarde csv save data = books data.
        #recuperer des images.
        return
        
if __name__ == '__main__':
    main()