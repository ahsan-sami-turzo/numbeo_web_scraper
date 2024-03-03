import json
import os

import pandas as pd

# Define the name of the directory that contains the json files
json_dir = "data_files/numbeo_data"

# Define the name of the directory that will store the excel files
excel_dir = "data_files/city_data"

# Define the column names for the excel files
columns = ["Category", "Title", "priceAverage", "priceMin", "priceMax"]


# Define a function to convert a price string to a float and remove unwanted characters
def convert_price(price):
    # Replace the euro sign, the dollar sign, and the comma with empty strings
    price = price.replace("\u20ac", "").replace("$", "").replace(",", "")
    # Convert the price to a float
    price = float(price)
    # Return the price
    return price


# Iterate over all files in the json directory
for filename in os.listdir(json_dir):
    # If the file is a json file
    if filename.endswith(".json"):
        # Construct the full path of the json file
        json_file = os.path.join(json_dir, filename)
        # Construct the full path of the excel file with the same name
        excel_file = os.path.join(excel_dir, filename.replace(".json", ".xlsx"))

        # If the excel file already exists, delete it
        if os.path.exists(excel_file):
            os.remove(excel_file)

        # Read the json file
        with open(json_file, "r") as file:
            data = json.load(file)

        # Create an empty list to store the rows
        rows = []

        # Iterate over the json data
        for category, category_data in data.items():
            # Iterate over the list of prices
            for price_data in category_data:
                # Extract the title, average price, and price range
                title = price_data[0].strip()
                average_price = price_data[1].strip()
                price_range = price_data[2].strip()

                # Split the price range by the dash
                price_range = price_range.split("-")

                # If the price range has two values, assign them to min and max
                if len(price_range) == 2:
                    min_price = price_range[0].strip()
                    max_price = price_range[1].strip()
                # Otherwise, assign the average price to both min and max
                else:
                    min_price = average_price
                    max_price = average_price

                # Convert the prices to float and remove unwanted characters
                average_price = convert_price(average_price)
                min_price = convert_price(min_price)
                max_price = convert_price(max_price)

                # Create a row as a dictionary
                row = {
                    "Category": category.strip(),
                    "Title": title,
                    "priceAverage": average_price,
                    "priceMin": min_price,
                    "priceMax": max_price
                }

                # Append the row to the list
                rows.append(row)

        # Convert the list of rows to a pandas dataframe
        df = pd.DataFrame(rows, columns=columns)

        # Write the dataframe to the excel file
        df.to_excel(excel_file, index=False)

        # Print a success message
        print(f"The data from {json_file} was successfully stored to {excel_file}.")
