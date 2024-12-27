import os
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI

load_dotenv()

fastapi_app = FastAPI()
openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    project="gpt-driver",
)

completion = openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion)


@fastapi_app.get("/")
def read_root():
    return {"Hello": "World"}


@fastapi_app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
