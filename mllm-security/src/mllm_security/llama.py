from ollama import chat
import pprint

from tqdm import tqdm
from mllm_security.loader import instructions, video_captions

def chat_llama(text: str) -> str:
    res = chat(
        model="llama3.1",
        messages=[
            {"role": "user", "content": text},
        ],
    )

    return res.message.content

def change_to_opposite_meaning(content: str) -> str:
    res = chat_llama("Change the meaning of the following sentence or word. Answer in one sentence or word: " + content)
    return res

if __name__ == "__main__":
    res = change_to_opposite_meaning("I am happy")
    print(res)
    path = input("Enter the path of the file: ")
    for idx, instruction in tqdm(enumerate(instructions), total=len(instructions)):

        video_id: str = instruction["video_id"]
        caption = video_captions.get(video_id)

