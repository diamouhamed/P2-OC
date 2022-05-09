import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from slugify import slugify

def get_categories(url):
    """return categories names & links"""
    print(f"traitement du site {url}")
    categories = []
    #Extraction of page.
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
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
            #création dictionnaire contenant name et link des catégories
            categs_dict = {"name" : name, "link" : link}
            categories.append(categs_dict)
    #Supreession Ligne 1
    del categories[0]
    return categories

def get_books_urls(category_url):
    """return les urls des livres d'une catégorie"""
    print(f"traitement url {category_url}")
    url_category = category_url
    books_url = []
    while True:
        response = requests.get(url_category)
        soup = BeautifulSoup(response.content, "html.parser")
        #Find all page in each category.
        h3s = soup.find_all("h3")
        for h3 in h3s:
            a = h3.find('a')
            link = a['href']
            books_url.append(category_url.replace("/category/books","") + link)
        #Find the next page to scrape in the pagination.
        print(f"traitement pagination {url_category}")
        next_page_element = soup.select_one('li.next > a')
        
        if next_page_element:
            next_page_url = next_page_element.get('href')
            url_category = category_url.replace("index.html", next_page_url)
        else:
            break 
    return books_url

def get_book_data(url):
    """return un dictionnaire contenant les informations d'un livre"""

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    #Récupération Product Page
    book_url = url
    #Récupération Title
    title = soup.find("h1").text
    #Récupération UPC
    upc = soup.find('th', string='UPC').find_next_sibling('td').string
    #Récupération Price Including Tax
    price_including_tax = soup.find("th", text="Price (incl. tax)").find_next_sibling("td").string
    #Récupération Price Encluding Tax
    price_excluding_tax = soup.find("th", text="Price (excl. tax)").find_next_sibling("td").string
    #Récupération Availability
    availability = soup.select('p.availability.instock')
    if availability:
        availability = availability[0].text
        availability = availability.replace('In stock (', '')
        availability = availability.replace(' available)', '')
        availability = int(availability)
    else:
        availability = 0 
    #Récupération Review Rating
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
        review_rating = 0
    #Récupération Category
    category = soup.find("li").find_next_sibling("li").find_next_sibling("li").text.strip()
    #Récupération Image Url
    image_url = soup.find("div", {"id": "product_gallery"})
    image_url = "http://books.toscrape.com/" + soup.find('img')["src"]
    #Récupération Product Description
    product_description = soup.find("div", id="product_description")
    if product_description:
        product_description = soup.find("div", id="product_description").find_next_sibling("p").text
    #Ajout du nom du fichier image (avec chemin) dans le csv.
    file_image = f"book_data/image/{category}/{slugify(title)}/jpeg"
    #Creation d'un dictionnaire avec toutes les informations des livres    
    book_data = {"title": title,"upc": upc, "price_including_tax": price_including_tax, "price_excluding_tax": price_excluding_tax,"availability": availability, "review_rating": review_rating, "category": category, "product_description": product_description,"image_url": image_url, "book_url": book_url, "file_image": file_image} 
    
    return book_data 

def writting_csv_data(books_data):
    print("ajout au fichier csv")
    
    category_name = books_data[0].get("category")
    DATA_CSV_DIR = "book_data/csv"
    Path(DATA_CSV_DIR).mkdir(parents=True, exist_ok=True)
    
    keys = books_data[0].keys()
    with open(f"{DATA_CSV_DIR}/{category_name}.csv", 'w', newline='', encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(books_data)

def save_img(img_url):
    DATA_IMG_DIR = "book_data/img"
    Path(DATA_IMG_DIR).mkdir(parents=True, exist_ok=True)
    
    response = requests.get(img_url)
    with open(f"{DATA_IMG_DIR}/{img_url}.csv", 'r', newline='', encoding="utf-8") as output_file:
        img_url.save('sauvegarde/png_version.png', 'png')
     
def main():
    """Fonction principale"""
    url = "https://books.toscrape.com/"
    categories = get_categories(url)
    
    loop = 0
    for category in categories:
        #print("traitement liens catégories")
        books_urls_category = get_books_urls(category["link"])
        
        books_data = []
        for book_url in books_urls_category:
            book_data = get_book_data(book_url)
            books_data.append(book_data)
        
        writting_csv_data(books_data)
        
        loop += 1 
        if loop > 1:
            return

if __name__ == '__main__':
    main()