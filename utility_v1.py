import psycopg2
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# Load the SentenceTransformer model (all-roberta-large-v1)
embed_model = SentenceTransformer('sentence-transformers/all-roberta-large-v1')


# Load database credentials
with open('data/creds.json') as f:
    creds = json.load(f)


# Function to connect to the PostgreSQL database
def connect_db():
    conn = psycopg2.connect(
        dbname=creds['database'],
        user=creds['user'],
        password=creds['password'],
        host=creds['host'],
        port=creds['port']
    )
    return conn


# Function to fetch all data and create document embeddings
def fetch_data_as_documents():
    # Connect to the database
    conn = connect_db()
    documents = []

    try:
        with conn.cursor() as cursor:
            # Fetch the necessary columns from your table
            query = """
                SELECT title, price, overall_rating, total_reviews, availability, model_number, material, item_length, clasp
                FROM amazon_watches;
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            # Loop through each row and create a text document
            for row in rows:
                title = row[0] or "N/A"
                price = f"The product costs ${row[1]}." if row[1] else "Price not available."
                rating = f"It has an overall rating of {row[2]}." if row[2] else "No rating available."
                total_reviews = f"It also has a total of {row[3]} reviews." if row[3] else "No rating available."
                availability = row[4] or "Availability information not provided."
                model = f"The model number is {row[5]}." if row[5] else "Model number not provided."
                material = f"The material is {row[6]}." if row[6] else "Material not specified."
                length = f"It has an item length of {row[7]}." if row[7] else "Item length not provided."
                clasp = f"The clasp type is {row[8]}." if row[8] else "Clasp type not specified."

                # Create a document by combining all the attributes
                document = f"{title}. {price} {rating} {total_reviews} {availability} {model} {material} {length} {clasp}"
                
                # Append to documents list
                documents.append(document)

    finally:
        conn.close()

    return documents


# Function to generate document embeddings
def generate_document_embeddings(documents):
    # Create embeddings for all documents
    return embed_model.encode(documents, convert_to_numpy=True)


# Function to create the FAISS index
def create_faiss_index(doc_embeddings):
    # Initialize a FAISS index (for cosine similarity)
    dimension = doc_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    
    # Normalize the embeddings (for cosine similarity)
    faiss.normalize_L2(doc_embeddings)

    # Add the document embeddings to the index
    index.add(doc_embeddings)
    return index


# Function to generate the query embedding
def generate_query_embedding(query):
    return embed_model.encode(query, convert_to_numpy=True)


# Function to search for the top documents using FAISS index
def search(query_embedding, index, top_k=10):
    # Normalize the query embedding (for cosine similarity)
    faiss.normalize_L2(query_embedding.reshape(1, -1))

    # Perform the search
    distances, indices = index.search(query_embedding.reshape(1, -1), top_k)
    return indices[0]  # Return the indices of the top documents

