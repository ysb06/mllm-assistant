import os

import alfworld.agents.modules.generic as generic
import numpy as np
from alfworld.agents.environment import get_environment
from langchain_core.messages import HumanMessage

from .graph import graph

# while True:
#     user_query = input("Enter your query: ")

#     # AgentState에 맞는 딕셔너리 형태로 변환
#     initial_state = {
#         "messages": [HumanMessage(content=user_query)],
#         "process_description": [user_query],  # 첫 번째 프로세스 설명
#         "process_modell": [],
#         "critique": [],
#     }

#     for output in graph.stream(initial_state):
#         for key, value in output.items():
#             print(f"Output from node '{key}':")
#             print("---")
#             if type(value) is dict:
#                 for item_key, item in value.items():
#                     print(item_key, end=":\r\n")
#                     if type(item) is list:
#                         for idx, sub_item in enumerate(item):
#                             print(f"# {idx}:")
#                             print(sub_item)
#                     else:
#                         print(item)
#             else:
#                 print(value)
#         print("\n---\n")


# load config
config = generic.load_config()
env_type = config['env']['type'] # 'AlfredTWEnv' or 'AlfredThorEnv' or 'AlfredHybrid'

# setup environment
env = get_environment(env_type)(config, train_eval='train')
env = env.init_env(batch_size=1)

# interact
obs, info = env.reset()
while True:
    # get random actions from admissible 'valid' commands (not available for AlfredThorEnv)
    admissible_commands = list(info['admissible_commands']) # note: BUTLER generates commands word-by-word without using admissible_commands
    random_actions = [np.random.choice(admissible_commands[0])]

    # step
    obs, scores, dones, infos = env.step(random_actions)
    print("Action: {}, Obs: {}".format(random_actions[0], obs[0]))