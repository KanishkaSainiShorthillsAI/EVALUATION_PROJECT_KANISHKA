import pandas as pd
import google.generativeai as genai  
import time  
import json  
import re 
import os  

class GeminiEvaluator:
    def __init__(self, api_key, input_file="que_answers.csv", output_file="testans_results.csv"):
        self.api_key = api_key
        self.input_file = input_file
        self.output_file = output_file
        self.processed_questions = set()
        self.results = []
        self.existing_results = pd.DataFrame()
        genai.configure(api_key=self.api_key)
        self.load_existing_results()
        self.load_input_data()
    
    def load_input_data(self):
        self.df = pd.read_csv(self.input_file)
        self.df.columns = self.df.columns.str.strip()
        self.df = self.df.dropna(subset=["Generated Answer", "Ground Truth"])
    
    def load_existing_results(self):
        if os.path.exists(self.output_file) and os.path.getsize(self.output_file) > 0:
            try:
                self.existing_results = pd.read_csv(self.output_file)
                if "Generated Answer" in self.existing_results.columns:
                    self.processed_questions = set(self.existing_results["Generated Answer"].dropna().astype(str).str.strip())
                print(f"Found {len(self.processed_questions)} previously processed answers")
            except Exception as e:
                print(f"Error reading existing results file: {e}")
                os.rename(self.output_file, f"{self.output_file}_backup_{int(time.time())}.csv")
                print("Backed up corrupted results file and starting fresh")
    
    @staticmethod
    def clean_json_response(response_text):
        response_text = response_text.strip()
        response_text = re.sub(r"```json\s*|\s*```", "", response_text)
        try:
            scores = json.loads(response_text)
            if isinstance(scores, dict):
                return {
                    "Faithfulness": float(scores.get("Faithfulness", 0)),
                    "Precision": float(scores.get("Precision", 0)),
                    "Recall": float(scores.get("Recall", 0)),
                    "Relevancy": float(scores.get("Relevancy", 0)),
                }
        except json.JSONDecodeError:
            print(f"❌ JSON Decode Error: {response_text}")
        return {"Faithfulness": 0, "Precision": 0, "Recall": 0, "Relevancy": 0}
    
    def evaluate_with_gemini(self, question, generated_answer, ground_truth, contexts):
        prompt = f"""
        You are evaluating a question-answering system based on four key metrics:
        Provide scores (0-1) in **valid JSON format** as follows:
        ```json
        {{"Faithfulness": 0.85, "Precision": 0.5, "Recall": 0.7, "Relevancy": 0.3}}
        ```
        **Input Data:**
        - Question: {question}
        - Generated Answer: {generated_answer}
        - Ground Truth: {ground_truth}
        - Contexts: {contexts}
        """
        try:
            model = genai.GenerativeModel(os.getenv("MODEL"))
            response = model.generate_content(prompt)
            return self.clean_json_response(response.text)
        except Exception as e:
            print(f"Error processing Gemini API: {e}")
            return {"Faithfulness": 0, "Precision": 0, "Recall": 0, "Relevancy": 0}
    
    def process_entries(self):
        for index, row in self.df.iterrows():
            try:
                generated_answer = str(row["Generated Answer"]).strip()
                ground_truth = str(row["Ground Truth"]).strip()
                question = str(row.get("Question", "")).strip()
                
                if not generated_answer or generated_answer in self.processed_questions:
                    print(f"Skipping already processed or empty answer at index {index}")
                    continue
                
                references = [str(row[f"Context {i}"].strip()) for i in range(1, 5) if f"Context {i}" in row and pd.notna(row[f"Context {i}"])]
                print(f"Processing question {index + 1}...")
                
                scores = self.evaluate_with_gemini(question, generated_answer, ground_truth, references)
                
                self.results.append({
                    "Question": question,
                    "Generated Answer": generated_answer,
                    "Ground Truth": ground_truth,
                    "Faithfulness": round(scores["Faithfulness"], 2),
                    "Precision": round(scores["Precision"], 2),
                    "Recall": round(scores["Recall"], 2),
                    "Relevancy": round(scores["Relevancy"], 2)
                })
                
                self.processed_questions.add(generated_answer)
                
                if len(self.results) % 5 == 0:
                    self.save_results()
                    print(f"Saved {len(self.results)} new results")
                
                time.sleep(5)
            except Exception as e:
                print(f"Error processing row {index}: {e}")
    
    def save_results(self):
        if self.results:
            current_results_df = pd.DataFrame(self.results)
            if not self.existing_results.empty:
                combined_df = pd.concat([self.existing_results, current_results_df], ignore_index=True).drop_duplicates(subset=["Generated Answer"])
                combined_df.to_csv(self.output_file, index=False)
            else:
                current_results_df.to_csv(self.output_file, index=False)
    
    def run_evaluation(self):
        self.process_entries()
        self.save_results()
        print(f"✅ Evaluation completed. Processed {len(self.results)} new entries.")


if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    evaluator = GeminiEvaluator(api_key)
    evaluator.run_evaluation()
