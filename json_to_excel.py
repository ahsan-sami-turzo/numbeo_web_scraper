import json
import os

import pandas as pd

# Define the name of the directory that contains the json files
json_dir = "data_files/numbeo_data"

# Define the name of the directory that will store the excel files
excel_dir = "data_files/city_data"

# Define the column names for the excel files
columns = ["Category", "Title", "priceAverage", "priceMin", "priceMax"]


# Define a function to check if a character is a special character
def is_special_char(char):
    # A special character is any character that is not alphanumeric or whitespace
    return not (char.isalnum() or char.isspace())


# Define a list of unwanted characters
unwanted_chars = ["\n", "\t", "\r", "\u00a0", "?", "€", "\xa0", "€"]

# Iterate over all the characters in the ASCII table
for i in range(128):
    # Convert the integer to a character
    char = chr(i)
    # If the character is a special character, add it to the list
    if is_special_char(char):
        unwanted_chars.append(char)


# Define a function to remove unwanted characters from a string
def remove_unwanted_chars(string):
    # Replace each unwanted character with an empty string
    for char in unwanted_chars:
        string = string.replace(char, "")
    # Return the cleaned string
    return string


def remove_unwanted_chars_from_number(number):
    number = str(number)
    number = remove_unwanted_chars(number)
    number = number.replace("\u20ac", "").replace("$", "").replace(",", "")
    if number == "":
        return 0
    number = float(number)
    return number


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

                # Remove unwanted characters from the strings and the numbers
                category = remove_unwanted_chars(category)
                title = remove_unwanted_chars(title)
                average_price = remove_unwanted_chars_from_number(average_price)
                min_price = remove_unwanted_chars_from_number(min_price)
                max_price = remove_unwanted_chars_from_number(max_price)

                # Create a row as a dictionary
                row = {
                    "Category": category,
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
