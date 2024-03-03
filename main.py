import json

import pandas as pd
import requests
from bs4 import BeautifulSoup


class ExtractTable:

    def __init__(self, page):
        self.table = page.find("table", class_="data_wide_table")
        self.data = {}

    def extract(self):
        if not self.table:
            return None

        for row in self.table.find_all("tr"):
            if row.find_all("th"):
                header = row.find_all("th")[0].text
                self.data[header] = []
            else:
                self.data[header].append([cell.text for cell in row.find_all("td")])

        return self.data


class CityScraper:

    def __init__(self, base_url, country, scrape_all_cities=False):
        self.base_url = base_url
        self.country = country
        self.all_cities = []
        self.results = {}

        # Scrape country-level data
        self.url = f"{base_url}/country_result.jsp?country={country}"
        response = requests.get(self.url)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.content, "html.parser")
            self.extract_country_data()
            if scrape_all_cities:
                self.extract_all_cities()

    def write_city_data_to_json(self, city_data, filename):
        try:
            with open(filename, "w") as f:
                json.dump(city_data, f, indent=4)  # Add indentation for readability
        except Exception as e:
            print(f"Error writing data to JSON: {e}")

    def write_city_data_to_excel(self, city_data, filename):
        try:
            first_row_length = len(list(city_data.values())[0])
            for row in city_data.values():
                if len(row) != first_row_length:
                    raise ValueError("Inconsistent data lengths in city_data")

            df = pd.DataFrame(city_data)
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=filename, index=False)
            writer.save()
        except ValueError as e:
            print(f"Error writing data: {e}")

    def extract_country_data(self):
        extractor = ExtractTable(self.soup)
        self.results[self.country] = extractor.extract()

    def extract_city_data(self, city):
        city_url = f"{self.base_url}/city_result.jsp?country={self.country}&city={city}"
        response = requests.get(city_url)
        if response.status_code == 200:
            city_soup = BeautifulSoup(response.content, "html.parser")
            extractor = ExtractTable(city_soup)
            return extractor.extract()
        else:
            print(f"Error fetching data for city: {city}")
            return None

    def extract_all_cities(self):
        self.all_cities_form = self.soup.find("form", class_="standard_margin")
        if self.all_cities_form:
            self.all_cities = [option["value"] for option in self.all_cities_form.find_all("option")]
            self.results[self.country]["cities"] = {}
            for city in self.all_cities:
                data = self.extract_city_data(city)
                if data:
                    self.results[self.country]["cities"][city] = data
                    # Writes data to excel
                    # self.write_city_data_to_excel(data, f"{city}.xlsx")
                    # Writes data to json
                    self.write_city_data_to_json(data, f"{city}.json")

    def get_results(self):
        return self.results


if __name__ == "__main__":
    URL = "https://www.numbeo.com/cost-of-living/"
    COUNTRY = "Finland"
    SCRAPE_ALL_CITIES = True  # Set to True to scrape all cities

    scraper = CityScraper(URL, COUNTRY, scrape_all_cities=SCRAPE_ALL_CITIES)
    results = scraper.get_results()

    with open("results.json", "w") as f:
        json.dump(results, f)

    print(f"Scraped data for {COUNTRY}:")
    # print(results)
