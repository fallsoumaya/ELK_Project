from bs4 import BeautifulSoup
import requests
import json

def soup_response(url):
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    return soup

# ---------- Extraction de données --------------------

list_categories_url = "https://openlibrary.org/subjects"
list_books_per_category = "https://openlibrary.org/search?subject="
end_point = "https://openlibrary.org"

# Récupération de la liste des catégories
soup = soup_response(list_categories_url)
subject = soup.find('div', id="subjectsPage")
categories = BeautifulSoup(str(subject), 'html.parser').find_all('li')
categories = [category.get_text() for category in categories][:-9]

# Préparation des URLs pour les livres par catégorie
for i in range(len(categories)):
    categories[i] = f'{list_books_per_category}{categories[i].strip()}&page=1'

books_link_detail_page = []

# Récupération des livres par catégorie
for category in categories:
    soup = soup_response(category)
    attributes = {
        "class": "results",
        "itemprop": "url"
    }
    book_link_detail_page = [f"{end_point}{link['href'].strip()}" for link in soup.find_all('a', attrs=attributes)]
    books_link_detail_page.extend(book_link_detail_page)

# Récupération des informations des livres
data = []
for link in books_link_detail_page:
    soup = soup_response(link)

    # Définition des attributs pour les sélecteurs
    attribute_title = {"class": "work-title", "itemprop": "name"}
    attribute_author = {"itemprop": "author"}
    attribute_genre = {"class": "reviews_value"}
    attribute_annee_publication = {"itemprop": "datePublished"}
    attribute_langue = {"itemprop":"inLanguage"}
    attribute_avg_rate = {"itemprop": "ratingValue"}
    attribute_nbre_rate = {"itemprop": "reviewCount"}

    title = soup.find('h1', attrs=attribute_title).get_text(strip=True) if soup.find('h1', attrs=attribute_title) else "N/A"
    author_tags = soup.find_all('a', attrs=attribute_author)
    authors = [author_tag.get_text(strip=True) for author_tag in author_tags]
    
    description_div = soup.find('div', class_='read-more__content')
    description_p = description_div.find('p') if description_div else None
    description = description_p.get_text(strip=True) if description_p else "N/A"

    genres = [genre.get_text(strip=True) for genre in soup.find_all('span', attrs=attribute_genre)]

    year_of_publication = soup.find('span', attrs=attribute_annee_publication).get_text(strip=True) if soup.find('span', attrs=attribute_annee_publication) else "N/A"
    language = soup.find('span', attrs=attribute_langue).get_text(strip=True) if soup.find('span', attrs=attribute_langue) else "N/A"
    avg_rating = soup.find('span', attrs=attribute_avg_rate).get_text(strip=True) if soup.find('span', attrs=attribute_avg_rate) else "N/A"
    review_count = soup.find('span', attrs=attribute_nbre_rate).get_text(strip=True) if soup.find('span', attrs=attribute_nbre_rate) else "N/A"

    data.append({
        "title": title,
        "authors": authors,
        "description": description,
        "genres": genres,
        "year_of_publication": year_of_publication,
        "language": language,
        "avg_rating": avg_rating,
        "review_count": review_count
    })

# ---------- Transformation de données --------------------

def clean_data(data):
    # Nettoyer les auteurs en supprimant les doublons
    data['authors'] = list(sorted(set(data['authors'])))
    
    # Nettoyer les genres en supprimant les doublons (s'ils existent)
    data['genres'] = list(sorted(set(data['genres'])))
    
    # Remplacer les valeurs "N/A" par None ou par une chaîne vide
    for key in ['description', 'language', 'avg_rating']:
        if data[key] == 'N/A':
            data[key] = None  # ou '' pour une chaîne vide
    
    # Assurez-vous que les valeurs par défaut comme '0' pour review_count sont des entiers
    if data['review_count'] == '0':
        data['review_count'] = 0
    else:
        try:
            data['review_count'] = int(data['review_count'])
        except ValueError:
            data['review_count'] = None  # ou 0 selon ce que vous préférez

    return data

# Nettoyage des données
cleaned_data = [clean_data(book) for book in data]

# Sauvegarde des données dans un fichier JSON
with open('books_data.json', 'w') as f:
    json.dump(cleaned_data, f, indent=4)
