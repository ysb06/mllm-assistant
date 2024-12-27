import pickle
from typing import Any, Dict, Tuple, List

def load_data(file_path: str) -> Dict[int, Dict[str, float]]:
    """파일에서 데이터를 불러옵니다."""
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    return data

def calculate_cml(baseline_data:Dict[int, Dict[str, Any]], modified_data: Dict[int, Dict[str, Any]]):
    """두 데이터 사이의 CI와 VRR을 계산합니다."""
    ci_values = []
    vrr_count = 0

    for idx, baseline_item in baseline_data.items():
        baseline_conf = baseline_item["model_response"]["confidence"]
        modified_conf = modified_data[idx]["model_response"]["confidence"]

        ci = modified_conf - baseline_conf  # 이것은 엄밀히 -CI입니다.
        ci_values.append(ci)

        if ci < 0:
            vrr_count += 1

    total_samples = len(ci_values)
    vrr = vrr_count / total_samples if total_samples > 0 else 0.0

    return ci_values, vrr
    

def calculate_ci_and_vrr(
    baseline_path: str, modified_path: str
) -> Tuple[List[float], float]:
    # 데이터 로드
    baseline_data = load_data(baseline_path)
    modified_data = load_data(modified_path)

    ci_values = []
    vrr_count = 0

    for idx, baseline_item in baseline_data.items():
        # 기준 신뢰도
        baseline_conf = baseline_item["model_response"]["confidence"]

        # 수정된 데이터에서의 신뢰도
        modified_conf = modified_data[idx]["model_response"]["confidence"]

        # CI 계산
        ci = modified_conf - baseline_conf
        ci_values.append(ci)

        # VRR 계산 (CI < 0인 경우)
        if ci < 0:
            vrr_count += 1

    # VRR 계산
    total_samples = len(ci_values)
    vrr = vrr_count / total_samples if total_samples > 0 else 0.0

    return ci_values, vrr

if __name__ == "__main__":
    # 테스트 실행
    baseline_path = "./output/results-normal-gpt-4o.pkl"
    modified_path = "./output/results-atk-visual-gpt-4o.pkl"

    ci_values, vrr = calculate_ci_and_vrr(baseline_path, modified_path)
    print(f"CI values: {ci_values}")
    print(f"VRR: {vrr:.4f}")