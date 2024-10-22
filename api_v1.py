from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import psycopg2
import json
from typing import List, Optional, Dict
import re
import uvicorn
from utility_v1 import *


global documents, document_embeddings, index

documents = fetch_data_as_documents()
document_embeddings = generate_document_embeddings(documents)
index = create_faiss_index(document_embeddings)


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


app = FastAPI()


# Define Pydantic models for product and review
class Product(BaseModel):
    id: int
    title: str
    price: float
    overall_rating: Optional[float]  # Change to float
    total_reviews: Optional[int]      # Change to int
    availability: Optional[str]
    model: Optional[str]      
    material: Optional[str]    
    item_length: Optional[str]
    length: Optional[str]      
    clasp: Optional[str]       
    model_number: Optional[str]
    link: Optional[str]                


class Review(BaseModel):
    reviewer_name: str
    review_text: str
    review_rating: str
    review_date: str


class AskRequest(BaseModel):
    query: str


# Helper function to extract numeric values
def extract_numeric(value: str) -> float:
    match = re.search(r"(\d+(\.\d+)?)", value)
    return float(match.group(1)) if match else 0.0

def extract_review_count(value: str) -> int:
    match = re.search(r"(\d{1,3}(,\d{3})*)", value)
    return int(match.group(1).replace(',', '')) if match else 0


# GET /products
@app.get("/products", response_model=List[Product])
async def search_products(
    brand: str = Query(None),
    model: str = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    min_rating: float = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1)
):
    offset = (page - 1) * limit
    params = []  # Start with an empty list
    conditions = []

    # Add brand filtering condition
    if brand:
        conditions.append("title ILIKE %s")
        params.append(f"%{brand}%")
    
    # Add model filtering condition
    if model:
        conditions.append("model ILIKE %s")
        params.append(f"%{model}%")
    
    # Add price filtering condition
    if min_price is not None:
        conditions.append("CAST(price AS FLOAT) >= %s")
        params.append(min_price)
    
    if max_price is not None:
        conditions.append("CAST(price AS FLOAT) <= %s")
        params.append(max_price)
    
    # Add rating filtering condition
    if min_rating is not None:
        conditions.append("CAST(SUBSTRING(overall_rating FROM '([0-9]+(\\.[0-9]+)?)') AS FLOAT) >= %s")
        params.append(min_rating)

    # Add limit and offset at the end
    params.append(limit)
    params.append(offset)

    # Build the WHERE clause from conditions
    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    
    # Final query
    query = f"""
        SELECT id, title, price,
               CAST(SUBSTRING(overall_rating FROM '([0-9]+(\\.[0-9]+)?)') AS FLOAT) AS overall_rating,
               CAST(REPLACE(SUBSTRING(total_reviews FROM '([0-9,]+)')::TEXT, ',', '') AS INTEGER) AS total_reviews,
               availability, model, material, item_length, length, clasp, model_number, link
        FROM amazon_watches
        WHERE {where_clause}
        ORDER BY total_reviews DESC, overall_rating DESC
        LIMIT %s OFFSET %s;
    """

    # Execute query with the prepared params list
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            products = cursor.fetchall()

            result = [
                {
                    "id": row[0],
                    "title": row[1],
                    "price": row[2],
                    "overall_rating": row[3],
                    "total_reviews": row[4],
                    "availability": row[5],
                    "model": row[6],
                    "material": row[7],
                    "item_length": row[8],
                    "length": row[9],
                    "clasp": row[10],
                    "model_number": row[11],
                    "link": row[12],
                } for row in products
            ]
            return result
    finally:
        conn.close()


# GET /products/top
@app.get("/products/top", response_model=List[Product])
async def get_top_products(limit: int = Query(10, ge=1)):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT id, title, price,
                       CAST(SUBSTRING(overall_rating FROM '([0-9]+(\\.[0-9]+)?)') AS FLOAT) AS overall_rating,
                       CAST(REPLACE(SUBSTRING(total_reviews FROM '([0-9,]+)')::TEXT, ',', '') AS INTEGER) AS total_reviews,
                       availability, model, material, item_length, length, clasp, model_number, link
                FROM amazon_watches
                ORDER BY total_reviews DESC, overall_rating DESC
                LIMIT %s;
            """
            cursor.execute(query, (limit,))
            products = cursor.fetchall()

            result = [
                {
                    "id": row[0],
                    "title": row[1],
                    "price": row[2],
                    "overall_rating": row[3],
                    "total_reviews": row[4],
                    "availability": row[5],
                    "model": row[6],
                    "material": row[7],
                    "item_length": row[8],
                    "length": row[9],
                    "clasp": row[10],
                    "model_number": row[11],
                    "link": row[12],
                } for row in products
            ]
            return result
    finally:
        conn.close()


# GET /products/{product_id}/reviews
@app.get("/products/{product_id}/reviews", response_model=List[Review])
async def get_product_reviews(product_id: int, page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT reviewer_name_1, review_text_1, review_rating_1, review_date_1
                FROM amazon_watches
                WHERE id = %s
                UNION ALL
                SELECT reviewer_name_2, review_text_2, review_rating_2, review_date_2
                FROM amazon_watches
                WHERE id = %s
                UNION ALL
                SELECT reviewer_name_3, review_text_3, review_rating_3, review_date_3
                FROM amazon_watches
                WHERE id = %s
                LIMIT %s OFFSET %s;
            """
            cursor.execute(query, (product_id, product_id, product_id, limit, (page - 1) * limit))
            reviews = cursor.fetchall()

            result = [
                {
                    "reviewer_name": row[0],
                    "review_text": row[1],
                    "review_rating": row[2],
                    "review_date": row[3],
                } for row in reviews
            ]
            return result
    finally:
        conn.close()


# POST /ask
@app.post("/ask")
async def ask_question(request: AskRequest):
    query = request.query

    # Step 3: Generate the query embedding for the input query
    query_embedding = generate_query_embedding(query)

    # Step 4: Retrieve relevant document indices using the FAISS index
    top_docs_indices = search(query_embedding, index)

    # Step 5: Fetch the top documents based on indices
    top_docs = [documents[i] for i in top_docs_indices]
    unique_top_docs = list(dict.fromkeys(top_docs))

    return {"query": query, "retrieved_documents": unique_top_docs}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)

