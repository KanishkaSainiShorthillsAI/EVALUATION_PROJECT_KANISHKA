import os
import unittest
import shutil
from book import NCERTScraper  

class TestNCERTScraper(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.scraper = NCERTScraper()

    def test_download_directory_exists(self):
        """Test if the book_pdfs directory exists."""
        os.makedirs(self.scraper.zip_folder, exist_ok=True)  
        self.assertTrue(os.path.exists(self.scraper.zip_folder), "Download directory does not exist.")

    def test_extracted_directory_exists(self):
        """Test if the extracted folder exists."""
        extracted_folder = os.path.join(self.scraper.zip_folder, "extracted")
        os.makedirs(extracted_folder, exist_ok=True)  
        self.assertTrue(os.path.exists(extracted_folder), "Extracted folder does not exist.")

    def test_download_directory_file_count(self):
        """Check if the download directory has exactly 5 files."""
        zip_files = [f for f in os.listdir(self.scraper.zip_folder) if f.endswith(".zip")]
        self.assertEqual(len(zip_files), 5, f"Expected 5 ZIP files, but found {len(zip_files)}")

    def test_extracted_directory_file_count(self):
        """Check if the extracted directory has exactly 46 files."""
        extracted_folder = os.path.join(self.scraper.zip_folder, "extracted")
        extracted_files = os.listdir(extracted_folder) if os.path.exists(extracted_folder) else []
        self.assertEqual(len(extracted_files), 46, f"Expected 46 files, but found {len(extracted_files)}")

    

if __name__ == "__main__":
    unittest.main()
