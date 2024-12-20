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
    if len(visual_modals) == 0:
        return visual_modals

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


# -----------


def on_caption_attacked_with_no_numeric(
    _: str, caption: str, need_visual_attack: bool
) -> str:
    modals = parse_caption(caption)

    description_modals = []
    visual_modals = []

    for modal in modals:
        modal_name = modal[0].lower()

        if modal_name == "road event" or modal_name == "car maneuver":
            description_modals.append(modal)
        elif modal_name == "steering angles":
            pass
        elif modal_name == "velocities":
            pass
        else:
            visual_modals.append(modal)

    if need_visual_attack:
        visual_modals = attack_visual(deepcopy(visual_modals))

    new_modals = description_modals + visual_modals
    new_caption = generate_caption(new_modals)

    return new_caption


def on_caption_attacked_with_no_steering(
    _: str,
    caption: str,
    need_visual_attack: bool,
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
            pass
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


def on_caption_attacked_with_no_velocity(
    _: str,
    caption: str,
    need_visual_attack: bool,
    need_steering_attack: bool,
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
            pass
        else:
            visual_modals.append(modal)

    if need_visual_attack:
        visual_modals = attack_visual(deepcopy(visual_modals))

    new_modals = description_modals + visual_modals + numeric_modals
    new_caption = generate_caption(new_modals)

    return new_caption


if __name__ == "__main__":
    # # 모든 모달리티 사용, 모든 모달리티 정상
    # random.seed(42)
    # generate_experiment_answer_with_context(
    #     instructions,
    #     video_captions,
    #     output_name="results-normal-gpt-4o",
    #     gpt_model="gpt-4o",
    #     on_caption_load=None,
    # )

    # # 모든 모달리티 사용, Steering만 공격
    # random.seed(42)
    # generate_experiment_answer_with_context(
    #     instructions,
    #     video_captions,
    #     output_name="results-atk-steering-gpt-4o",
    #     gpt_model="gpt-4o",
    #     on_caption_load=(
    #         on_caption_attacked,
    #         None,
    #         {
    #             "need_visual_attack": False,
    #             "need_steering_attack": True,
    #             "need_velocity_attack": False,
    #         },
    #     ),
    # )

    # # 모든 모달리티 사용, Velocity만 공격
    # random.seed(42)
    # generate_experiment_answer_with_context(
    #     instructions,
    #     video_captions,
    #     output_name="results-atk-velocity-gpt-4o",
    #     gpt_model="gpt-4o",
    #     on_caption_load=(
    #         on_caption_attacked,
    #         None,
    #         {
    #             "need_visual_attack": False,
    #             "need_steering_attack": False,
    #             "need_velocity_attack": True,
    #         },
    #     ),
    # )

    # # 모든 모달리티 사용, Steering, Velocity 공격
    # random.seed(42)
    # generate_experiment_answer_with_context(
    #     instructions,
    #     video_captions,
    #     output_name="results-atk-velocity-steering-gpt-4o",
    #     gpt_model="gpt-4o",
    #     on_caption_load=(
    #         on_caption_attacked,
    #         None,
    #         {
    #             "need_visual_attack": False,
    #             "need_steering_attack": True,
    #             "need_velocity_attack": True,
    #         },
    #     ),
    # )

    # # 모든 모달리티 사용, Visual만 공격
    # random.seed(42)
    # generate_experiment_answer_with_context(
    #     instructions,
    #     video_captions,
    #     output_name="results-atk-visual-gpt-4o",
    #     gpt_model="gpt-4o",
    #     on_caption_load=(
    #         on_caption_attacked,
    #         None,
    #         {
    #             "need_visual_attack": True,
    #             "need_steering_attack": False,
    #             "need_velocity_attack": False,
    #         },
    #     ),
    # )

    # # 모든 모달리티 사용, Visual과 Steering에 공격
    # random.seed(42)
    # generate_experiment_answer_with_context(
    #     instructions,
    #     video_captions,
    #     output_name="results-atk-visual-steering-gpt-4o",
    #     gpt_model="gpt-4o",
    #     on_caption_load=(
    #         on_caption_attacked,
    #         None,
    #         {
    #             "need_visual_attack": True,
    #             "need_steering_attack": True,
    #             "need_velocity_attack": False,
    #         },
    #     ),
    # )

    # # 모든 모달리티 사용, Visual과 Velocity에 공격
    # random.seed(42)
    # generate_experiment_answer_with_context(
    #     instructions,
    #     video_captions,
    #     output_name="results-atk-visual-velocity-gpt-4o",
    #     gpt_model="gpt-4o",
    #     on_caption_load=(
    #         on_caption_attacked,
    #         None,
    #         {
    #             "need_visual_attack": True,
    #             "need_steering_attack": False,
    #             "need_velocity_attack": True,
    #         },
    #     ),
    # )

    # # 모든 모달리티 사용, Visual과 Velocity에 공격
    # random.seed(42)
    # generate_experiment_answer_with_context(
    #     instructions,
    #     video_captions,
    #     output_name="results-atk-all-gpt-4o",
    #     gpt_model="gpt-4o",
    #     on_caption_load=(
    #         on_caption_attacked,
    #         None,
    #         {
    #             "need_visual_attack": True,
    #             "need_steering_attack": True,
    #             "need_velocity_attack": True,
    #         },
    #     ),
    # )

    # Visual 모달 만 사용, 공격 없음
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-normal-with-no-numeric-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_numeric,
            None,
            {
                "need_visual_attack": False,
            },
        ),
    )

    # Visual 모달 만 사용, Visual에 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-atk-visual-with-no-numeric-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_numeric,
            None,
            {
                "need_visual_attack": True,
            },
        ),
    )

    # ------------------------------------------------
    # Visual, Steering 사용, 공격 없음
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-normal-with-no-velocity-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_velocity,
            None,
            {
                "need_visual_attack": False,
                "need_steering_attack": False,
            },
        ),
    )

    # Visual, Steering 사용, Visual에 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-atk-visual-with-no-velocity-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_velocity,
            None,
            {
                "need_visual_attack": True,
                "need_steering_attack": False,
            },
        ),
    )

    # Visual, Steering 사용, Steering 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-atk-steering-with-no-velocity-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_velocity,
            None,
            {
                "need_visual_attack": False,
                "need_steering_attack": True,
            },
        ),
    )

    # Visual, Steering 사용, 전체 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-atk-all-with-no-velocity-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_velocity,
            None,
            {
                "need_visual_attack": True,
                "need_steering_attack": True,
            },
        ),
    )

    # ------------------------------------------------
    # Visual, Velocity 사용, 공격 없음
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-normal-with-no-steering-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_steering,
            None,
            {
                "need_visual_attack": False,
                "need_velocity_attack": False,
            },
        ),
    )

    # Visual, Velocity 사용, Visual에 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-atk-visual-with-no-steering-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_steering,
            None,
            {
                "need_visual_attack": True,
                "need_velocity_attack": False,
            },
        ),
    )

    # Visual, Velocity 사용, Velocity에 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-atk-velocity-with-no-steering-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_steering,
            None,
            {
                "need_visual_attack": False,
                "need_velocity_attack": True,
            },
        ),
    )

    # Visual, Velocity 사용, 전체 공격
    random.seed(42)
    generate_experiment_answer_with_context(
        instructions,
        video_captions,
        output_name="results-atk-all-with-no-steering-gpt-4o",
        gpt_model="gpt-4o",
        on_caption_load=(
            on_caption_attacked_with_no_steering,
            None,
            {
                "need_visual_attack": True,
                "need_velocity_attack": True,
            },
        ),
    )
