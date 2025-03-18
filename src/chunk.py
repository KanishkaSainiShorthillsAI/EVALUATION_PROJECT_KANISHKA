from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import weaviate
from weaviate.classes.config import Property, DataType
import os
import glob
from sentence_transformers import SentenceTransformer
 
class DocumentProcessor:
    """Class for loading, chunking, and embedding documents."""
    
    def __init__(self, pdf_directory, embedding_model_name='all-MiniLM-L6-v2'):
        """Initialize with PDF directory and embedding model."""
        self.pdf_directory = pdf_directory
        # Initialize the sentence transformer model for embeddings
        self.embedding_model = SentenceTransformer(embedding_model_name)
        print(f"DocumentProcessor initialized with directory: {pdf_directory}")
    
    def get_embedding(self, text):
        """Generate embeddings locally using sentence-transformers."""
        # Convert text to vector and return as a list
        return self.embedding_model.encode(text).tolist()
    
    def process_pdfs(self):
        """Process all PDFs in the directory and return chunks."""
        # Find all PDF files in the directory
        pdf_files = glob.glob(os.path.join(self.pdf_directory, "*.pdf"))
        print(f"Found {len(pdf_files)} PDF files in the directory.")
        
        all_chunks = []
        
        # Process each PDF file
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file}")
            
            try:
                # Load the PDF
                loader = PyPDFLoader(pdf_file)
                pages = loader.load_and_split()
                
                # Create chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                )
                file_chunks = text_splitter.split_documents(pages)
                
                # Add source information
                for chunk in file_chunks:
                    chunk.metadata["source"] = os.path.basename(pdf_file)
                
                # Add to all chunks
                all_chunks.extend(file_chunks)
                
                print(f"  - Processed {len(file_chunks)} chunks from {os.path.basename(pdf_file)}")
            except Exception as e:
                print(f"  - Error processing {pdf_file}: {str(e)}")
        
        print(f"Total chunks processed: {len(all_chunks)}")
        return all_chunks
    
    def setup_weaviate_collection(self, client, collection_name="DocumentChunks"):
        """Set up or reset a Weaviate collection."""
        try:
            # Delete existing collection if it exists
            if client.collections.exists(collection_name):
                client.collections.delete(collection_name)
                
            # Create new collection
            client.collections.create(
                name=collection_name,
                vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                ]
            )
            print(f"Collection '{collection_name}' created successfully!")
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise
    
    def insert_documents(self, client, chunks, collection_name="DocumentChunks"):
        """Insert document chunks into Weaviate."""
        try:
            documents_collection = client.collections.get(collection_name)
            
            # Setup counters
            total_chunks = len(chunks)
            processed_chunks = 0
            
            # Process in batches
            with documents_collection.batch.dynamic() as batch:
                for chunk in chunks:
                    # Create embedding locally
                    vector = self.get_embedding(chunk.page_content)
                    
                    # Add to batch
                    batch.add_object(
                        properties={
                            "text": chunk.page_content,
                            "source": chunk.metadata.get("source", "unknown")
                        },
                        vector=vector
                    )
                    
                    # Update progress
                    processed_chunks += 1
                    if processed_chunks % 10 == 0:
                        print(f"Processed {processed_chunks}/{total_chunks} chunks")
            
            print("Documents inserted successfully!")
        except Exception as e:
            print(f"Error inserting documents: {e}")
            raise