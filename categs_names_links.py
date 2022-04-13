import requests
from bs4 import BeautifulSoup

#Extraction de la page.
url = "https://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
print(soup)