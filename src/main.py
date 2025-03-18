import os
import weaviate
from dotenv import load_dotenv
from chunk import DocumentProcessor
from book import NCERTScraper
load_dotenv()
def run_backend():
    pdf_directory = os.path.join("book_pdfs", "extracted")
    # Connect to Weaviate
    try:
        weaviate_client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv('WEAVIATE_RESTURL'),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv('WEAVIATE_ADMIN'))
        )
        print("Weaviate connection established.")
    except Exception as e:
        print(f"Error connecting to Weaviate: {e}")
        return None
    # Scrape if PDFs directory don't exist
    if not os.path.exists(pdf_directory) or not os.listdir(pdf_directory):
        scraper = NCERTScraper()
        scraper.scrape_data()
        scraper.extract_zip()
    # Process PDFs
    doc_processor = DocumentProcessor(pdf_directory)
    chunks = doc_processor.process_pdfs()
    # Setup Weaviate Collection only if it doesn't exist
    if not weaviate_client.collections.exists("DocumentChunks"):
        doc_processor.setup_weaviate_collection(weaviate_client)
    # Insert Documents
    doc_processor.insert_documents(weaviate_client, chunks)
    return weaviate_client  

if __name__ == "__main__":
    run_backend()
