import random
from typing import List, Tuple, Union
from copy import deepcopy

from mllm_security.gpt import generate_experiment_answer_with_context
from mllm_security.llama import change_to_opposite_meaning
from mllm_security.loader import instructions, video_captions

Modal = Tuple[str, Union[str, List[float]]]


def parse_caption(caption: str) -> List[Modal]:
    modals_raw = caption.split("\n")
    modals = []
    for modal in modals_raw:
        key, value = modal.split("] ")
        temp = value.split(": [")
        if len(temp) > 1:
            value = temp[1][:-1]
            value = value.split(", ")
            value = [float(val) for val in value]
        modals.append((key[1:], value))

    return modals


def generate_caption(modals: List[Modal]) -> str:
    caption = ""
    for key, value in modals:
        if isinstance(value, list):
            caption += f"[{key}] : {value}\n"
        else:
            caption += f"[{key}] {value}\n"
    return caption


def attack_random(data: List[float], a: float, b: float) -> str:
    min_val = min(a, b)
    max_val = max(a, b)
    for i in range(len(data)):
        data[i] = round(random.uniform(min_val, max_val), 1)
    return data


def attack_visual(
    visual_modals: List[Modal], selection_ratio: float = 0.25
) -> List[Modal]:
    modal_idxs = list(range(len(visual_modals)))
    selection_count = round(len(visual_modals) * selection_ratio)
    selection_count = max(1, selection_count)

    selected_modals = random.sample(modal_idxs, selection_count)
    for idx in selected_modals:
        info_raw = visual_modals[idx][1].split(": ")
        if len(info_raw) > 1:
            attacked_info = change_to_opposite_meaning(info_raw[1])
            attacked_text = f"{info_raw[0]}: {attacked_info}"
        else:
            attacked_text = change_to_opposite_meaning(visual_modals[idx][1])
        visual_modals[idx] = (visual_modals[idx][0], attacked_text)

    return visual_modals


# ------------------------------
# on_caption_load의 커스텀 정의들. 이 함수로 공격을 구현.


def on_caption_steering_attacked(video_id: str, caption: str) -> str:
    modals = parse_caption(caption)
    for i in range(len(modals)):
        if modals[i][0] == "Steering Angles":
            attacked_modal = attack_random(modals[i][1], 480, -480)
            # Angle 값이 이러한 범위인 이유는 데이터셋이 이 범위 내 값으로만 이루어져 있기 때문
            modals[i] = (modals[i][0], attacked_modal)

    new_caption = generate_caption(modals)
    return new_caption


def on_caption_velocity_attacked(video_id: str, caption: str) -> str:
    modals = parse_caption(caption)
    for i in range(len(modals)):
        if modals[i][0] == "Velocities":
            attacked_modal = attack_random(modals[i][1], 120, 0)
            # 속도가 120 이하로 설정된 이유는 데이터셋이 이 속도 이하로만 이루어져 있기 때문
            modals[i] = (modals[i][0], attacked_modal)

    new_caption = generate_caption(modals)
    return new_caption


def on_caption_steering_velocity_attacked(video_id: str, caption: str) -> str:
    modals = parse_caption(caption)
    for i in range(len(modals)):
        if modals[i][0] == "Velocities":
            attacked_modal = attack_random(modals[i][1], 120, 0)
            modals[i] = (modals[i][0], attacked_modal)
        if modals[i][0] == "Steering Angles":
            attacked_modal = attack_random(modals[i][1], 480, -480)
            modals[i] = (modals[i][0], attacked_modal)

    new_caption = generate_caption(modals)
    return new_caption


def on_caption_visual_attacked(video_id: str, caption: str) -> str:
    modals = parse_caption(caption)
    visual_modals = []
    non_visual_modals = []
    for i in range(len(modals)):
        if modals[i][0] != "Velocities" and modals[i][0] != "Steering Angles":
            visual_modals.append(modals[i])
        else:
            non_visual_modals.append(modals[i])

    visual_modals = attack_visual(visual_modals)
    modals = visual_modals + non_visual_modals

    new_caption = generate_caption(modals)
    return new_caption


def on_caption_visual_steering_attacked(video_id: str, caption: str):
    modals = parse_caption(caption)
    visual_modals = []
    non_visual_modals = []
    for i in range(len(modals)):
        if modals[i][0] == "Steering Angles":
            attacked_modal = attack_random(modals[i][1], 480, -480)
            non_visual_modals.append((modals[i][0], attacked_modal))
        elif modals[i][0] == "Velocities":
            non_visual_modals.append(modals[i])
        else:
            visual_modals.append(modals[i])

    visual_modals = attack_visual(visual_modals)
    modals = visual_modals + non_visual_modals

    new_caption = generate_caption(modals)
    return new_caption


def on_caption_visual_velocity_attacked(video_id: str, caption: str):
    modals = parse_caption(caption)
    visual_modals = []
    non_visual_modals = []
    for i in range(len(modals)):
        if modals[i][0] == "Velocities":
            attacked_modal = attack_random(modals[i][1], 120, 0)
            non_visual_modals.append((modals[i][0], attacked_modal))
        elif modals[i][0] == "Steering Angles":
            non_visual_modals.append(modals[i])
        else:
            visual_modals.append(modals[i])

    visual_modals = attack_visual(visual_modals)
    modals = visual_modals + non_visual_modals

    new_caption = generate_caption(modals)
    return new_caption


def on_caption_all_attacked(_: str, caption: str):
    modals = parse_caption(caption)
    visual_modals = []
    non_visual_modals = []
    for i in range(len(modals)):
        if modals[i][0] == "Velocities":
            attacked_modal = attack_random(modals[i][1], 120, 0)
            non_visual_modals.append((modals[i][0], attacked_modal))
        elif modals[i][0] == "Steering Angles":
            attacked_modal = attack_random(modals[i][1], 480, -480)
            non_visual_modals.append((modals[i][0], attacked_modal))
        else:
            visual_modals.append(modals[i])

    visual_modals = attack_visual(visual_modals)
    modals = visual_modals + non_visual_modals

    new_caption = generate_caption(modals)
    return new_caption


def on_caption_attacked(
    _: str,
    caption: str,
    need_visual_attack: bool,
    need_steering_attack: bool,
    need_velocity_attack: bool,
) -> str:
    modals = parse_caption(caption)

    description_modals = []
    visual_modals = []
    numeric_modals = []

    for modal in modals:
        modal_name = modal[0].lower()
        modal_value = modal[1]

        if modal_name == "road event" or modal_name == "car maneuver":
            description_modals.append(modal)
        elif modal_name == "steering angles":
            if need_steering_attack:
                attacked_modal = attack_random(deepcopy(modal_value), 480, -480)
                numeric_modals.append((modal_name, attacked_modal))
            else:
                numeric_modals.append(modal)
        elif modal_name == "velocities":
            if need_velocity_attack:
                attacked_modal = attack_random(deepcopy(modal_value), 120, 0)
                numeric_modals.append((modal_name, attacked_modal))
            else:
                numeric_modals.append(modal)
        else:
            visual_modals.append(modal)

    if need_visual_attack:
        visual_modals = attack_visual(deepcopy(visual_modals))

    new_modals = description_modals + visual_modals + numeric_modals
    new_caption = generate_caption(new_modals)

    return new_caption


# 끝 ------------------------------

if __name__ == "__main__":
    # 모든 모달리티 사용, 모든 모달리티 정상
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-normal-gpt-4o.yaml",
        gpt_model="gpt-4o",
        on_caption_load=None,
    )

    # 모든 모달리티 사용, Steering만 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-atk-steering-gpt-4o.yaml",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked,
            None,
            {
                "need_visual_attack": False,
                "need_steering_attack": True,
                "need_velocity_attack": False,
            },
        ),
    )

    # 모든 모달리티 사용, Velocity만 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-atk-velocity-gpt-4o.yaml",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked,
            None,
            {
                "need_visual_attack": False,
                "need_steering_attack": False,
                "need_velocity_attack": True,
            },
        ),
    )

    # 모든 모달리티 사용, Steering, Velocity 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-atk-velocity-steering-gpt-4o.yaml",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked,
            None,
            {
                "need_visual_attack": False,
                "need_steering_attack": True,
                "need_velocity_attack": True,
            },
        ),
    )

    # 모든 모달리티 사용, Visual만 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-atk-visual-gpt-4o.yaml",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked,
            None,
            {
                "need_visual_attack": True,
                "need_steering_attack": False,
                "need_velocity_attack": False,
            },
        ),
    )

    # 모든 모달리티 사용, Visual과 Steering에 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-atk-visual-steering-gpt-4o.yaml",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked,
            None,
            {
                "need_visual_attack": True,
                "need_steering_attack": True,
                "need_velocity_attack": False,
            },
        ),
    )

    # 모든 모달리티 사용, Visual과 Velocity에 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-atk-visual-velocity-gpt-4o.yaml",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked,
            None,
            {
                "need_visual_attack": True,
                "need_steering_attack": False,
                "need_velocity_attack": True,
            },
        ),
    )

    # 모든 모달리티 사용, Visual과 Velocity에 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-atk-all-gpt-4o.yaml",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked,
            None,
            {
                "need_visual_attack": True,
                "need_steering_attack": True,
                "need_velocity_attack": True,
            },
        ),
    )

    # --------------- 모달리티 오염 공격 끝 ----------------- #
