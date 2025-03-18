import os
import unittest
from book import NCERTScraper  

class TestNCERTScraper(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.scraper = NCERTScraper()

    def test_scraper_instance(self):
        """Ensure the NCERTScraper instance initializes correctly."""
        self.assertIsInstance(self.scraper, NCERTScraper, "NCERTScraper instance was not created properly.")

    def test_download_folder_permissions(self):
        """Check if the download folder has read and write permissions."""
        os.makedirs(self.scraper.zip_folder, exist_ok=True)
        self.assertTrue(os.access(self.scraper.zip_folder, os.R_OK | os.W_OK), 
                        "Download folder does not have read/write permissions.")

    def test_extracted_folder_permissions(self):
        """Verify that the extracted folder is accessible for reading files."""
        extracted_folder = os.path.join(self.scraper.zip_folder, "extracted")
        os.makedirs(extracted_folder, exist_ok=True)
        self.assertTrue(os.access(extracted_folder, os.R_OK), 
                        "Extracted folder does not have read permissions.")

    def test_download_folder_not_empty(self):
        """Ensure the download folder is not empty if files exist."""
        if os.path.exists(self.scraper.zip_folder):
            self.assertGreater(len(os.listdir(self.scraper.zip_folder)), 0, 
                               "Download folder is unexpectedly empty.")
        else:
            self.skipTest("Download folder does not exist.")

    def test_extracted_folder_not_empty(self):
        """Ensure the extracted folder contains files after extraction."""
        extracted_folder = os.path.join(self.scraper.zip_folder, "extracted")
        if os.path.exists(extracted_folder):
            self.assertGreater(len(os.listdir(extracted_folder)), 0, 
                               "Extracted folder is unexpectedly empty.")
        else:
            self.skipTest("Extracted folder does not exist.")

if __name__ == "__main__":
    unittest.main()
