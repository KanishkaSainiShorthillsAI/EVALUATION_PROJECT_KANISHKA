import streamlit as st
import weaviate
import requests
import json
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

CHAT_HISTORY_FILE = "chat_history.json"

def load_environment():
    """Load environment variables."""
    load_dotenv()

def initialize_weaviate_client():
    """Connect to the Weaviate cloud instance."""
    return weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_RESTURL"),
        auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_ADMIN"))
    )

def initialize_embedding_model():
    """Initialize the sentence transformer model."""
    return SentenceTransformer("all-MiniLM-L6-v2")

def query_weaviate(client, query_embedding, collection_name="DocumentChunks", limit=3):
    """Perform vector search in Weaviate."""
    documents_collection = client.collections.get(collection_name)
    results = documents_collection.query.near_vector(near_vector=query_embedding, limit=limit)
    return "\n\n".join([obj.properties["text"] for obj in results.objects])

def query_ollama(prompt, model="llama2"):
    """Send a query to Ollama for response generation."""
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "No response generated")
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def load_chat_history():
    """Load chat history from file."""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    return []

def save_chat_history(chat_history):
    """Save chat history to file."""
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(chat_history, file, indent=4)

def main():
    """Main function to run the Streamlit app."""
    load_environment()
    st.set_page_config(page_title="Weaviate Q&A", layout="wide")
    st.title("📚 AI-Powered Q&A for NCERT Political Science (Class 6-10)")

    client = initialize_weaviate_client()
    embedding_model = initialize_embedding_model()

    # Load chat history from file
    chat_history = load_chat_history()

    # Display previous queries in sidebar
    st.sidebar.title("📝 Previous Queries")
    for entry in chat_history:
        with st.sidebar.expander(f"{entry['query']}"):
            st.write(entry['answer'])

    query = st.text_input("🔍 Ask a question:")

    if st.button("Get Answer"):
        if query:
            with st.spinner("Searching for the best answer..."):
                query_embedding = embedding_model.encode(query).tolist()
                context = query_weaviate(client, query_embedding)

                ollama_prompt = f"""
                Answer this question: {query}
                
                Provide a clear and concise answer based only on the given knowledge base.
                """
                ollama_response = query_ollama(ollama_prompt)

            # Store query and answer history in a persistent file
            chat_entry = {"query": query, "answer": ollama_response}
            chat_history.append(chat_entry)
            save_chat_history(chat_history)  # Save updated history

            st.subheader("🤖 AI Answer:")
            st.markdown(f"""<div style="background-color:#f9f9f9;padding:10px;border-radius:5px;">
                        {ollama_response}</div>""", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter a question!")

    client.close()

if __name__ == "__main__":
    main()
