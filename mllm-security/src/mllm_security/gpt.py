import os
import pickle
from typing import Any, Callable, Dict, List, Optional, Union

import openai
from tqdm import tqdm

from mllm_security.loader import ANSWERING_PROMPT, instructions, video_captions


def get_model_answer(client: openai.OpenAI, query: str, model: str = "gpt-4o") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content.strip()


def generate_answer_with_context(
    qas: List[Dict[str, Union[str, Dict[str, str]]]],
    captions: Dict[str, str],
    output_dir: str = "./output",
    output_filename: str = "results.json",
    gpt_model: str = "gpt-4o",
    max_length: int = 1000,
    on_caption_load: Optional[Callable[[str, str], str]] = None,
    verbose: bool = True,
    debug: bool = False,
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    results = {}
    if not os.path.exists(output_path):
        with open(output_path, "wb") as f:
            pickle.dump(results, f)
    else:
        with open(output_path, "rb") as f:
            results = pickle.load(f)

    client = openai.OpenAI()

    for idx, instruction in tqdm(enumerate(qas), total=len(qas)):
        if idx >= max_length:
            break

        video_id: str = instruction["video_id"]
        caption = captions.get(video_id)
        
        if on_caption_load is not None:
            caption = on_caption_load(video_id, caption)

        if caption is None:
            continue

        qa: Dict[str, str] = instruction["QA"]
        question: str = qa["q"]
        expected_answer: str = qa["a"]

        if verbose:
            if idx in results:
                result = results[idx]
                if (
                    result["video_id"] == video_id
                    and result["question"] == question
                    and caption == result["caption"]
                ):
                    print("Already answered for question[", video_id, "]:", question)
                    continue

        query: str = caption + ANSWERING_PROMPT + question
        if not debug:
            model_answer: str = get_model_answer(client, query, model=gpt_model)

            result = {
                "video_id": video_id,
                "caption": caption,
                "question": question,
                "expected_answer": expected_answer,
                "model_answer": model_answer,
            }

            results[idx] = result

            with open(output_path, "wb") as f:
                pickle.dump(results, f)
        else:
            print(query)
            print("-" * 35)
            print("Answer:\n", expected_answer)
            cmd = input("Stop? (y/n): ")
            if cmd.lower() == "y":
                break


if __name__ == "__main__":
    generate_answer_with_context(
        instructions,
        video_captions,
        output_filename="results-normal-gpt-4o.pkl",
        gpt_model="gpt-4o",
    )
