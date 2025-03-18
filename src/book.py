import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import zipfile
 
class NCERTScraper:
    """Class for scraping and extracting NCERT textbooks."""
    
    def __init__(self, chromedriver_path="/usr/bin/chromedriver", base_url="https://ncert.nic.in/textbook.php?"):
        """Initialize with chromedriver path and base URL."""
        self.chromedriver_path = chromedriver_path
        self.base_url = base_url
        self.zip_folder = "book_pdfs"
        os.makedirs(self.zip_folder, exist_ok=True)
        
    def _setup_driver(self):
        """Set up and return a headless Chrome driver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(self.chromedriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)
        
    def _find_download_link(self, url):
        """Find download link for NCERT textbook from URL."""
        driver = self._setup_driver()
        driver.get(url)
        time.sleep(7)  # Wait for page to load completely
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        driver.quit()
        
        download_link = None
        for a_tag in soup.find_all("a"):
            if "Download complete book" in a_tag.get_text():
                download_link = a_tag["href"]
                break
                
        if download_link:
            if download_link and download_link.startswith(".."):
                download_link = "https://ncert.nic.in/" + download_link.replace("..", "")
            return download_link
        else:
            print(f"No valid donload link found for {url}")
            return None
        
    def _download_file(self, download_link):
        """Download file from the given link."""
        if not download_link:
            print("Skipping download")
            return False
        response = requests.get(download_link, stream=True)
        if response.status_code == 200:
            zip_filename = os.path.join(self.zip_folder, download_link.split("/")[-1])
            with open(zip_filename, "wb") as zip_file:
                for chunk in response.iter_content(1024):
                    zip_file.write(chunk)
            return True
        else:
            print(f"Failed to download:{download_link}(Status: {response.status_code})")
            return False
    
    def scrape_data(self):
        """Scrape NCERT textbooks from predefined list of book codes."""
        book_codes = [
            "fees1=1-14",
            "gess3=0-8",
            "hess3=0-8",
            "iess4=0-5",
            "jess4=0-5"
        ]
        
        success_count = 0
        for code in book_codes:
            url = self.base_url + code
            print(f"Processing {url}")
            
            try:
                download_link = self._find_download_link(url)
                if download_link:
                    print(f"Found download link: {download_link}")
                    if self._download_file(download_link):
                        success_count += 1
                        print(f"Downloaded book {success_count} of {len(book_codes)}")
                    else:
                        print(f"Failed to download from {download_link}")
                else:
                    print(f"No download link found for {url}")
            except Exception as e:
                print(f"Error processing {url}:{e}")
                
        print(f"Downloaded {success_count} of {len(book_codes)} books")
        return self.zip_folder
        
    def extract_zip(self):
        """Extract all ZIP files in the zip folder."""
        extract_folder = os.path.join(self.zip_folder, "extracted")
        os.makedirs(extract_folder, exist_ok=True)
        
        zip_files = [f for f in os.listdir(self.zip_folder) if f.endswith(".zip")]
        
        if not zip_files:
            print("No ZIP files found to extract.")
            return
            
        for zip_file in zip_files:
            zip_path = os.path.join(self.zip_folder, zip_file)
            extract_path = os.path.join(extract_folder, zip_file.replace(".zip", ""))
            
            if os.path.exists(extract_path):  # kip if already extracted
                print(f"Already extracted: {zip_file}. Skipping...")
                continue
            print(f"Extracting {zip_file}...")
            
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_folder)
                print(f"Successfully extracted {zip_file}")
            except Exception as e:
                print(f"Error extracting {zip_file}: {str(e)}")
                
        return extract_folder