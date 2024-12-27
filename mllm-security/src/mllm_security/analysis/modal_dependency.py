import pandas as pd
from . import plain_normal_path, no_visual_normal_path, no_steering_normal_path, no_velocity_normal_path
from .util import load_data, anova, calculate_bert_score_legacy
from ..cml import calculate_cml


def analyze_normal_dependency():
    criterion_data = load_data(plain_normal_path)

    no_visual_normal_data = load_data(no_visual_normal_path)
    no_steering_normal_data = load_data(no_steering_normal_path)
    no_velocity_normal_data = load_data(no_velocity_normal_path)

    ci_value_nvis, vrr_nvis = calculate_cml(criterion_data, no_visual_normal_data)
    # CML이 양수일 경우 신뢰도가 증가한 것
    # CML 논문에서는 이것이 좋지 않은 징후 (특정 모달리티에 크게 의존한 것)

    # Total CML Loss 비교
    print("No Visual")
    print(f"CML: {sum(ci_value_nvis)}")
    print(f"VRR (no numeric): {vrr_nvis:.4f}")

    ci_values_nste, vrr_nste = calculate_cml(criterion_data, no_steering_normal_data)
    print("No Steering")
    print(f"CML: {sum(ci_values_nste)}")
    print(f"VRR (no steering): {vrr_nste:.4f}")

    ci_values_nvel, vrr_nvel = calculate_cml(criterion_data, no_velocity_normal_data)
    print("No Velocity")
    print(f"CML: {sum(ci_values_nvel)}")
    print(f"VRR (no velocity): {vrr_nvel:.4f}")

    # CML 분포 분석
    ci_data = {}
    ci_data["No Visual"] = ci_value_nvis
    ci_data["No Steering"] = ci_values_nste
    ci_data["No Velocity"] = ci_values_nvel
    df_cis = pd.DataFrame(ci_data)
    anova(df_cis, post_hoc=True)

    # 성능: BERTScore 계산
    print("BERTScore")

    no_vis_scores = calculate_bert_score_legacy(no_visual_normal_data, reference_data=criterion_data)
    print("No Visual:", sum(no_vis_scores) / len(no_vis_scores))
    no_ste_scores = calculate_bert_score_legacy(no_steering_normal_data, reference_data=criterion_data)
    print("No Steering:", sum(no_ste_scores) / len(no_ste_scores))
    no_vel_scores = calculate_bert_score_legacy(no_velocity_normal_data, reference_data=criterion_data)
    print("No Velocity:", sum(no_vel_scores) / len(no_vel_scores))

    bert_socres_data = {}
    bert_socres_data["No Visual"] = no_vis_scores
    bert_socres_data["No Steering"] = no_ste_scores
    bert_socres_data["No Velocity"] = no_vel_scores
    df_bert = pd.DataFrame(bert_socres_data)
    anova(df_bert, post_hoc=True)





    

