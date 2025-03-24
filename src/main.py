import os
import fitz  # PyMuPDF
import weaviate
from dotenv import load_dotenv
from document_processor import WeaviateManager, EmbeddingModel
from scrapeNCERT import NCERTScraper
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

class PDFProcessor:
    def __init__(self, pdf_directory):
        self.pdf_directory = pdf_directory
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    def extract_text(self):
        chunks = []
        
        if not os.path.exists(self.pdf_directory):
            print(f"Directory '{self.pdf_directory}' does not exist.")
            return chunks
        
        for filename in os.listdir(self.pdf_directory):
            if filename.endswith(".pdf"):
                file_path = os.path.join(self.pdf_directory, filename)
                print(f"📄 Processing {file_path}...")
                
                try:
                    doc = fitz.open(file_path)
                    full_text = "\n".join(page.get_text("text") for page in doc)
                    text_chunks = self.text_splitter.split_text(full_text)
                    
                    for chunk in text_chunks:
                        chunks.append({"text": chunk, "source": filename})
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        return chunks

class BackendRunner:
    def __init__(self, pdf_directory="book_pdfs/extracted", collection_name="DocumentChunks"):
        self.pdf_directory = pdf_directory
        self.collection_name = collection_name
        self.scraper = NCERTScraper()
        self.weaviate_manager = WeaviateManager()
        self.embedding_model = EmbeddingModel()
        self.client = None

    def setup_weaviate(self):
        try:
            self.client = self.weaviate_manager.client
            if not self.client:
                raise ConnectionError("Failed to connect to Weaviate.")
            self.weaviate_manager.setup_collection(self.collection_name)
        except Exception as e:
            print(f"Error: {e}")
            return False
        return True
    
    def run(self):
        if not os.path.exists(self.pdf_directory) or not os.listdir(self.pdf_directory):
            self.scraper.scrape_data()
            self.scraper.extract_zip()

        if not self.setup_weaviate():
            return None

        pdf_processor = PDFProcessor(self.pdf_directory)
        chunks = pdf_processor.extract_text()
        
        if not chunks:
            print("No text extracted from PDFs.")
            return None

        try:
            self.weaviate_manager.insert_documents(chunks, self.embedding_model, self.collection_name)
        except Exception as e:
            print(f"Error inserting documents into Weaviate: {e}")
            return None
        
        return self.client

if __name__ == "__main__":
    backend = BackendRunner()
    backend.run()
