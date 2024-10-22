import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
from psycopg2 import sql
import os
import json
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.abspath(os.path.dirname("__file__"))
DATA_DIR = os.path.join(BASE_DIR, "data")

CREDS_PATH = os.path.join(DATA_DIR, 'creds.json')

with open(CREDS_PATH) as f:
    creds = json.load(f)


# Function to connect to the PostgreSQL database
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=creds['database'],
            user=creds['user'],
            password=creds['password'],
            host=creds['host'],
            port=creds['port']
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None

# Function to create table if it does not exist
def create_table_if_not_exists(conn):
    with conn.cursor() as cursor:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS amazon_watches (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price TEXT,
            overall_rating TEXT,
            total_reviews TEXT,
            availability TEXT,
            model TEXT,
            material TEXT,
            item_length TEXT,
            length TEXT,
            clasp TEXT,
            model_number TEXT,
            reviewer_name_1 TEXT,
            review_text_1 TEXT,
            review_rating_1 TEXT,
            review_date_1 TEXT,
            reviewer_name_2 TEXT,
            review_text_2 TEXT,
            review_rating_2 TEXT,
            review_date_2 TEXT,
            reviewer_name_3 TEXT,
            review_text_3 TEXT,
            review_rating_3 TEXT,
            review_date_3 TEXT,
            link TEXT UNIQUE  -- Add unique link column
        );
        """
        cursor.execute(create_table_query)
        conn.commit()

# Function to insert data into the database
def insert_data(conn, data):
    with conn.cursor() as cursor:
        insert_query = sql.SQL("""
            INSERT INTO amazon_watches (title, price, overall_rating, total_reviews, availability,
                                          model, material, item_length, length, clasp, model_number,
                                          reviewer_name_1, review_text_1, review_rating_1, review_date_1,
                                          reviewer_name_2, review_text_2, review_rating_2, review_date_2,
                                          reviewer_name_3, review_text_3, review_rating_3, review_date_3,
                                          link)
            VALUES (%s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s) ON CONFLICT (link) DO NOTHING;  -- Handle duplicate links
        """)
        cursor.execute(insert_query, (
            data.get("title"),
            data.get("price"),
            data.get("overall_rating"),
            data.get("total_reviews"),
            data.get("availability"),
            data.get("Model"),
            data.get("Material"),
            data.get("Item Length"),
            data.get("Length"),
            data.get("Clasp"),
            data.get("Model number"),
            data.get("reviewer_name_1"),
            data.get("review_text_1"),
            data.get("review_rating_1"),
            data.get("review_date_1"),
            data.get("reviewer_name_2"),
            data.get("review_text_2"),
            data.get("review_rating_2"),
            data.get("review_date_2"),
            data.get("reviewer_name_3"),
            data.get("review_text_3"),
            data.get("review_rating_3"),
            data.get("review_date_3"),
            data.get("link")  # Include the link in the insert statement
        ))
        conn.commit()


# Function to extract Product Title
def get_title(soup):

    try:
        # Outer Tag Object
        title = soup.find("span", attrs={"id":'productTitle'})
        
        # Inner NavigatableString Object
        title_value = title.text

        # Title as a string value
        title_string = title_value.strip()

    except AttributeError:
        title_string = ""

    return title_string

# Function to extract Product Price
def get_price(soup):
    try:
        # Find the price data in the HTML
        price_data = soup.find("div", attrs={'class':'a-section aok-hidden twister-plus-buying-options-price-data'}).string.strip()
        
        # Parse the JSON string to a Python dictionary
        price_dict = json.loads(price_data)
        
        # Access the "priceAmount" field
        price_amount = price_dict["desktop_buybox_group_1"][0]["priceAmount"]
    
    except (AttributeError, json.JSONDecodeError, KeyError):
        # Handle cases where the price or data is not found or malformed
        price_amount = ""

    return price_amount

# Function to extract Product Rating
def get_rating(soup):

    try:
        rating = soup.find("i", attrs={'class':'a-icon a-icon-star a-star-4-5'}).string.strip()
    
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
        except:
            rating = ""	

    return rating

# Function to extract Number of User Reviews
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id':'acrCustomerReviewText'}).string.strip()

    except AttributeError:
        review_count = ""	

    return review_count

# Function to extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id':'availability'})
        available = available.find("span").string.strip()

    except AttributeError:
        available = "Not Available"	

    return available


# Your new function for scraping technical specifications
def get_technical_specs(soup):
    specs = {}
    try:
        table = soup.find("table", {"id": "technicalSpecifications_section_1"})
        if table:
            for row in table.find_all("tr"):
                th = row.find("th").text.strip()  # Extracting header name
                td = row.find("td").text.strip()  # Extracting corresponding value
                specs[th] = td  # Adding to the dictionary
    except AttributeError:
        pass
    return specs


# Function to get consistent lengths for review data
def get_reviews(soup):
    names, reviews, ratings, dates = [], [], [], []
    try:
        review_list = soup.find("div", {"id": "cm-cr-dp-review-list"})
        review_divs = review_list.find_all("div", attrs={"data-hook": "review"}, limit=3)
        for review_div in review_divs:
            name = review_div.find("span", attrs={"class": "a-profile-name"}).text.strip()
            review = review_div.find("div", attrs={"data-hook": "review-collapsed"}).text.strip()
            rating = review_div.find("i", attrs={"data-hook": "review-star-rating"}).text.strip()
            date = review_div.find("span", attrs={"data-hook": "review-date"}).text.strip()
            names.append(name)
            reviews.append(review)
            ratings.append(rating)
            dates.append(date)
    except AttributeError:
        pass
    
    # Ensure three entries for names, reviews, ratings, and dates
    for _ in range(3 - len(reviews)):
        names.append("")
        reviews.append("")
        ratings.append("")
        dates.append("")
    
    return names, reviews, ratings, dates


# Combining data with technical specifications and link
def get_all_data(soup, product_link):
    data = {
        "title": get_title(soup),
        "price": get_price(soup),
        "overall_rating": get_rating(soup),
        "total_reviews": get_review_count(soup),
        "availability": get_availability(soup),
        "link": product_link  # Add the product link to the data
    }
    
    # Get the technical specifications and merge them with the existing data
    specs = get_technical_specs(soup)
    data.update(specs)

    names, reviews, ratings, dates = get_reviews(soup)
    data["reviewer_name_1"] = names[0]
    data["review_text_1"] = reviews[0]
    data["review_rating_1"] = ratings[0]
    data["review_date_1"] = dates[0]

    data["reviewer_name_2"] = names[1]
    data["review_text_2"] = reviews[1]
    data["review_rating_2"] = ratings[1]
    data["review_date_2"] = dates[1]

    data["reviewer_name_3"] = names[2]
    data["review_text_3"] = reviews[2]
    data["review_rating_3"] = ratings[2]
    data["review_date_3"] = dates[2]

    return data


if __name__ == '__main__':
    HEADERS = {'User-Agent': '', 'Accept-Language': 'en-US, en;q=0.5'}
    URL = "https://www.amazon.com/s?i=specialty-aps&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A6358539011&ref=nav_em__nav_desktop_sa_intl_watches_0_2_13_4"

    # Connect to the database
    conn = connect_db()
    if conn is None:
        exit()

    logging.info("Connected to database")

    try:
        # Create table if it doesn't exist
        create_table_if_not_exists(conn)

        webpage = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "html.parser")
        links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})
        links_list = [link.get('href') for link in links]

        data_list = []

        for link in links_list:
            try:
                product_link = "https://www.amazon.com" + link  # Construct the full product link
                new_webpage = requests.get(product_link, headers=HEADERS)
                new_soup = BeautifulSoup(new_webpage.content, "html.parser")
                product_data = get_all_data(new_soup, product_link)  # Pass the link to get_all_data
                data_list.append(product_data)

                # Insert each product's data into the database
                insert_data(conn, product_data)
                
                logging.info(f"Inserted data for product: {product_data['title']}")
                
                time.sleep(1)  # Delay to prevent getting blocked

            except Exception as e:
                logging.error(f"Error scraping {link}: {e}")

        # Write to CSV after collecting all data
        df = pd.DataFrame(data_list)
        df.to_csv("amazon_watch_data_with_specs_5.csv", index=False)

    finally:
        conn.close()  # Close the database connection
