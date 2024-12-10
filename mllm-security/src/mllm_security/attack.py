import random
from typing import List, Tuple, Union
from mllm_security.gpt import generate_answer_with_context
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


def on_caption_load(video_id: str, caption: str) -> str:
    modals = parse_caption(caption)
    for i in range(len(modals)):
        if modals[i][0] == "Velocities":
            attacked_modal = attack_random(modals[i][1], 120, 0, seed=42)
            modals[i] = (modals[i][0], attacked_modal)
        if modals[i][0] == "Steering angles":
            attacked_modal = attack_random(modals[i][1], 480, -480, seed=42 * 42)
            modals[i] = (modals[i][0], attacked_modal)

    new_caption = generate_caption(modals)
    return new_caption


def attack_random(data: List[float], max_val, min_val, seed: int = 42) -> str:
    rand = random.Random(seed)
    for i in range(len(data)):
        data[i] = round(rand.random() * (max_val + min_val) - min_val, 1)
    return data


def attack_on_modal():
    generate_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-atk-steering-gpt-4o.pkl",
        gpt_model="gpt-4o",
        on_caption_load=on_caption_load,
    )


if __name__ == "__main__":
    attack_on_modal()
