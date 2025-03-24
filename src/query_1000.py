import os
import csv
import weaviate
from dotenv import load_dotenv
from query_processor import QueryProcessor

class WeaviateManager:
    def __init__(self):
        load_dotenv()
        self.client = self.connect_to_weaviate()

    def connect_to_weaviate(self):
        try:
            print("Connecting to Weaviate...")
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=os.getenv('WEAVIATE_RESTURL'),
                auth_credentials=weaviate.auth.AuthApiKey(os.getenv('WEAVIATE_ADMIN'))
            )
            return client
        except Exception as e:
            print(f"Error connecting to Weaviate: {e}")
            return None

    def close_connection(self):
        if self.client:
            self.client.close()
            print("Weaviate connection closed.")

class AnswerGenerator:
    def __init__(self, question_file, output_csv, query_processor):
        self.question_file = question_file
        self.output_csv = output_csv
        self.query_processor = query_processor
        self.existing_questions = self.load_existing_questions()
    
    def load_existing_questions(self):
        existing_questions = set()
        if os.path.exists(self.output_csv):
            with open(self.output_csv, "r", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                next(reader, None)  
                existing_questions = {row[0] for row in reader} 
        return existing_questions

    def generate_answers(self):
        with open(self.question_file, "r", encoding="utf-8") as q_file:
            questions = [line.strip() for line in q_file.readlines() if line.strip()]
        
        with open(self.output_csv, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            for i, question in enumerate(questions, 1):
                if question in self.existing_questions:
                    continue  
                
                print(f"Processing question {i}/{len(questions)}")
                result = self.query_processor.process_query(question)
                answer = result.get("response", "No answer generated")
                writer.writerow([question, answer])
                self.existing_questions.add(question)  
        
        print(f"All questions processed. Appended to {self.output_csv}")

class MainApp:
    def __init__(self):
        self.weaviate_manager = WeaviateManager()
        self.query_processor = QueryProcessor(self.weaviate_manager.client)
        self.answer_generator = AnswerGenerator("queries.txt", "questions_answers.csv", self.query_processor)
    
    def run(self):
        try:
            self.answer_generator.generate_answers()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.weaviate_manager.close_connection()

if __name__ == "__main__":
    app = MainApp()
    app.run()
