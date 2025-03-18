import os
import unittest
from book import NCERTScraper  

class TestNCERTScraper(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.scraper = NCERTScraper()
    
    def test_setup(self):
        """Test if the scraper initializes correctly."""
        self.assertTrue(os.path.exists(self.scraper.zip_folder))
    
    def test_scrape_data(self):
        """Test scraping function by checking if it returns the expected folder."""
        result_folder = self.scraper.scrape_data()
        self.assertTrue(os.path.exists(result_folder))
    
    def test_download_file(self):
        """Test file downloading by verifying a sample download."""
        sample_url = "https://ncert.nic.in/textbook/pdf/fees1.zip"  # Example URL
        success = self.scraper._download_file(sample_url)
        downloaded_file = os.path.join(self.scraper.zip_folder, "fees1.zip")
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(downloaded_file))
    
    def test_extract_zip(self):
        """Test ZIP extraction and verify if files are extracted."""
        extracted_folder = self.scraper.extract_zip()
        self.assertTrue(os.path.exists(extracted_folder))
        self.assertGreater(len(os.listdir(extracted_folder)), 0)
    
    def test_end_to_end(self):
        """Test the entire workflow from scraping to extraction."""
        zip_folder = self.scraper.scrape_data()
        self.assertTrue(os.path.exists(zip_folder))
        
        extracted_folder = self.scraper.extract_zip()
        self.assertTrue(os.path.exists(extracted_folder))
        self.assertGreater(len(os.listdir(extracted_folder)), 0)
        
if __name__ == "__main__":
    unittest.main()
