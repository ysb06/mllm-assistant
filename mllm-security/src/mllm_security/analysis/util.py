import pickle
from typing import Any, Dict, Optional

import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import bert_score


def load_data(file_path: str) -> Dict[int, Dict[str, Any]]:
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    return data


def anova(
    df: pd.DataFrame,
    var_name: str = "group",
    value_name: str = "value",
    post_hoc: bool = True,
    alpha: float = 0.05,
):
    df_melt = df.melt(var_name=var_name, value_name=value_name)

    model = ols(f"{value_name} ~ C({var_name})", data=df_melt).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    print("\nANOVA results:")
    print(anova_table)

    if post_hoc:
        tukey = pairwise_tukeyhsd(
            endog=df_melt[value_name], groups=df_melt[var_name], alpha=alpha
        )
        print("\nTukey's HSD Post-hoc Test:")
        print(tukey)

def get_reference_data(target_data: Dict[int, Dict[str, Any]], reference_score: float = 0.6) -> Dict[int, Dict[str, Any]]:
    references = []
    hypotheses = []

    for idx in sorted(target_data.keys()):
        references.append(target_data[idx]["expected_answer"])
        hypotheses.append(target_data[idx]["model_response"]["message"])
    
    P, R, F1 = bert_score.score(hypotheses, references, model_type="bert-base-uncased")

    filtered_idx = []
    for idx, f1 in enumerate(F1):
        if (f1 > reference_score).item():
            filtered_idx.append(idx)

    return filtered_idx

def calculate_bert_score(
    target_data: Dict[int, Dict[str, Any]],
    reference_data: Dict[int, Dict[str, Any]],
) -> float:
    references = []
    hypotheses = []

    for idx in sorted(target_data.keys()):
        references.append(reference_data[idx]["model_response"]["message"])
        hypotheses.append(target_data[idx]["model_response"]["message"])
    
    P, R, F1 = bert_score.score(hypotheses, references, model_type="bert-base-uncased")

    return F1.tolist()

def calculate_bert_score_legacy(
    target_data: Dict[int, Dict[str, Any]],
    reference_data: Optional[Dict[int, Dict[str, Any]]] = None,
    reference_score: float = 0.6,   # Use when reference_data is not None
) -> float:
    # 주의 Key Sort 가정
    references = []
    hypotheses = []

    if reference_data is None:
        for result in target_data.values():
            references.append(result["expected_answer"])
            hypotheses.append(result["model_response"])
    else:
        temp_references = []
        temp_hypotheses = []
        for result in reference_data.values():
            temp_references.append(result["expected_answer"])
            temp_hypotheses.append(result["model_response"]["message"])
        
        P, R, F1 = bert_score.score(temp_hypotheses, temp_references, model_type="bert-base-uncased")

        for idx, f1 in enumerate(F1):
            if (f1 > reference_score).item():
                references.append(temp_hypotheses[idx])
                hypotheses.append(target_data[idx]["model_response"]["message"])
        
        print("Filtered data size:", len(references))
    
    P, R, F1 = bert_score.score(hypotheses, references, model_type="bert-base-uncased")

    return F1.tolist()