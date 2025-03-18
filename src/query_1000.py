import os
import csv
import weaviate
from dotenv import load_dotenv
from chunk import DocumentProcessor
from query_p import QueryProcessor
from book import NCERTScraper


def generate_answers(question_file, output_csv, query_processor):
    """Reads questions from a file, generates answers using Ollama, and appends new ones to a CSV file."""
    
    # Load existing questions from CSV to avoid duplicates
    existing_questions = set()
    if os.path.exists(output_csv):
        with open(output_csv, "r", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)  
            existing_questions = {row[0] for row in reader}  # Store existing questions
    
    # Read all questions from file
    with open(question_file, "r", encoding="utf-8") as q_file:
        questions = [line.strip() for line in q_file.readlines() if line.strip()]
    
    # Open the CSV in append mode
    with open(output_csv, "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        
        for i, question in enumerate(questions, 1):
            if question in existing_questions:
                continue  # Skip already processed questions
            
            print(f"Processing question {i}/{len(questions)}")
            result = query_processor.process_query(question)
            answer = result.get("response", "No answer generated")
            writer.writerow([question, answer])
            existing_questions.add(question)  # Add to processed set
    
    print(f"Remaining questions processed. Appended to {output_csv}")

def main():
    """Main function to orchestrate the entire workflow."""
    try:
        # Load environment variables
        load_dotenv()
        
        pdf_directory = os.path.join("book_pdfs", "extracted")
        question_file = "queries.txt"
        output_csv = "questions_answers.csv"
        
        # Step 1: Connect to Weaviate
        print("Connecting to Weaviate...")
        weaviate_client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv('WEAVIATE_RESTURL'),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv('WEAVIATE_ADMIN'))
        )
        
        # Step 2: Initialize Query Processor
        query_processor = QueryProcessor(weaviate_client)
        
        # Step 3: Generate answers for 1000 questions
        generate_answers(question_file, output_csv, query_processor)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Clean up connection
        if 'weaviate_client' in locals():
            weaviate_client.close()
            print("Connection closed properly")

if __name__ == "__main__":
    main()
