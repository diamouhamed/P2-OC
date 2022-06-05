""" Utilisez les bases de Python pour l'analyse de marché - Use Python basics for market analysis | OPENCLASSROMS

Système en version bêta pour suivre les prix des livres chez Books to Scrape, un revendeur de livres en ligne. En pratique il s'agit simplement d'une application exécutable à la demande visant à récupérer les informations {"title", "upc", "price_including_tax", "price_excluding_tax", "availability", "review_rating", "category", "product_description", "image_url", "book_url", "file_image"} ainsi que les images des livres au moment de son exécution. """

import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from slugify import slugify
from tqdm import tqdm
from sys import exit

DATA_CSV_DIR = "book_data/CSV"
DATA_IMG_DIR = "book_data/IMAGES/"

def get_soup(url):
    """Return a beautiful soup object"""
    response = requests.get(url)                                        
    soup = BeautifulSoup(response.content, "html.parser")

    if not response.ok:
        print("Une erreur est survenue lors de la requête. Réessayez plus tard.")
        exit()
    return soup

def get_categories(url):
    """Return liste [noms et liens de toutes les catégories de livre]"""
    print(f" ---- strat processing website {url} ----")
    
    categories = []
    # Extraction de la page d'accueil.
    soup = get_soup(url)

    # Boucle For pour la récupération des noms et liens des catégories des livres à partir du SideBar.
    for ultag in soup.find_all("ul", class_="nav nav-list"):
        for litag in ultag.find_all("li"):
            a = litag.find("a")
            # Lien catégories/
            link = a["href"]
            link = url + link
            # Nom catégories/
            category = a.text
            name = slugify(category)
            # Création d'un dictionnaire contenant le nom et le lien de toutes les catégories.
            categs_dict = {"name": name, "link": link}
            categories.append(categs_dict)
                
    del categories[0]  # Supression du premier élément de la liste.
    return categories  # Noms et liens de toutes les catégories.

def get_books_urls(category_url):
    """return les urls de tous les livres d'une catégorie"""
    url_category = category_url
    books_url = []

    # Boucle While pour parcourir les urls de tous les livres d'une catégorie
    while True:
        soup = get_soup(url_category)

        # Boucle For pour extraire tous les liens des livres
        h3s = soup.find_all("h3")
        for h3 in h3s:
            a = h3.find("a")
            link = a["href"]
            books_url.append(category_url.replace("/category/books", "") + link)

        # Pagination si existante.
        next_page_element = soup.select_one("li.next > a")
        if next_page_element:
            next_page_url = next_page_element.get("href")
            url_category = category_url.replace("index.html", next_page_url)
            print(f"processing {next_page_url.replace('.html', '')}")
        else:
            break
    return books_url

def get_book_data(url):
    """return un dictionnaire contenant les informations d'un livre"""
    soup = get_soup(url)
    
    # Récupération Product Page
    book_url = url  

    # Récupération Title
    title = soup.find("h1").text  

    # Récupération UPC
    upc = soup.find("th", string="UPC").find_next_sibling("td").string

    # Récupération Price Including Tax
    price_including_tax = soup.find("th", text="Price (incl. tax)").find_next_sibling("td").string

    # Récupération Price Excluding Tax
    price_excluding_tax = soup.find("th", text="Price (excl. tax)").find_next_sibling("td").string
    
    # Récupération Availability
    availability = soup.select("p.availability.instock")
    if availability:
        availability = availability[0].text
        availability = availability.replace("In stock (", "")
        availability = availability.replace(" available)", "")
        availability = int(availability)
    else:
        availability = 0
        
    # Récupération Review Rating
    review_rating = soup.find("p", {"class": "star-rating"})
    if review_rating.has_attr("class"):
        review_rating = review_rating["class"][1]
        review_rating = transform_rating_to_number(review_rating)
    else:
        review_rating = 0
    
    # Récupération Category
    category = soup.find("li").find_next_sibling("li").find_next_sibling("li").text.strip()
    
    # Récupération Image Url
    image_url = soup.find("div", {"id": "product_gallery"})
    image_url = "http://books.toscrape.com/" + soup.find("img")["src"]

    # Récupération Product Description
    product_description = soup.find("div", id="product_description")
    if product_description:
        product_description = soup.find("div", id="product_description").find_next_sibling("p").text
        
    # Récupération Chemin d'accés image
    file_image = f"{DATA_IMG_DIR}{slugify(category)}/{slugify(title)}.jpeg" 

    #Structuration d'un dictionnaire avec toutes les données des livres
    book_data = {
        "title": title,
        "upc": upc,
        "price_including_tax": price_including_tax,
        "price_excluding_tax": price_excluding_tax,
        "availability": availability,
        "review_rating": review_rating,
        "category": category,
        "product_description": product_description,
        "image_url": image_url,
        "book_url": book_url,
        "file_image": file_image,
    }
    return book_data

def transform_rating_to_number(review_rating):
    """Retourne la note transformée en nombre"""
    if review_rating == "One":
        rating_number = 1
    elif review_rating == "Two":
        rating_number = 2
    elif review_rating == "Three":
        rating_number = 3
    elif review_rating == "Four":
        rating_number = 4
    elif review_rating == "Five":
        rating_number = 5
    else:
        rating_number = 0
    return rating_number

def writting_csv_data(books_data):
    """écriture du fichier csv"""
    category_name = books_data[0].get("category")

    Path(DATA_CSV_DIR).mkdir(parents=True, exist_ok=True)

    keys = books_data[0].keys()
    with open (f"{DATA_CSV_DIR}/{category_name}.csv", "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(books_data)

def save_image(img_url, file_img):
    """sauvegarde des images"""
    response = requests.get(img_url)

    with open(file_img, "wb") as file:
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

if __name__ == "__main__":
    main()