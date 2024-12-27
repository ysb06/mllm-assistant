import pandas as pd

from ..cml import calculate_cml
from . import (
    plain_normal_path,
    attacked_visual_with_all_path,
    attacked_steering_with_all_path,
    attacked_velocity_with_all_path,
    attacked_visual_steering_with_all_path,
    attacked_visual_velocity_with_all_path,
    attacked_all_with_all_path,
)
from .util import anova, calculate_bert_score, get_reference_data, load_data


def analyze_modal_in_all():
    true_data = load_data(plain_normal_path)
    target_idxs = get_reference_data(true_data)

    # Visual Atk 공통
    normal_data = {idx: true_data[idx] for idx in target_idxs}

    visual_attacked_raw = load_data(attacked_visual_with_all_path)
    visual_attacked_data = {idx: visual_attacked_raw[idx] for idx in target_idxs}
    steering_attacked_raw = load_data(attacked_steering_with_all_path)
    steering_attacked_data = {idx: steering_attacked_raw[idx] for idx in target_idxs}
    velocity_attacked_raw = load_data(attacked_velocity_with_all_path)
    velocity_attacked_data = {idx: velocity_attacked_raw[idx] for idx in target_idxs}
    visual_steering_attacked_raw = load_data(attacked_visual_steering_with_all_path)
    visual_steering_attacked_data = {idx: visual_steering_attacked_raw[idx] for idx in target_idxs}
    visual_velocity_attacked_raw = load_data(attacked_visual_velocity_with_all_path)
    visual_velocity_attacked_data = {idx: visual_velocity_attacked_raw[idx] for idx in target_idxs}
    all_attacked_raw = load_data(attacked_all_with_all_path)
    all_attacked_data = {idx: all_attacked_raw[idx] for idx in target_idxs}




    data = {
        "VIS Atk": visual_attacked_data,
        "STE Atk": steering_attacked_data,
        "VEL Atk": velocity_attacked_data,
        "VIS and STE Atk": visual_steering_attacked_data,
        "VIS and VEL Atk": visual_velocity_attacked_data,
        "All Atk": all_attacked_data,
    }

    # 성능: BERTScore 계산
    print("BERTScore")
    bert_socres = {}
    for key, value in data.items():
        bert_socres[key] = calculate_bert_score(value, reference_data=normal_data)
        print(f"{key}: {sum(bert_socres[key]) / len(bert_socres[key])}")

    df_bert = pd.DataFrame(bert_socres)
    anova(df_bert, post_hoc=True)

    # Total CML Loss 비교
    data = {
        "Atk VIS": (normal_data, visual_attacked_data),
        "Atk STE": (normal_data, steering_attacked_data),
        "Atk VEL": (normal_data, velocity_attacked_data),
        "Atk VIS and STE": (normal_data, visual_steering_attacked_data),
        "Atk VIS and VEL": (normal_data, visual_velocity_attacked_data),
        "Atk All": (normal_data, all_attacked_data),
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
