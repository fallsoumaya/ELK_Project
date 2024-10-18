from elasticsearch import Elasticsearch, helpers
import json

# Connexion à Elasticsearch
es = Elasticsearch(["http://localhost:9201"])

# Nom de l'index où les données seront stockées
index_name = "books_index"

# Chargement des données à partir du fichier JSON
with open('books_data.json', 'r') as file:
    data = json.load(file)

# Fonction pour générer des documents à indexer
def generate_documents(data):
    for i, doc in enumerate(data):
        yield {
            "_index": index_name,
            "_id": i,  # Utilisez un ID unique pour chaque document
            "_source": {
                "title": doc.get("title"),
                "authors": doc.get("authors"),
                "description": doc.get("description"),
                "genres": doc.get("genres"),
                "year_of_publication": doc.get("year_of_publication"),
                "language": doc.get("language"),
                "avg_rating": doc.get("avg_rating"),
                "review_count": doc.get("review_count")
            }
        }


# Indexation des documents
helpers.bulk(es, generate_documents(data))

print("Données indexées avec succès !")
