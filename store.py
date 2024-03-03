import json
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, City, Category, SubCategory, Price

load_dotenv()

# Access database credentials from .env file (assuming it's in the same directory)
db_host = os.getenv("PGHOST")
db_user = os.getenv("PGUSER")
db_password = os.getenv("PGPASSWORD")
db_port = os.getenv("PGPORT")
db_name = os.getenv("PGDATABASE")

# Construct database connection URL
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Connect to database
engine = create_engine(connection_string)

# Drop the tables if they exist
Base.metadata.drop_all(engine)

# Create all tables in the engine
Base.metadata.create_all(engine)

# Create database session
Session = sessionmaker(bind=engine)
session = Session()


# Function to sanitize and extract data from the JSON string
def process_and_store_data(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)

    for category_name, category_data in data.items():
        # Create category if it doesn't exist
        category = session.query(Category).filter_by(category_name=category_name).first()
        if not category:
            category = Category(category_name)
            session.add(category)
            session.commit()

        for city_name, city_data in category_data.items():
            # Create city if it doesn't exist
            city = session.query(City).filter_by(city_name=city_name).first()
            if not city:
                city = City(city_name, None)  # Assuming no country information
                session.add(city)
                session.commit()

            for price_data in city_data:
                subcategory_name, average_price, min_price, max_price = process_data(price_data)

                # Create subcategory if it doesn't exist
                subcategory = session.query(SubCategory).filter_by(
                    subcategory_name=subcategory_name, category_id=category.id
                ).first()
                if not subcategory:
                    subcategory = SubCategory(subcategory_name, category.id)
                    session.add(subcategory)
                    session.commit()

                # Create price record
                price = Price(city.id, subcategory.id, average_price, min_price, max_price)
                session.add(price)

    session.commit()


# Process all JSON files in the "data" directory
for filename in os.listdir("data"):
    if filename.endswith(".json"):
        json_file = os.path.join("data", filename)
        process_and_store_data(json_file)

# Close the session
session.close()
