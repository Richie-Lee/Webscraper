from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime

# Get HMTL source
SCRAPE_HTML_SOURCE = True

# Track total runtime
_start_time = datetime.now()
bdo_uk_url = "https://www.bdo.co.uk" # used for formulating urls from scraped documents

# URL to scrape
url = "https://www.bdo.co.uk/en-gb/insights/tax"
export_directory = "C:/Users/RLee/Desktop/TAX BASE/bdo_uk_scrape.txt"


def scrape_html_source(url):
    """
    Scrapes the html file from the URL.
    - Capable of handling dynamic pages, by automating hovering
    """
    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run headless
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Open the webpage
        driver.get(url)
    
        # Wait until the specific element that signifies that articles are loaded is present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "insight-grid__cards"))
        )
    
        # Locate all article elements
        article_elements = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "animated-card"))
        )
    
        # Hover over each article element to trigger the loading of content
        for article in article_elements:
            # Scroll the article into view before hovering to avoid MoveTargetOutOfBoundsException
            driver.execute_script("arguments[0].scrollIntoView(true);", article)
            time.sleep(1)  # Wait for scrolling and possible page re-layout
            ActionChains(driver).move_to_element(article).perform()
            # You may need to wait for the animation to complete
            # time.sleep(1)  # Adjust the sleep time as necessary
    
        # Re-grab the page source after all hovers have been performed
        html_source = driver.page_source
    
    except Exception as e:
        import traceback
        print(f"An error occurred: {e}")
        traceback.print_exc()  # This will print the full traceback
        
    finally:
        driver.quit()
    
    return html_source

if SCRAPE_HTML_SOURCE == True:
    html_source = scrape_html_source(url)
    
soup = BeautifulSoup(html_source, 'lxml')

# Find the container for all articles
article_container = soup.find("div", class_="insight-grid__cards")
articles = article_container.find_all("article") 

export_str = ""

for article in articles:
    title = article.find("div", class_="featured-card__title").text if article.find("div", class_="featured-card__title") else None
    date = article.find("div", class_="featured-card__date").text if article.find("div", class_="featured-card__date") else None
    description = article.find("div", class_="featured-card__description").text if article.find("div", class_="featured-card__description") else None
    
    link_tag = article.find('a', class_='animated-card cursor-pointer')  # this should find the 'a' tag directly
    link = bdo_uk_url + link_tag['href'] if link_tag else None  # gets the href attribute if the 'a' tag is found
    
    article_summary = f"\n{'=' * 30}\n\nTitle: {title} \nDate: {date} \nDescription: {description} \nLink: {link}"
    print(article_summary)
    export_str += article_summary


def str_to_txt_file(export_str):
    text_file = open(export_directory, 'w')
    text_file.write(export_str)
    text_file.close()

str_to_txt_file(export_str)
    
# Print execution time
print(f"\n===============================\nTotal runtime:  {datetime.now() - _start_time}")

