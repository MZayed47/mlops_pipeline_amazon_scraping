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
    - [AWS Elastic Beanstalk Deployment Guide FastAPI & Scraping Task]
    - [Step 1: Prepare the FastAPI Application]
    - [Step 2: Set Up Elastic Beanstalk Environment]
    - [Step 3: Set Up Amazon RDS for PostgreSQL]
    - [Step 4: Set Up AWS Lambda for Scraping Task]
    - [Step 5: Deploy the FastAPI Application]
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
uvicorn api_v1:app --reload
```

---

# Service Deployment

## AWS Elastic Beanstalk Deployment Guide FastAPI & Scraping Task

The following description provides a rough idea on the step-by-step approach I would take to deploying a FastAPI application and a periodic scraping task on AWS using Elastic Beanstalk, Amazon RDS for PostgreSQL, and AWS Lambda for scheduling.

### Why Elastic Beanstalk?
- **Managed Environment**: Elastic Beanstalk handles infrastructure management, load balancing, scaling, and monitoring.
- **Scalability**: Automatically adjusts based on application traffic.
- **Integration**: Easily integrates with AWS services like RDS, S3, CloudWatch, and IAM.

---

## Step 1: Prepare the FastAPI Application

### 1.1 Create a Project Structure
Organize the project directory as given in this GitHub repo within an "app" folder or similar, and the Dockerfile in the project-root:

```
project-root/
├── app/
│   ├── api_v1.py                # FastAPI app
│   ├── utility_v1.py            # necessary functions script
│   ├── amazon_watches_v2.py     # perioidic scrapping
│   └── requirements.txt         # Dependencies
└── Dockerfile                   # Docker configuration for FastAPI
```

### 1.2 Write Dockerfile
Use a `Dockerfile` to containerize the FastAPI application:

```dockerfile
# Dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.api_v1:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.3 Add Dependencies
List the dependencies in `requirements.txt`. I have is mentioned above.

---

## Step 2: Set Up Elastic Beanstalk Environment

### 2.1 Create an Elastic Beanstalk Application
1. Navigate to the **Elastic Beanstalk** service in the AWS Console.
2. **Create Application** and select **Web server environment**.
3. Configure the environment with the following options:
   - **Platform**: Choose "Docker."
   - **Application Code**: Upload the `project-root` folder.

### 2.2 Configure Elastic Beanstalk Environment
1. Under **Configuration**, adjust settings:
   - **Capacity**: Set minimum and maximum instance count for scaling.
   - **Load Balancer**: Ensure it’s set up for auto-scaling.
   - **Database**: Link to an **Amazon RDS PostgreSQL** database (created in Step 3).

---

## Step 3: Set Up Amazon RDS for PostgreSQL

1. Navigate to **Amazon RDS** in the AWS Console.
2. Create a new PostgreSQL instance:
   - Select the latest PostgreSQL version.
   - Choose instance size according to expected load (I usually use `db.t3.micro` for development).
3. Configure security groups to allow the Beanstalk environment to access the RDS instance.
4. Note the **endpoint**, **database name**, **username**, and **password** for database connection in FastAPI.

### 3.1 Configure Database Connection in FastAPI
In `api_v1.py`, currently I have the connection code loaded from JSON file. But for AWS, we should add the database connection code using environment variables (.env) for security and load it in "startup" event:

```python
import os
from fastapi import FastAPI
import psycopg2

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

@app.on_event("startup")
async def startup():
    app.state.db = psycopg2.connect(DATABASE_URL)
```

---

## Step 4: Set Up AWS Lambda for Scraping Task

1. Navigate to **AWS Lambda** in the Console.
2. Create a new Lambda function for the scraping task:
   - **Runtime**: Python 3.x
   - **Permissions**: Assign an IAM role allowing S3 access (if you’re storing scraped data in S3).

3. Write the scraping logic from `amazon_watches_v2.py` in the Lambda function and schedule it:
   - Use **Amazon EventBridge** to run the function at intervals (Suppose, every 30 minutes).

---

## Step 5: Deploy the FastAPI Application

### 5.1 Deploy Using Elastic Beanstalk CLI (Optional)
1. Install the Elastic Beanstalk CLI and configure it:
   ```bash
   pip install awsebcli
   eb init -p docker my-fastapi-app
   ```
2. Create an Elastic Beanstalk environment and deploy:
   ```bash
   eb create my-fastapi-env
   eb deploy
   ```

### 5.2 Deploy Using AWS Console
- From the Elastic Beanstalk Console, navigate to the application and click **Upload and Deploy**.
- Choose the Dockerized application bundle and deploy.

---

## Step 6: Domain Name and SSL (Optional, if needed)

1. Set up **Amazon Route 53** for custom domain management.
2. Use **AWS Certificate Manager (ACM)** to provision SSL certificates for HTTPS.

---

## Step 7: Monitoring and Scaling

1. Set up **Amazon CloudWatch** to monitor metrics like CPU usage, memory, and request latency.
2. Enable **Auto Scaling** within the Elastic Beanstalk environment to automatically adjust the instance count based on demand.

---


## Author
Mashrukh Zayed – Sr Data Scientist at SSL Wireless.
