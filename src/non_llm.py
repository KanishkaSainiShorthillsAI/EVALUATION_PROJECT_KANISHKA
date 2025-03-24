import os
import csv
import time
import weaviate
import google.generativeai as genai
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

class WeaviateClient:
    def __init__(self):
        self.client = self.connect_to_weaviate()

    def connect_to_weaviate(self):
        print("Connecting to Weaviate...")
        return weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv('WEAVIATE_RESTURL'),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv('WEAVIATE_ADMIN'))
        )

    def fetch_stored_vector(self, question):
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        query_vector = embedding_model.encode(question).tolist()
        time.sleep(2)
        return query_vector
    
    def query_documents(self, query_vector, limit=3):
        documents_collection = self.client.collections.get("DocumentChunks")
        results = documents_collection.query.near_vector(near_vector=query_vector, limit=limit)
        return [obj.properties.get("text", "") for obj in results.objects[:limit]]
    
    def close(self):
        self.client.close()
        print("Weaviate connection closed.")

class GeminiQA:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("MODEL"))

    def generate_answer(self, question, contexts):
        prompt = f"""
        You are an AI assistant answering questions strictly based on the provided knowledge base. 

        ## Instructions:
        - Provide a clear and concise answer.
        - Use only the given context for answering.
        - If the answer is not found in the context, explicitly state: "This information is not available in my context."
        - Do not hallucinate or make up any facts.

        ## Context:
        {contexts[0][:500] if len(contexts) > 0 else 'N/A'}
        {contexts[1][:500] if len(contexts) > 1 else 'N/A'}
        {contexts[2][:500] if len(contexts) > 2 else 'N/A'}

        ## Question:
        {question}

        Provide a well-structured response.
        """
        response = self.model.generate_content(prompt)
        return response.text if hasattr(response, "text") else "No answer generated"

class QAProcessor:
    def __init__(self, question_file, output_csv, weaviate_client, gemini_qa):
        self.question_file = question_file
        self.output_csv = output_csv
        self.weaviate_client = weaviate_client
        self.gemini_qa = gemini_qa
        self.existing_questions = self.load_existing_questions()
    
    def load_existing_questions(self):
        existing_questions = set()
        if os.path.exists(self.output_csv):
            with open(self.output_csv, "r", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                next(reader, None)  
                existing_questions = {row[0] for row in reader}
        return existing_questions
    
    def process_questions(self):
        with open(self.question_file, "r", encoding="utf-8") as q_file:
            questions = [line.strip() for line in q_file.readlines() if line.strip()]
        
        with open(self.output_csv, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            if os.stat(self.output_csv).st_size == 0:
                writer.writerow(["Question", "Answer", "Context 1", "Context 2", "Context 3"])
            
            for i, question in enumerate(questions, 1):
                if question in self.existing_questions:
                    continue
                
                print(f"Processing question {i}/{len(questions)}")
                try:
                    query_vector = self.weaviate_client.fetch_stored_vector(question)
                except ValueError as e:
                    print(f"Skipping question due to missing vector: {e}")
                    continue
                
                contexts = self.weaviate_client.query_documents(query_vector)
                answer = self.gemini_qa.generate_answer(question, contexts)
                
                writer.writerow([question, answer] + contexts[:3])
                self.existing_questions.add(question)
                
                time.sleep(2)
        
        print(f"Questions processed and saved to {self.output_csv}")
    
    def close(self):
        self.weaviate_client.close()

if __name__ == "__main__":
    load_dotenv()
    
    weaviate_client = WeaviateClient()
    gemini_qa = GeminiQA()
    qa_processor = QAProcessor("queries.txt", "que_answers.csv", weaviate_client, gemini_qa)
    
    try:
        qa_processor.process_questions()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        qa_processor.close()
