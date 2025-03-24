import pandas as pd
import torch
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import score

class TextEvaluator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_csv(file_path)
        self.evaluation_results = []
        self.total_bleu = 0
        self.total_rouge1 = 0
        self.total_rouge2 = 0
        self.total_rougeL = 0
        self.total_bertscore = 0
        self.num_samples = len(self.df)
    
    def compute_bleu(self, references, candidate):
        reference_tokens = [ref.split() for ref in references]
        candidate_tokens = candidate.split()
        chencherry = SmoothingFunction()
        return sentence_bleu(reference_tokens, candidate_tokens, 
                             weights=(0.5, 0.5, 0, 0), 
                             smoothing_function=chencherry.method1) * 100

    def compute_rouge(self, references, candidate):
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        rouge_1_scores, rouge_2_scores, rouge_l_scores = [], [], []
        
        for ref in references:
            scores = scorer.score(ref, candidate)
            rouge_1_scores.append(scores['rouge1'].fmeasure * 100)
            rouge_2_scores.append(scores['rouge2'].fmeasure * 100)
            rouge_l_scores.append(scores['rougeL'].fmeasure * 100)

        return {
            "ROUGE-1": max(rouge_1_scores),
            "ROUGE-2": max(rouge_2_scores),
            "ROUGE-L": max(rouge_l_scores)
        }

    def compute_bertscore(self, references, candidate):
        scores = []
        for ref in references:
            _, _, F1 = score([candidate], [ref], lang="en", verbose=False)
            scores.append(F1.item() * 100)
        return max(scores)

    def evaluate(self):
        for _, row in self.df.iterrows():
            generated_answer = row["Generated Answer"]
            ground_truth = row["Ground Truth"]
            
            references = [ground_truth] + [row["Context1"], row["Context2"], row["Context3"]]
            references = [ref for ref in references if pd.notna(ref)]
            
            bleu = self.compute_bleu(references, generated_answer)
            rouge_scores = self.compute_rouge(references, generated_answer)
            bertscore = self.compute_bertscore(references, generated_answer)
            
            self.evaluation_results.append({
                "Generated Answer": generated_answer,
                "Ground Truth": ground_truth,
                "Context1": row["Context1"],
                "Context2": row["Context2"],
                "Context3": row["Context3"],
                "BLEU Score": bleu,
                "ROUGE-1": rouge_scores["ROUGE-1"],
                "ROUGE-2": rouge_scores["ROUGE-2"],
                "ROUGE-L": rouge_scores["ROUGE-L"],
                "BERTScore": bertscore
            })
            
            self.total_bleu += bleu
            self.total_rouge1 += rouge_scores["ROUGE-1"]
            self.total_rouge2 += rouge_scores["ROUGE-2"]
            self.total_rougeL += rouge_scores["ROUGE-L"]
            self.total_bertscore += bertscore

    def compute_averages(self):
        return {
            "Average BLEU Score": self.total_bleu / self.num_samples,
            "Average ROUGE-1 Score": self.total_rouge1 / self.num_samples,
            "Average ROUGE-2 Score": self.total_rouge2 / self.num_samples,
            "Average ROUGE-L Score": self.total_rougeL / self.num_samples,
            "Average BERTScore": self.total_bertscore / self.num_samples
        }

    def save_results(self, output_file="evaluation_results.csv"):
        pd.DataFrame(self.evaluation_results).to_csv(output_file, index=False)
        print(f"Evaluation results saved to {output_file}")

    def run(self):
        self.evaluate()
        averages = self.compute_averages()
        self.save_results()
        print("\nOverall Evaluation Results:")
        for key, value in averages.items():
            print(f"{key}: {value:.2f}")

if __name__ == "__main__":
    evaluator = TextEvaluator("que_answers.csv")
    evaluator.run()
