import pickle
from typing import Dict, Optional
from mllm_security.loader import video_captions
from mllm_security.attack import parse_caption

def check_min_max_steering_angle():
    data = []
    for caption in video_captions.values():
        modals = parse_caption(caption)
        data.extend(modals["Steering Angles"])

    print("Max Steering Angle:", max(data))
    print("Min Steering Angle:", min(data))

def print_results(result_path: str, target_idx: Optional[int] = None):
    with open(result_path, "rb") as f:
        results: Dict[str, str] = pickle.load(f)

    for idx, result in results.items():
        if idx is not None and idx != target_idx:
            continue

        print(f"Question {idx}:")
        print("Video ID:", result["video_id"])
        print("Caption:", result["caption"])
        print("Question:", result["question"])
        print("Expected Answer:", result["expected_answer"])
        print("Model Answer:", result["model_answer"])
        print()

if __name__ == "__main__":
    print("== Attacked data:")
    print_results("output/results-atk-velocity-gpt-4o.pkl", target_idx=142)

    print("== Normal data:")
    print_results("output/results-normal-gpt-4o.pkl", target_idx=142)