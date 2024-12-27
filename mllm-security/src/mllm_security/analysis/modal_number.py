import pandas as pd

from ..cml import calculate_cml
from . import (
    plain_normal_path,
    attacked_visual_with_all_path,
    attacked_visual_with_only_visual_path,
    attacked_visual_with_visual_steering_path,
    attacked_visual_with_visual_velocity_path,
    normal_with_only_visual_path,
    no_velocity_normal_path,
    no_steering_normal_path,
)
from .util import anova, calculate_bert_score, get_reference_data, load_data


def analyze_modal_number_dependency():
    true_data = load_data(plain_normal_path)
    target_idxs = get_reference_data(true_data)

    # Visual Attacked 공통
    normal_with_only_visual_data = load_data(normal_with_only_visual_path)
    attacked_with_only_visual_data = load_data(attacked_visual_with_only_visual_path)
    attacked_with_visual_steering_data = load_data(
        attacked_visual_with_visual_steering_path
    )
    attacked_with_visual_velocity_data = load_data(
        attacked_visual_with_visual_velocity_path
    )
    attacked_with_all_data = load_data(attacked_visual_with_all_path)

    data = {
        "Normal": {idx: normal_with_only_visual_data[idx] for idx in target_idxs},
        "Attacked": {idx: attacked_with_only_visual_data[idx] for idx in target_idxs},
        "Attacked_with_STR": {
            idx: attacked_with_visual_steering_data[idx] for idx in target_idxs
        },
        "Attacked_with_VEL": {
            idx: attacked_with_visual_velocity_data[idx] for idx in target_idxs
        },
        "Attacked_with_ALL": {idx: attacked_with_all_data[idx] for idx in target_idxs},
    }

    criterion_data = {idx: true_data[idx] for idx in target_idxs}
    # CML이 양수일 경우 신뢰도가 증가한 것
    # CML 논문에서는 이것이 좋지 않은 징후 (특정 모달리티에 크게 의존한 것)

    # 성능: BERTScore 계산
    print("BERTScore")
    bert_socres = {}
    for key, value in data.items():
        bert_socres[key] = calculate_bert_score(value, reference_data=criterion_data)
        print(f"{key}: {sum(bert_socres[key]) / len(bert_socres[key])}")

    df_bert = pd.DataFrame(bert_socres)
    anova(df_bert, post_hoc=True)

    # Total CML Loss 비교
    normal_with_visual_steering_data = load_data(no_velocity_normal_path)
    normal_with_visual_velocity_data = load_data(no_steering_normal_path)

    data = {
        "None": (
            {idx: normal_with_only_visual_data[idx] for idx in target_idxs},
            {idx: attacked_with_only_visual_data[idx] for idx in target_idxs},
        ),
        "Only Steering": (
            {idx: normal_with_visual_steering_data[idx] for idx in target_idxs},
            {idx: attacked_with_visual_steering_data[idx] for idx in target_idxs},
        ),
        "Only Velocity": (
            {idx: normal_with_visual_velocity_data[idx] for idx in target_idxs},
            {idx: attacked_with_visual_velocity_data[idx] for idx in target_idxs},
        ),
        "All": (
            criterion_data,
            {idx: attacked_with_all_data[idx] for idx in target_idxs},
        ),
    }

    ci_values = {}
    vrr_values = {}
    for key, value in data.items():
        ci_values[key], vrr_values[key] = calculate_cml(value[0], value[1])
        print(key)
        print(f"CML: {sum(ci_values[key])}")
        print(f"VRR: {vrr_values[key]:.4f}")

    df_cis = pd.DataFrame(ci_values)
    anova(df_cis, post_hoc=True)
