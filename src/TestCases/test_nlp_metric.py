import pandas as pd
import torch
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import score

# Load CSV File (Ensure it contains: Generated Answer, Ground Truth, Context1, Context2, Context3)
file_path = "input_data.csv"
df = pd.read_csv(file_path)

# BLEU Score Calculation
def compute_bleu(references, candidate):
    reference_tokens = [ref.split() for ref in references]
    candidate_tokens = candidate.split()

    # Smoothing for short sentences
    chencherry = SmoothingFunction()
    return sentence_bleu(reference_tokens, candidate_tokens, 
                         weights=(0.5, 0.5, 0, 0),  # Unigram & bigram focus
                         smoothing_function=chencherry.method1) * 100

# ROUGE Score Calculation
def compute_rouge(references, candidate):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    # Compute scores against each reference and take the max
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

# BERTScore Calculation
def compute_bertscore(references, candidate):
    # Compute similarity for each reference separately
    scores = []
    for ref in references:
        _, _, F1 = score([candidate], [ref], lang="en", verbose=False)
        scores.append(F1.item() * 100)  # Convert tensor to scalar
    return max(scores)  # Take max similarity from all references

# Track total scores for overall average
total_bleu, total_rouge1, total_rouge2, total_rougeL, total_bertscore = 0, 0, 0, 0, 0
num_samples = len(df)

# Iterate over all answers in CSV and compute scores
for index, row in df.iterrows():
    generated_answer = row["Generated Answer"]
    ground_truth = row["Ground Truth"]
    
    # Combine ground truth and contexts as references
    references = [ground_truth] + [row["Context1"], row["Context2"], row["Context3"]]
    references = [ref for ref in references if pd.notna(ref)]  # Remove NaN values

    # Compute Scores
    bleu = compute_bleu(references, generated_answer)
    rouge_scores = compute_rouge(references, generated_answer)
    bertscore = compute_bertscore(references, generated_answer)

    # Sum up for overall average
    total_bleu += bleu
    total_rouge1 += rouge_scores["ROUGE-1"]
    total_rouge2 += rouge_scores["ROUGE-2"]
    total_rougeL += rouge_scores["ROUGE-L"]
    total_bertscore += bertscore

# Compute overall averages
avg_bleu = total_bleu / num_samples
avg_rouge1 = total_rouge1 / num_samples
avg_rouge2 = total_rouge2 / num_samples
avg_rougeL = total_rougeL / num_samples
avg_bertscore = total_bertscore / num_samples

# Print Final Averages
print("\nOverall Evaluation Results:")
print(f"Average BLEU Score: {avg_bleu:.2f}")
print(f"Average ROUGE-1 Score: {avg_rouge1:.2f}")
print(f"Average ROUGE-2 Score: {avg_rouge2:.2f}")
print(f"Average ROUGE-L Score: {avg_rougeL:.2f}")
print(f"Average BERTScore: {avg_bertscore:.2f}")
