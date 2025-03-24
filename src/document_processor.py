import weaviate
from weaviate.classes.config import Property, DataType
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
 
load_dotenv()  
 
class WeaviateManager:
    def __init__(self):
        self.cluster_url = os.getenv("WEAVIATE_RESTURL")
        self.api_key = os.getenv("WEAVIATE_ADMIN")
        if not self.cluster_url or not self.api_key:
            raise ValueError("ERROR: Missing Weaviate credentials. Check your .env file!")
            
        self.client = self.connect_to_weaviate()
    
    def connect_to_weaviate(self):
        try:
            client = weaviate.connect_to_wcs(
                cluster_url=self.cluster_url,
                auth_credentials=weaviate.auth.AuthApiKey(self.api_key),
            )
            print("Connected to Weaviate successfully!")
            return client
        except Exception as e:
            print(f"Error connecting to Weaviate: {e}")
            raise
    
    def setup_collection(self, collection_name="DocumentChunks"):
        try:
            if self.client.collections.exists(collection_name):
                self.client.collections.delete(collection_name)
                
            self.client.collections.create(
                name=collection_name,
                vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                ]
            )
            print(f"Collection '{collection_name}' created successfully!")
        except Exception as e:
            print(f"Error setting up collection: {e}")
            raise
    
    def insert_documents(self, chunks, embedding_model, collection_name="DocumentChunks"):
        try:
            documents_collection = self.client.collections.get(collection_name)
            with documents_collection.batch.dynamic() as batch:
                for chunk in chunks:
                    vector = embedding_model.get_embedding(chunk["text"])  
                
                    batch.add_object(
                        properties={
                            "text": chunk["text"],  
                            "source": chunk.get("source", "unknown"),  
                        },
                        vector=vector
                    )
            print("Documents inserted successfully!")
        except Exception as e:
            print(f"Error inserting documents: {e}")
            raise
 
 
    
    def close_connection(self):
        if hasattr(self, 'client') and self.client:
            self.client.close()
            print("Weaviate connection closed.")
 
class EmbeddingModel:
    def __init__(self, model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")):
        self.model = SentenceTransformer(model_name)
    
    def get_embedding(self, text):
        return self.model.encode(text).tolist()