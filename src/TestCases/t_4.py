import unittest
import weaviate
import requests
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()
 
# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
 
class TestWeaviateQnA(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Connect to Weaviate before running tests"""
        cls.client =weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv('WEAVIATE_RESTURL'),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv('WEAVIATE_ADMIN'))
        )
 
    @classmethod
    def tearDownClass(cls):
        """Close Weaviate connection after tests"""
        cls.client.close()
    
    def test_embedding_generation(self):
        """Test if SentenceTransformer generates valid embeddings."""
        query = "What is artificial intelligence?"
        embedding = embedding_model.encode(query).tolist()
        self.assertIsInstance(embedding, list)
        self.assertGreater(len(embedding), 0)
    
    def test_weaviate_connection(self):
        """Test if Weaviate client is connected."""
        self.assertIsNotNone(self.client)
    
    def test_query_weaviate(self):
        """Test if Weaviate returns valid search results."""
        query_embedding = embedding_model.encode("Test Query").tolist()
        documents_collection = self.client.collections.get("DocumentChunks")
        results = documents_collection.query.near_vector(near_vector=query_embedding, limit=3)
        self.assertIsInstance(results.objects, list)
    
    def test_ollama_request(self):
        """Test if the Ollama API request returns a valid response."""
        url = "http://localhost:11434/api/generate"
        payload = {"model": "llama2", "prompt": "Hello AI!", "stream": False}
        response = requests.post(url, json=payload)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("response", json_response)
    
    def test_query_ollama(self):
        """Test if Ollama API returns expected output format."""
        def query_ollama(prompt, model="llama2"):
            url = "http://localhost:11434/api/generate"
            payload = {"model": model, "prompt": prompt, "stream": False}
            response = requests.post(url, json=payload)
            return response.json().get("response", "No response generated")
        
        result = query_ollama("What is AI?")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
if __name__ == "__main__":
    unittest.main()