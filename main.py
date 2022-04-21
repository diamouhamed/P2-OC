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
    
    del categories[0]
    return categories

def get_books_urls(category_url):
    """return les urls des livres d'une catégorie"""
    books_url = []
    
    response = requests.get(category_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    if response.ok:
        h3s = soup.find_all("h3")
        for h3 in h3s:
            a = h3.find('a')
            link = a['href']
            books_url.append(category_url.replace("/category/books","") + link)
    
    return(books_url)

def get_book_data(url):
    """return un dictionnaire contenant les informations d'un livre"""

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    title = soup.find("h1").text
    
    price_including_tax = soup.find("th", text="Price (incl. tax)").find_next_sibling("td").string
    
    price_excluding_tax = soup.find("th", text="Price (excl. tax)").find_next_sibling("td").string
    
    availability = soup.select('p.availability.instock')
    if availability:
        availability = availability[0].text
        availability = availability.replace('In stock (', '')
        availability = availability.replace(' available)', '')
        availability = int(availability)
    else:
        availability = 0 
    
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

    category = soup.find("li").find_next_sibling("li").find_next_sibling("li").text.strip()
    
    product_description = soup.find("div", id="product_description")
    if product_description:
        product_description = soup.find("div", id="product_description").find_next_sibling("p").text
        
    book_data = {"title": title,"price_including_tax": price_including_tax, "price_excluding_tax": price_excluding_tax,"availability": availability, "review_rating": review_rating, "category":category, "product_description": product_description} 
    
    return book_data

def main():
    url = "https://books.toscrape.com/"

    categories = get_categories(url)
    
    for category in categories:
        books_urls_category = get_books_urls(category["link"])
        #print(books_urls_category)
        
        books_data = []
        for book_url in books_urls_category:
            book_data = get_book_data(book_url)
            books_data.append(book_data)
            print(books_data)
        return
    
if __name__ == '__main__':
    main()
