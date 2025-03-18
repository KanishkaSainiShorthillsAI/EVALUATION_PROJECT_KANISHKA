### stream.py 
   - Runs the Streamlit UI for interacting with the chatbot.
   - Accepts user queries and retrieves answers from Weaviate and Llama2.
### main.py
   - Orchestrator to NCERTScraper, DocumentProcessor, QueryProcessor
   
## To run this project, follow these steps:
   - `Set Up the Environment` – Install necessary dependencies and ensure all required Python packages are available. Environment variables should be configured properly for accessing external services like Weaviate.
   
   - `Scrape and Process Data` – The NCERTScraper extracts content from NCERT textbooks, and DocumentProcessor structures it into smaller chunks for efficient retrieval. These chunks are stored in Weaviate, a vector database for semantic search.
   
   - `Run the Chatbot UI` – Streamlit provides an interface where users can ask questions. The QueryProcessor retrieves relevant context from Weaviate, and an LLM (like Llama2) generates answers based on retrieved content.
   
   - `Evaluate the Model` – The evaluation script compares chatbot-generated responses with expected answers. It calculates BLEU, ROUGE, and BERTScore to assess the model's accuracy.


