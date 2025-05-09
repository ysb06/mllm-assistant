import os
import pickle
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import openai
import yaml
from tqdm import tqdm

from mllm_security.loader import ANSWERING_PROMPT

EventCallback = Optional[
    Tuple[Callable[[str, str], str], Optional[List[Any]], Optional[Dict[str, Any]]]
]


def get_model_answer(client: openai.OpenAI, query: str, model: str = "gpt-4o") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content.strip()


def get_model_experiment_answer(
    client: openai.OpenAI,
    query: str,
    model: str = "gpt-4o",
    logprobs_count: Optional[int] = None,
) -> Tuple[Dict[str, Any], str, float]:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ],
        logprobs=True,
        top_logprobs=logprobs_count,
        top_p=0.1,
    )
    # https://platform.openai.com/docs/api-reference/chat/object
    result = response.choices[0]

    message = result.message.content
    logprobs_contents = result.logprobs.content
    logprobs_list = []
    for content in logprobs_contents:
        logprobs_list.append(content.logprob)
    sentence_confidence = calculate_sentence_confidence(logprobs_list)

    return response.to_dict(), message, sentence_confidence


def calculate_sentence_confidence(logprobs: List[float]) -> float:
    """
    토큰별 로그 확률 리스트를 받아 문장 전체의 확률(Confidence) 계산
    """
    total_logprob: np.float64 = np.sum(logprobs)  # 로그 확률 합
    sentence_confidence: np.float64 = np.exp(total_logprob)  # 확률로 변환

    return sentence_confidence.item()


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

        query: str = (
            ANSWERING_PROMPT + caption + "\n" + "-" * 16 + "\nQuestion:\n" + question
        )
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


def generate_experiment_answer_with_context(
    qas: List[Dict[str, Union[str, Dict[str, str]]]],
    captions: Dict[str, str],
    output_dir: str = "./output",
    output_name: str = "results",
    gpt_model: str = "gpt-4o",
    max_length: int = 1000,
    on_caption_load: EventCallback = None,
    verbose: bool = True,
    debug: bool = False,
    save_point: int = 100,
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    pickle_output_path = os.path.join(output_dir, f"{output_name}.pkl")
    yaml_output_path = os.path.join(output_dir, f"{output_name}.yaml")

    results = {}
    if not os.path.exists(pickle_output_path):
        with open(pickle_output_path, "wb") as f:
            pickle.dump(results, f)
    else:
        with open(pickle_output_path, "rb") as f:
            results = pickle.load(f)

    client = openai.OpenAI()

    for idx, instruction in tqdm(enumerate(qas), total=len(qas)):
        if idx >= max_length:
            break

        video_id: str = instruction["video_id"]
        caption = captions.get(video_id)

        if on_caption_load is not None:
            callback, args, kwargs = on_caption_load
            if args is not None and kwargs is not None:
                caption = callback(video_id, caption, *args, **kwargs)
            elif args is not None:
                caption = callback(video_id, caption, *args)
            elif kwargs is not None:
                caption = callback(video_id, caption, **kwargs)
            else:
                caption = callback(video_id, caption)

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

        query: str = (
            ANSWERING_PROMPT + caption + "\n" + "-" * 16 + "\nQuestion:\n" + question
        )
        if not debug:
            res, message, conf = get_model_experiment_answer(
                client, query, model=gpt_model
            )

            result = {
                "video_id": video_id,
                "caption": caption,
                "question": question,
                "expected_answer": expected_answer,
                "model_response": {
                    "response": res,
                    "message": message,
                    "confidence": conf,
                },
            }

            results[idx] = result

            if idx % save_point == 0:
                with open(pickle_output_path, "wb") as f:
                    pickle.dump(results, f)
        else:
            print(query)
            print("-" * 35)
            print("Answer:\n", expected_answer)
            cmd = input("Stop? (y/n): ")
            if cmd.lower() == "y":
                break
    
    with open(pickle_output_path, "wb") as f:
        pickle.dump(results, f)
    
    for idx in list(results.keys()):
        result = results[idx]
        del result["model_response"]["response"]
        
    with open(yaml_output_path, "w") as f:
        yaml.dump(results, f)