from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from selenium.webdriver.chrome.service import Service # type: ignore
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
from bs4 import BeautifulSoup
import time

def scrape_importyeti(url):
    """
    Scrape content from ImportYeti website using Selenium
    """
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        # Initialize the Chrome driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for dynamic content to load
        time.sleep(5)
        
        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract main content
        main_content = soup.find('main') or soup.find('div', {'id': 'root'})
        
        if main_content:
            print(f"Successfully scraped content from {url}")
            print("-" * 50)
            print(main_content.text.strip())
        else:
            print("Could not find main content element. Printing full page text:")
            print(soup.text.strip())
            
        # Close the driver
        driver.quit()
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        
if __name__ == "__main__":
    url = "https://www.importyeti.com/company/codan-us"
    scrape_importyeti(url)