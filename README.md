# Amazon Product and Review API Documentation

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

#### Example Request:
```
GET /products/1/reviews?page=1&limit=5
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

## Error Handling

### 400 Bad Request
Occurs when invalid query parameters are provided.
```json
{
    "detail": "Invalid query parameters"
}
```

### 404 Not Found
Occurs when a product or review is not found.
```json
{
    "detail": "Product not found"
}
```

### 500 Internal Server Error
Occurs when an internal server error happens.
```json
{
    "detail": "Internal server error"
}
```

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

## Author
Mashrukh – Sr Data Scientist at SSL Wireless.
