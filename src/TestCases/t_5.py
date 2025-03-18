import os
import unittest
import weaviate
from chunk import DocumentProcessor
from weaviate.auth import AuthApiKey
 
class TestDocumentProcessor(unittest.TestCase):
 
    @classmethod
    def setUpClass(cls):
        """Set up Weaviate client and test directory before running tests."""
        cls.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv('WEAVIATE_RESTURL'),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv('WEAVIATE_ADMIN'))
        )
        cls.pdf_directory = "testingDirectory"  
        cls.processor = DocumentProcessor(pdf_directory=cls.pdf_directory)
 
        if not os.path.exists(cls.pdf_directory):
            os.makedirs(cls.pdf_directory)
 
        # Ensure at least one PDF is in the test directory
        test_pdf_path = os.path.join(cls.pdf_directory, "fees101.pdf")
        if not os.path.exists(test_pdf_path):
            with open(test_pdf_path, "wb") as f:
                f.write(b"%PDF-1.4\n%Test PDF Content\n")
 
 
    """Test that DocumentProcessor initializes correctly."""
    def test_document_processor_initialization(self):
        self.assertEqual(self.processor.pdf_directory, self.pdf_directory)
        self.assertIsNotNone(self.processor.embedding_model)
 
 
    """Test that get_embedding() returns a valid embedding."""
    def test_get_embedding(self):
        sample_text = "This is a test sentence."
        embedding = self.processor.get_embedding(sample_text)
        
        self.assertIsInstance(embedding, list)  
        self.assertGreater(len(embedding), 0)  
 
 
    """Test processing a valid PDF and ensure chunks are generated."""
    def test_process_pdfs_with_valid_pdf(self):
        chunks = self.processor.process_pdfs()
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)  
        self.assertIn("source", chunks[0].metadata)  
 
 
    """Test if Weaviate collection is created successfully."""
    def test_setup_weaviate_collection(self):
        self.processor.setup_weaviate_collection(self.client, "TestCollection")
        self.assertTrue(self.client.collections.exists("TestCollection"))
 
 
    """Test inserting chunks into Weaviate."""
    def test_insert_documents(self):
        chunks = self.processor.process_pdfs()
        self.processor.insert_documents(self.client, chunks, "TestCollection")
 
        collection = self.client.collections.get("TestCollection")
        results = collection.aggregate.over_all(total_count=True)
        self.assertGreater(results.total_count, 0)
 
 
    """Test recreating a Weaviate collection, inserting empty chunks, and retrieving inserted documents."""
    def test_weaviate_collection_operations(self):
        # Step 1: Recreate the collection (should be idempotent)
        self.processor.setup_weaviate_collection(self.client, "TestCollection")
        self.processor.setup_weaviate_collection(self.client, "TestCollection")  # Run again
        self.assertTrue(self.client.collections.exists("TestCollection"))
 
        # Step 2: Insert empty chunks (should not raise an error)
        empty_chunks = []
        try:
            self.processor.insert_documents(self.client, empty_chunks, "TestCollection")
        except Exception as e:
            self.fail(f"Inserting empty chunks raised an exception: {e}")
 
        # Step 3: Insert real chunks and verify retrieval
        chunks = self.processor.process_pdfs()
        self.processor.insert_documents(self.client, chunks, "TestCollection")
 
        collection = self.client.collections.get("TestCollection")
        results = collection.query.fetch_objects(limit=1)  
        self.assertGreater(len(results.objects), 0)  # Ensure at least one document is retrievable    
 
 
    @classmethod
    def tearDownClass(cls):
        """Clean up Weaviate collections after tests."""
        if cls.client.collections.exists("TestCollection"):
            cls.client.collections.delete("TestCollection")
        cls.client.close()
        print("Cleaned up test collections.")
 
# Run Tests
if __name__ == "__main__":
    unittest.main()
 