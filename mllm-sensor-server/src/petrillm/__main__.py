import os

from langchain_core.messages import HumanMessage
from .graph import graph


while True:
    user_query = input("Enter your query: ")

    # AgentState에 맞는 딕셔너리 형태로 변환
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "process_description": [user_query],  # 첫 번째 프로세스 설명
        "process_modell": [],
        "critique": [],
    }

    for output in graph.stream(initial_state):
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            if type(value) is dict:

                for item_key, item in value.items():
                    print(item_key, end=":\r\n")
                    if type(item) is list:
                        for idx, sub_item in enumerate(item):
                            print(f"# {idx}:")
                            print(sub_item)
                    else:
                        print(item)
            else:
                print(value)
        print("\n---\n")
