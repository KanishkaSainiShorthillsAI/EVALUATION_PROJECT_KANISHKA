import streamlit as st
import weaviate
import os
import json
import logging
import time
from dotenv import load_dotenv
from query_processor import QueryProcessor
from document_processor import WeaviateManager  # Updated import

class WeaviateQuerySystem:
    def __init__(self):
        load_dotenv()
        self.cluster_url = os.getenv("WEAVIATE_RESTURL")
        self.api_key = os.getenv("WEAVIATE_ADMIN")
        self.collection_name = os.getenv("WEAVIATE_COLLECTION", "DocumentChunks")
        self.log_file = "query_log.json"
        
        self.setup_logging()
        self.logger.info("Frontend page loaded.")
        self.connect_to_weaviate()
    
    def setup_logging(self):
        """Set up logging for the system."""
        logging.basicConfig(
            level=logging.INFO, 
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("query_system.log"),  # Log to file
                logging.StreamHandler()  # Log to console
            ]
        )
        self.logger = logging.getLogger()

    def connect_to_weaviate(self):
        """Establish connection to Weaviate."""
        try:
            self.logger.info("Attempting to connect to Weaviate...")

            self.weaviate_manager = WeaviateManager()  
            self.query_processor = QueryProcessor(self.weaviate_manager.client)  
            
            self.logger.info("Successfully connected to Weaviate!")
        except Exception as e:
            self.logger.error(f"Failed to connect to Weaviate: {e}")
            st.error("Error connecting to Weaviate. Please check your configuration.")

    def log_query(self, query, result, context, duration):
        """Logs queries and responses to a JSON file."""
        log_entry = {
            "query": query,
            "result": result,
            "context": context,
            "time_taken": f"{duration:.2f} seconds"
        }

        logs = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                self.logger.warning("⚠️ Log file is corrupted. Creating a new one.")

        logs.append(log_entry)

        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=4)
        
        self.logger.info(f"Logged query: '{query}' | Time taken: {duration:.2f} sec")

    def load_previous_queries(self):
        """Loads previous queries from the log file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                self.logger.warning("⚠️ Failed to load previous queries due to JSON decode error.")
                return []
        return []

    def process_query(self, query):
        """Processes the user query and fetches the result from Weaviate."""
        if not query:
            st.warning("⚠️ Please enter a query!")
            return

        st.write("🔍 Searching...")
        start_time = time.time()
        
        try:
            self.logger.info(f"Received query: '{query}'")

            self.logger.info("Creating embedding for the query...")
            result = self.query_processor.process_query(query)

            self.logger.info("Retrieving relevant document chunks from Weaviate...")
            context = result.get("context", "No relevant documents found.")
            
            self.logger.info("Generating answer using Ollama...")
            response = result.get("response", "No answer available.")

            end_time = time.time()
            duration = end_time - start_time

            self.logger.info("Query processed successfully!")

            st.subheader("Answer:")
            st.write(response)

            with st.expander("Show Retrieved Context"):
                st.write(context)

            self.log_query(query, response, context, duration)

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            st.error(f"An error occurred while processing your query: {str(e)}")

    def display_query_history(self):
        """Displays the previous queries in the sidebar."""
        st.sidebar.title("Query History")
        previous_queries = self.load_previous_queries()
        for entry in previous_queries[-5:]:  
            with st.sidebar.expander(entry["query"]):
                st.write("Answer:", entry["result"])
                st.write("Context:", entry["context"])

    def close_connection(self):
        """Closes the Weaviate connection if it exists."""
        if hasattr(self, "weaviate_manager") and self.weaviate_manager:
            self.weaviate_manager.close_connection()
            self.logger.info("Weaviate connection closed.")

def main():
    """Main function to run the Streamlit app."""
    system = WeaviateQuerySystem()

    st.title("📚 Political Science NCERT Query System")
    query = st.text_input("Enter your query:", "")

    if st.button("Search"):
        system.process_query(query)

    system.display_query_history()
    system.close_connection()

if __name__ == "__main__":
    main()
