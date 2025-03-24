# Political Science NCERT Query System
 
## Overview
The **Political Science NCERT Query System** is a Streamlit-based application that allows users to search political science content from NCERT books. It leverages **Weaviate** for vector search, **Ollama** for query processing, and maintains a query log for tracking previous searches.
 
## Features
- **Weaviate Integration:** Retrieves relevant document chunks based on embeddings.
- **Ollama-based Query Processing:** Generates answers using contextual understanding.
- **Logging Mechanism:** Stores previous queries and responses in a JSON log file.
- **Streamlit UI:** Simple and interactive frontend for user interaction.
- **Sidebar Query History:** Displays past queries for easy reference.
 
---
 
## Setup & Installation
 
### 1️⃣ **Clone the Repository**
```bash
git clone <repository-url>
cd political science-ncert-query-system
```
 
### 2️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```
 
### 3️⃣ **Set Up Environment Variables**
Create a `.env` file in the root directory and add:
```plaintext
GENAI_API_KEY="your-gemini-api-key"
GENAI_MODEL="gemini-model-name"
WEAVIATE_RESTURL=<your-weaviate-cluster-url>
WEAVIATE_ADMIN=<your-weaviate-api-key>
WEAVIATE_COLLECTION=DocumentChunks  # Default collection name
EMBEDDING_MODEL="embedding-model-name"
LIMIT=3
OLLAMA_MODEL="ollama-model-name"
OLLAMA_URL="ollama-local-host-url"
```
 
### 4️⃣ **Run the Application**
```bash
streamlit run app.py --server.fileWatcherType none
```
 
---
 
## Usage Guide
1. **Enter a query** related to NCERT political science topics in the text box.
2. Click **"Search"** to retrieve the most relevant content.
3. The system displays an **AI-generated response** based on retrieved context.
4. Expand **"Show Retrieved Context"** to view supporting document excerpts.
5. The **query history** is accessible in the sidebar for reference.
 
---
 
## Query-Processing Project Structure
```
📂 political science-ncert-query-system
│── 📄 app.py                  # Streamlit application
│── 📄 query_processor.py      # Handles query embeddings & retrieval
│── 📄 document_processor.py   # Manages Weaviate database operations
│── 📄 requirements.txt        # Dependencies
│── 📄 .env                    # Environment variables
│── 📄 query_log.json          # Stores query history
```
 
---
 
## Logging & Query History
- All queries, responses, and retrieval contexts are stored in `query_log.json`.
- If the log file becomes corrupted, the system resets it automatically.
 
---
 
## Troubleshooting
### 🔹 Issue: **Weaviate Connection Fails**
Ensure the `WEAVIATE_RESTURL` and `WEAVIATE_ADMIN` in `.env` are correct.
 
### 🔹 Issue: **No Response from Query**
Check if the query is relevant to the indexed NCERT content.
Ensure Weaviate is properly configured and running.
 
### 🔹 Issue: **Streamlit App Not Launching**
Confirm that all dependencies are installed (`pip install -r requirements.txt`).
Check if the `.env` file exists with valid credentials.

