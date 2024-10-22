# Amazon Product and Review API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Endpoints](#endpoints)
    - [1. Search Products](#1-search-products)
    - [2. Get Top Products](#2-get-top-products)
    - [3. Get Product Reviews](#3-get-product-reviews)
4. [Database Schema](#database-schema-amazon-watches)
5. [Running the API](#running-the-api)
6. [Service Deployment](#service-deployment)
    - [A. Set Up a Conda Environment](#a-set-up-a-conda-environment)
    - [B. API Organization](#b-api-organization)
    - [C. Dockerization](#c-dockerization)
    - [D. Run The Scraping Pipeline in "amazon_watches_v2.py" using cron](#d-run-the-scraping-pipeline-in-amazon_watches_v2py-using-cron)
7. [Author](#author)

---
## Overview
This API provides endpoints to search for products, retrieve the top-rated products, and get product reviews from an Amazon database.

### Base URL
`http://127.0.0.1:8000`

---

## Endpoints

### 1. Search Products
**Endpoint**: `/products`  
**Method**: `GET`  
**Description**: Retrieves a list of products based on filters such as brand, model, price range, and rating. Supports pagination.

#### Query Parameters:
| Parameter  | Type   | Description                              | Example         |
|------------|--------|------------------------------------------|-----------------|
| `brand`    | `str`  | (Optional) Filters products by brand name | `Casio`         |
| `model`    | `str`  | (Optional) Filters products by model name | `G-Shock`       |
| `min_price`| `float`| (Optional) Filters products with minimum price | `100.0`     |
| `max_price`| `float`| (Optional) Filters products with maximum price | `500.0`     |
| `min_rating`| `float`| (Optional) Filters products with minimum rating | `4.0`    |
| `page`     | `int`  | (Optional) Page number for pagination. Default is 1. | `1` |
| `limit`    | `int`  | (Optional) Number of products per page. Default is 10. | `10` |

#### Response (200 OK):
Returns a list of products matching the criteria.

```json
[
    {
        "id": 1,
        "title": "Casio Men's Watch",
        "price": 150.0,
        "overall_rating": 4.5,
        "total_reviews": 100,
        "availability": "In Stock",
        "model": "G-Shock",
        "material": "Resin",
        "item_length": "7 inches",
        "length": "7 inches",
        "clasp": "Buckle",
        "model_number": "GA100-1A1",
        "link": "https://www.amazon.com/product/12345"
    }
]
```

#### Example Request:
```
GET /products?brand=Casio&min_price=100.0&max_price=300.0&min_rating=4.0&page=1&limit=5
```

---

### 2. Get Top Products
**Endpoint**: `/products/top`  
**Method**: `GET`  
**Description**: Retrieves a list of top-rated products based on reviews and ratings.

#### Query Parameters:
| Parameter  | Type   | Description                          | Example |
|------------|--------|--------------------------------------|---------|
| `limit`    | `int`  | (Optional) Number of top products to retrieve. Default is 10. | `10` |

#### Response (200 OK):
Returns a list of top products.

```json
[
    {
        "id": 1,
        "title": "Casio Men's Watch",
        "price": 150.0,
        "overall_rating": 4.5,
        "total_reviews": 100,
        "availability": "In Stock",
        "model": "G-Shock",
        "material": "Resin",
        "item_length": "7 inches",
        "length": "7 inches",
        "clasp": "Buckle",
        "model_number": "GA100-1A1",
        "link": "https://www.amazon.com/product/12345"
    }
]
```

#### Example Request:
```
GET /products/top?limit=5
```

---

### 3. Get Product Reviews
**Endpoint**: `/products/{product_id}/reviews`  
**Method**: `GET`  
**Description**: Retrieves a list of reviews for a specific product.

#### Path Parameters:
| Parameter   | Type   | Description                                | Example |
|-------------|--------|--------------------------------------------|---------|
| `product_id`| `int`  | ID of the product to retrieve reviews for   | `1`     |

#### Query Parameters:
| Parameter  | Type   | Description                            | Example |
|------------|--------|----------------------------------------|---------|
| `page`     | `int`  | (Optional) Page number for pagination. Default is 1. | `1` |
| `limit`    | `int`  | (Optional) Number of reviews per page. Default is 10. | `10` |

#### Response (200 OK):
Returns a list of reviews for the specified product.

```json
[
    {
        "reviewer_name": "John Doe",
        "review_text": "Great product, very durable and stylish!",
        "review_rating": "5.0",
        "review_date": "2023-01-15"
    },
    {
        "reviewer_name": "Jane Smith",
        "review_text": "Good value for the price, but the strap is a bit uncomfortable.",
        "review_rating": "4.0",
        "review_date": "2023-02-10"
    }
]
```

---

## Database Schema (Amazon Watches)
The table `amazon_watches` stores product and review information with the following fields:

- `id`: Product ID
- `title`: Product title
- `price`: Product price
- `overall_rating`: Overall rating (as string, extracted and cast as float)
- `total_reviews`: Total number of reviews (as string, extracted and cast as integer)
- `availability`: Product availability status
- `model`: Product model name
- `material`: Product material
- `item_length`: Length of the item
- `length`: Product length
- `clasp`: Type of clasp used
- `model_number`: Model number
- `link`: URL link to the product page
- Review fields (e.g., `reviewer_name_1`, `review_text_1`, `review_rating_1`, etc.)

---

## Running the API

### Requirements
- Python 3.x
- FastAPI
- Uvicorn
- PostgreSQL

### Start the API
Run the following command to start the API:

```bash
uvicorn main:app --reload
```

---

# Service Deployment

## A. Set Up a Conda Environment

1. Create and activate a new conda environment:

    ```bash
    conda create -n ml_ops python=3.9
    conda activate ml_ops
    ```

## B. API Organization

1. Use the two scripts for API:

    - **api_v1.py**: Holds the main functionality and calls the necessary functions from `utility_v1.py`.
    - **utility_v1.py**: Contains reusable functions.

## C. Dockerization

1. Export the environment libraries:

    ```bash
    conda list --export > requirements.txt
    ```

2. **Clean unnecessary library versions** in `requirements.txt` (recommended).

3. **Dockerize the application**:

    - **Dockerfile**: Copy the necessary files and set up the environment.
    - **docker-compose.yml**: Automate Docker setup and start the service.

4. Build and run the service:

    ```bash
    docker-compose build
    docker-compose up -d
    ```

    Or combine the steps:

    ```bash
    docker-compose up -d --build
    ```

5. **Check container logs**:

    ```bash
    docker logs <container_id>
    ```

## D. Run The Scrapping Pipeline in "amazon_watches_v2.py" using cron

### 1. Access the Docker container shell:
```bash
docker exec -it <container_id> /bin/bash
```

### 2. Open the crontab editor within the container:
```bash
crontab -e
```

### 3. Add the cron job to run your Python script every 30 minutes:
```bash
*/30 * * * * /usr/bin/python3 /path/to/your/amazon_watches_v2.py >> /path/to/logfile.log 2>&1
```
- **`*/30`**: Runs the job every 30 minutes.
- **`/usr/bin/python3`**: Path to the Python interpreter inside the container (adjust if different).
- **`/path/to/your/amazon_watches_v2.py`**: Path to your Python script inside the container.
- **`>> /path/to/logfile.log 2>&1`**: Logs the output and errors to `logfile.log` for debugging purposes (optional).

### 4. Save and exit the crontab editor.

### 5. Ensure the cron service is running:
You may need to start the cron service inside the container:

```bash
service cron start
```

## Author
Mashrukh – Sr Data Scientist at SSL Wireless.
