from typing import Annotated, Any, Dict, List, Literal, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from petrillm import PetriState


class CodeOutput(BaseModel):
    answer: str = Field(description="Answer to the query")
    python_function: str = Field(
        description="Python function code used to derive the answer. This code should be executable function and return the answer when run with python_function_args as arguments."
    )
    python_function_args: Dict[str, str] = Field(
        description="Arguments passed as **kwargs to the python_function to obtain the answer to the query. These arguments must ensure the python_function returns the correct answer when called."
    )


class ExpandOutput(BaseModel):
    control_flow: Literal["sequence", "fallback", "parallel"] = Field(
        description="Type of control‑flow node to use when decomposing the goal."
    )
    subgoals: List[str] = Field(
        description="A list of natural‑language subgoals created from the current goal."
    )


llm_llama = ChatOllama(model="llama3.1")
llm_llama_code = llm_llama.with_structured_output(CodeOutput, include_raw=True)
llm_llama_ctrl_flow = llm_llama.with_structured_output(ExpandOutput, include_raw=True)


def node_find_next_action(state: PetriState):
    query: List[BaseMessage] = state["messages"]
    current_user_query: HumanMessage = query[-1]
    user_query_message: str = current_user_query.content
    prompt = (
        "The \"Sequence node\", which executes its child nodes in order. "
        "It returns success if all child nodes succeed; however, if any child node fails, the sequence node returns failure. "
        "The second type is the \"Fallback\" node, which also executes its child nodes sequentially but returns success as soon as any child node succeeds. "
        "If none of the child nodes succeed, it returns failure. "
        "The third type is the \"Parallel\" node, a variation of the traditional parallel node concept. "
        "While the traditional definition of a parallel node involves executing child nodes simultaneously, the \"Parallel\" node executes its child nodes independently, regardless of their individual success or failure. After all nodes are executed, the outcomes are aggregated according to a predefined policy to determine the overall success or failure. "

        "Given the current high‑level goal, decide whether it should be decomposed. "
        f"High‑level goal: {user_query_message}\n"
    )
    result_raw = llm_llama_ctrl_flow.invoke(prompt)
    result = result_raw["parsed"]
    return {"messages": [AIMessage(content=f"{result}")]}
