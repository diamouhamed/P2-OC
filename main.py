""" Utilisez les bases de Python pour l'analyse de marché - Use Python basics for market analysis |           OPENCLASSROMS

Système en version bêta pour suivre les prix des livres chez Books to Scrape, un revendeur de livres en ligne. En pratique il s'agit simplement d'une application exécutable à la demande visant à récupérer les informations {"title", "upc", "price_including_tax", "price_excluding_tax", "availability", "review_rating", "category", "product_description", "image_url", "book_url", "file_image"} ainsi que les images des livres au moment de son exécution. """

import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from slugify import slugify
import time
from tqdm import tqdm

DATA_IMG_DIR = "book_data/IMAGES/"
time.sleep(0.01)
    
def get_categories(url):
    """return liste [noms et liens de chaque catégorie]"""
    print(f" ---- strat processing website {url} ----")
    categories = [] 
    #Extraction de la page.
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    #Boucle For pour la récupération du nom et du lien de la catégorie parcourue
    for ultag in soup.find_all('ul', class_='nav nav-list'):
        for litag in ultag.find_all('li'):    
            a = litag.find('a')
            #Lien catégories/
            link = a['href']
            link = url + link
            #Nom catégories/
            category = a.text
            name = slugify(category)
            #Création d'un dictionnaire contenant le nom et le lien de la catégorie parcourue
            categs_dict = {"name" : name, "link" : link}
            categories.append(categs_dict)
    
    del categories[0] #Supression du premier élément de la liste [Books]
    return categories #Liste contenant les noms et liens de chaque catégories

def get_books_urls(category_url):
    """return les urls des livres d'une catégorie"""
    url_category = category_url
    books_url = []
    
    #Boucle While pour parcourir l'url de chaque catégorie
    while True:
        response = requests.get(url_category)
        soup = BeautifulSoup(response.content, "html.parser")
        
        #Boucle For pour parcourir tous les livres d'une catégorie       
        h3s = soup.find_all("h3")
        for h3 in h3s:
            a = h3.find('a')
            link = a['href']
            books_url.append(category_url.replace("/category/books","") + link)
            
        #Pagination 
        next_page_element = soup.select_one('li.next > a')
        if next_page_element:
            next_page_url = next_page_element.get('href')
            url_category = category_url.replace("index.html", next_page_url)
            print(f"processing {next_page_url.replace('.html', '')}")
        else:
            break
        
    return books_url

def get_book_data(url):
    """return un dictionnaire contenant les informations d'un livre"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    book_url = url #Récupération Product Page
    
    title = soup.find("h1").text #Récupération Title
    
    upc = soup.find('th', string='UPC').find_next_sibling('td').string #Récupération UPC
    
    price_including_tax = soup.find("th", text="Price (incl. tax)").find_next_sibling("td").string #Récupération Price Including Tax
    
    price_excluding_tax = soup.find("th", text="Price (excl. tax)").find_next_sibling("td").string #Récupération Price Encluding Tax

    availability = soup.select('p.availability.instock')
    if availability:
        availability = availability[0].text
        availability = availability.replace('In stock (', '')
        availability = availability.replace(' available)', '')
        availability = int(availability)
    else:
        availability = 0 #Récupération Availability
    
    review_rating = soup.find('p', {"class": "star-rating"})
    if review_rating.has_attr('class'):
        review_rating = review_rating["class"][1]
        if review_rating == "One":
            review_rating = 1
        elif review_rating == "Two":
            review_rating = 2
        elif review_rating == "Three":
            review_rating = 3
        elif review_rating == "Four":
            review_rating = 4
        elif review_rating == "Five":
            review_rating = 5
        else:
            review_rating = 0
    else:
        review_rating = 0 #Récupération Review Rating
    
    category = soup.find("li").find_next_sibling("li").find_next_sibling("li").text.strip() #Récupération Category
    
    image_url = soup.find("div", {"id": "product_gallery"})
    image_url = "http://books.toscrape.com/" + soup.find('img')["src"] #Récupération Image Url

    product_description = soup.find("div", id="product_description")
    if product_description:
        product_description = soup.find("div", id="product_description").find_next_sibling("p").text #Récupération Product Description
    
    file_image = f"{DATA_IMG_DIR}{slugify(category)}/{slugify(title)}.jpeg"  #Récupération Chemin d'accés image
    
    #Creation d'un dictionnaire avec toutes les informations des livres    
    book_data = {"title": title,"upc": upc, "price_including_tax": price_including_tax, "price_excluding_tax": price_excluding_tax,"availability": availability, "review_rating": review_rating, "category": category, "product_description": product_description,"image_url": image_url, "book_url": book_url, "file_image": file_image} 
    
    return book_data #dictionnaire avec toutes les informations des livres

def writting_csv_data(books_data):
    """écriture du fichier csv"""
    category_name = books_data[0].get("category")
    DATA_CSV_DIR = "book_data/CSV"
    Path(DATA_CSV_DIR).mkdir(parents=True, exist_ok=True)

    keys = books_data[0].keys()
    with open(f"{DATA_CSV_DIR}/{category_name}.csv", 'w', newline='', encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(books_data)

def save_image(img_url, file_img):
    """sauvegarde des images"""  
    response = requests.get(img_url)
        
    with open(file_img, 'wb') as file:
        file.write(response.content)
    
def main():
    """Fonction principale"""
    url = "https://books.toscrape.com/"
    categories = get_categories(url)

    for category in categories:
        print(f"Processing category {category['name'].upper()}")
        books_urls_category = get_books_urls(category["link"])
        print(f"Donwload {category['name'].upper()}'S informations to csv in book_data")

        books_data = []
        for book_url in tqdm(books_urls_category):
            book_data = get_book_data(book_url)
            books_data.append(book_data)

        writting_csv_data(books_data)
        
        Path(f"{DATA_IMG_DIR}{category['name']}").mkdir(parents=True, exist_ok=True)
        print(f"Download {category['name'].upper()}'S images in book_data ")
        for book in tqdm(books_data):
            save_image(book["image_url"], book["file_image"])
            
    return

if __name__ == '__main__':
    main()
    
"""
Merci d'avoir pris le temps de me lire :)
Toute contribution est la bienvenue.

@DiaMouhamed
@OlivierMajchrzak
"""