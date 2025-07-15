import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from petrillm import GRAPH_IMAGE_PATH, PetriState

from .node import call_pydantic_output_parser, critique, improve, modell, structure


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    process_description: Annotated[Sequence[BaseMessage], operator.add]
    process_modell: Annotated[Sequence[BaseMessage], operator.add]
    critique: Annotated[Sequence[BaseMessage], operator.add]


workflow = StateGraph(AgentState)

workflow.add_node("Structure", structure)
workflow.add_node("Model", modell)
workflow.add_node("Critic", critique)
workflow.add_node("Improve", improve)
workflow.add_node("OutputParser", call_pydantic_output_parser)

workflow.add_edge("Structure", "Model")
workflow.add_edge("Model", "Critic")
workflow.add_edge("Critic", "Improve")
workflow.add_edge("Improve", "OutputParser")

workflow.set_entry_point("Structure")

workflow.set_finish_point("OutputParser")

graph = workflow.compile()


# class GraphGenGraph:
#     def __init__(self):
#         self.graph_builder = StateGraph(PetriState)
#         # Add Nodes
#         self.graph_builder.add_node("chatbot", node_find_next_action)
#         # Add Edges
#         self.graph_builder.add_edge(START, "chatbot")
#         self.graph_builder.add_edge("chatbot", END)
#         self.chat_graph = self.graph_builder.compile()
#         self.chat_graph.get_graph().draw_png(output_file_path=GRAPH_IMAGE_PATH)

#     def invoke(self, user_query: str):
#         init_state = PetriState(messages=[HumanMessage(content=user_query)])
#         for event in self.chat_graph.stream(init_state):
#             print(event)


# 1. 목표, 시스템 범위, 페트리 넷 종료 조건
# 2. 처음 상태 정의 (횟수도 포함)
# 3. 특정 상태에서 다음 상태를 확인. 다음 상태는 여러개가 가능. 즉 다음 Transition과 Place를 정의
# 4. 현재 상태에서 진행 가능한 다음 상태들 확인
# 5. 여러 상태 중 우선 순위 정하기
# 6. 최우선 순위 상태를 다음 상태로 설정
# 7. 동시에 진행 가능한 상태 확인
# 8. 동시에 진행 가능한 상태 중 우선 순위 높은 상태를 분기로 설정.
# 9. 동시 진행 가능한 상태를 찾을 수 없을 때까지 7~8을 반복
# 10. 다음 상태에서 필요한 정보, 상황을 정의
# 11. 다음 상태에서 필요한 정보를 얻거나 상황을 만들기 위해 필요한 액션을 정의
# 12. 현재 진행 중인 다른 상태들 중 다음 상태를 진행하기 위해 진행이 필요한 경우 같이 연결
# 13. 페트리 넷 발화
# 14. 발화에 따라 통과한 Transition을 실제로 실행
# 15. Transition 실행 후 다음 상태에 실행한 결과를 업데이트
# 16. 목표가 수행될때까지, 4~15를 반복

# 기타 아이디어: 유사한 상태에서 다음 상태를 찾은 사례를 기억하고 생성에 반영
# 아크는 어떻게?
