import pickle
from typing import Callable, Dict, List, Optional, Tuple

import nltk
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from bert_score import score

import pandas as pd
from torch import Tensor
from tqdm import tqdm

import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd

nltk.download("punkt")
nltk.download("punkt_tab") # 필요 없으므로 주석처리


def load_data(raw_path: str) -> List[Dict[str, str]]:
    with open(raw_path, "rb") as f:
        raw_data: Dict[int, Dict[str, str]] = pickle.load(f)
    sorted_items = sorted(raw_data.items(), key=lambda x: x[0])
    data_list = [v for _, v in sorted_items]
    return data_list


def calculate_bleu_score(reference: str, hypothesis: str) -> float:
    reference_tokens = nltk.word_tokenize(reference)
    hypothesis_tokens = nltk.word_tokenize(hypothesis)

    smoothie = SmoothingFunction().method4
    score_val = sentence_bleu(
        [reference_tokens], hypothesis_tokens, smoothing_function=smoothie
    )
    return score_val


def test_bleu(data: List[Dict[str, str]]) -> List[float]:
    scores = []
    for result in data:
        expected_answer = result["expected_answer"]
        model_answer = result["model_answer"]
        bleu = calculate_bleu_score(expected_answer, model_answer)
        scores.append(bleu)

    if scores:
        avg_bleu = sum(scores) / len(scores)
        print(f"Average BLEU score: {avg_bleu:.4f}")
    else:
        print("No scores available.")

    return scores


def get_bertscore(data: List[Dict[str, str]]) -> List[float]:
    references = []
    hypotheses = []
    for result in data:
        references.append(result["expected_answer"])
        hypotheses.append(result["model_answer"])

    P, R, F1 = score(hypotheses, references, model_type="bert-base-uncased")
    print(
        f"BERTScore - P: {P.mean().item():.4f}, R: {R.mean().item():.4f}, F1: {F1.mean().item():.4f}"
    )
    return F1.tolist()

def get_bleu_score(data: List[Dict[str, str]]) -> List[float]:
    references = []
    hypotheses = []
    for result in data:
        references.append(result["expected_answer"])
        hypotheses.append(result["model_answer"])

    scores = []
    for reference, hypothesis in zip(references, hypotheses):
        scores.append(calculate_bleu_score(reference, hypothesis))

    return scores


def analyze_score(
    score_method: Callable[[List[Dict[str, str]]], List[Tensor]],
    target_list: List[Tuple[str, List[Dict[str, str]]]],
    sample_target: Optional[List[int]] = None,
):
    data = {}
    for name, data_list in tqdm(target_list):
        target_score = score_method(data_list)
        data[name] = target_score

    df = pd.DataFrame(data)
    if sample_target is not None:
        print(f"Sampling from {len(df)} rows...")
        df = df.iloc[sample_target]
        print(f"After sampling: {len(df)} rows")
    print(df.describe())

    # ANOVA 분석을 위해 Long format으로 변환
    df_melt = df.melt(var_name="group", value_name="score")

    # OLS 모델 적합 및 ANOVA
    model = ols("score ~ C(group)", data=df_melt).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    print("\nANOVA results:")
    print(anova_table)

    # 사후 분석: Tukey's HSD, groups별로 점수 분포를 비교
    tukey = pairwise_tukeyhsd(
        endog=df_melt["score"], groups=df_melt["group"], alpha=0.05
    )
    print("\nTukey's HSD Post-hoc Test:")
    print(tukey)


if __name__ == "__main__":
    atk_non_data = load_data("./output/results-normal-gpt-4o.pkl")
    atk_vel_data = load_data("./output/results-atk-velocity-gpt-4o.pkl")
    atk_str_data = load_data("./output/results-atk-steering-gpt-4o.pkl")
    atk_vis_data = load_data("./output/results-atk-visual-gpt-4o.pkl")
    atk_vel_str_data = load_data("./output/results-atk-velocity-steering-gpt-4o.pkl")
    atk_vis_vel_data = load_data("./output/results-atk-visual-velocity-gpt-4o.pkl")
    atk_vis_str_data = load_data("./output/results-atk-visual-steering-gpt-4o.pkl")
    atk_all_data = load_data("./output/results-atk-all-gpt-4o.pkl")

    # BERTScore 계산 후 특정 기준(예: 0.7 이상) 인덱스 추출
    normal_scores = get_bertscore(atk_non_data)
    target_idxs = [i for i, val in enumerate(normal_scores) if val > 0.6]

    # sample 활용 예시
    import random

    sample_idxs = random.sample(target_idxs, min(len(target_idxs), 3))
    for idx in sample_idxs:
        print(f"Expected: {atk_non_data[idx]['expected_answer']}")
        print(f"Model: {atk_non_data[idx]['model_answer']}")
        print(f"Score: {normal_scores[idx]:.4f}")
        print("-" * 50)

    # analyze_score 호출 시 target_list를 (이름, 데이터) 형태로 전달
    target_list = [
        ("Normal", atk_non_data),
        ("Vis.", atk_vis_data),
        ("Vel.", atk_vel_data),
        ("Str.", atk_str_data),
        ("Vis. & Vel.", atk_vis_vel_data),
        ("Vis. & Str.", atk_vis_str_data),
        ("Vel. & Str.", atk_vel_str_data),
        ("All", atk_all_data),
    ]
    analyze_score(
        score_method=get_bleu_score, target_list=target_list, sample_target=target_idxs
    )

    analyze_score(
        score_method=get_bertscore, target_list=target_list, sample_target=target_idxs
    )

# Todo: Normal과 기존 데이터셋 비교 중 낮은 BERT Score의 데이터를 샘플링하여 어떤 차이를 보이는지 확인
# Todo: GPT-4o 기반 이미지 모달리티 공격 구현
# Todo: Normal을 기준으로 BERT Score 다시 계산
# Todo: 이미지 모달리티까지 ANOVA 분석
# Todo: BLEU Score 기반 분석도 추가
# Todo: BeLLM 기반 Score로도 실험 진행
# Todo: Calibrating Multimodal Learning (CML) 도 구현 및 분석
