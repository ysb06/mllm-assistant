import os
import pickle
from typing import Any, Dict, List, Union

import nltk
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from bert_score import score

nltk.download("punkt")
nltk.download("punkt_tab")


def calculate_bleu_score(reference: str, hypothesis: str) -> float:
    """
    reference: 정답 문장 (expected_answer)
    hypothesis: 모델 답변 (model_answer)
    """
    # 간단히 whitespace 토크나이징. 필요에 따라 더 정교한 토크나이저 사용 가능.
    reference_tokens = nltk.word_tokenize(reference)
    hypothesis_tokens = nltk.word_tokenize(hypothesis)

    # BLEU 계산 (여기서는 sentence_bleu사용)
    # smoothingFunction은 BLEU 계산 시 0 나누기 오류 회피 및 점수 안정화에 도움.
    smoothie = SmoothingFunction().method4
    score = sentence_bleu(
        [reference_tokens], hypothesis_tokens, smoothing_function=smoothie
    )
    return score


def test_bleu(raw_path: str):
    with open(raw_path, "rb") as f:
        results: Dict[str, str] = pickle.load(f)

    total_score = 0.0
    count = 0
    for result in results.values():
        expected_answer = result["expected_answer"]
        model_answer = result["model_answer"]
        bleu = calculate_bleu_score(expected_answer, model_answer)
        total_score += bleu
        count += 1

    avg_bleu = total_score / count if count > 0 else 0.0
    print(f"Average BLEU score: {avg_bleu:.4f}")


def calculate_bertscore(
    references: List[str], hypotheses: List[str], model_type: str = "bert-base-uncased"
):
    """
    references와 hypotheses는 문장 리스트 형태여야 합니다.
    model_type으로 사용할 언어모델을 지정할 수 있습니다.
    """
    P, R, F1 = score(hypotheses, references, model_type=model_type)
    # F1.mean().item()로 평균 F1 스코어를 얻을 수 있습니다.
    return P.mean().item(), R.mean().item(), F1.mean().item()


def test_bertscore(raw_path: str):
    with open(raw_path, "rb") as f:
        results = pickle.load(f)

    references = []
    hypotheses = []
    for result in results.values():
        references.append(result["expected_answer"])
        hypotheses.append(result["model_answer"])

    P, R, F1 = score(hypotheses, references, model_type="bert-base-uncased")
    print(
        f"BERTScore - P: {P.mean().item():.4f}, R: {R.mean().item():.4f}, F1: {F1.mean().item():.4f}"
    )


if __name__ == "__main__":
    # test_bleu("./output/results-normal-gpt-4o.pkl")
    print("== Normal data:")
    test_bertscore("./output/results-normal-gpt-4o.pkl")

    print("== Attacked data:")
    test_bertscore("./output/results-atk-velocity-gpt-4o.pkl")
