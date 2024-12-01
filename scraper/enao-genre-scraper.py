import time
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Adjust this number based on your system's capabilities
num_threads = int(input("How many threads do you want to use for the scraping? (Recommended: 4): ") or 4)

# Set up selenium driver
chrome_options = Options()
chrome_options.add_argument("--headless")
chromedriver_path = 'C:\\Users\\Wildan Aziz\\OneDrive\\Documents\\Dev\\enoa-scraper\\chromedriver.exe'
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://everynoise.com/")

# Record the start time
start_time = time.time()

# Scrape all genres + convert style attributes to DataFrame
genres_elems = driver.find_elements(By.CLASS_NAME, "genre")

# Initialize an empty list for genre data
genres_objs = []

# Function to scrape genre data (this will run in parallel threads)
def scrape_genre(genre):
    genre_obj = {
        "genre": genre.get_attribute("innerText"),
        "preview_url": genre.get_attribute("preview_url"),
        "preview_track": genre.get_attribute("title")
    }
    
    for style in genre.get_attribute("style").split(";")[:-1]:
        [key, value] = style.split(":")
        genre_obj[key.strip().replace("-", "_")] = value.strip()
    
    return genre_obj

# Create a ThreadPoolExecutor for concurrent scraping
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    # Use tqdm to display the progress
    futures = [executor.submit(scrape_genre, genre) for genre in genres_elems]
    
    # Use tqdm to monitor progress
    for future in tqdm(as_completed(futures), total=len(futures), desc="Scraping progress", unit="genre"):
        genres_objs.append(future.result())

# Convert the list of genre objects to a DataFrame
genres_df = pd.DataFrame(genres_objs)

# Save data
genres_df.to_csv("../data/enao-genres.csv", index=False)

# Record the end time
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - start_time
print(f"Scraping process completed in {elapsed_time:.2f} seconds.")

# Clean up: close the browser
driver.quit()