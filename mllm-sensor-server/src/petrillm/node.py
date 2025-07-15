import json
from typing import Dict, List, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


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


# llm_llama = ChatOllama(model="llama3.1")
# Open Source LLM
llm = ChatOllama(model="llama3.1")
# llm_llama_code = llm_llama.with_structured_output(CodeOutput, include_raw=True)
# llm_llama_ctrl_flow = llm_llama.with_structured_output(ExpandOutput, include_raw=True)


# def node_find_next_action(state: PetriState):
#     query: List[BaseMessage] = state["messages"]
#     current_user_query: HumanMessage = query[-1]
#     user_query_message: str = current_user_query.content
#     prompt = (
#         "The \"Sequence node\", which executes its child nodes in order. "
#         "It returns success if all child nodes succeed; however, if any child node fails, the sequence node returns failure. "
#         "The second type is the \"Fallback\" node, which also executes its child nodes sequentially but returns success as soon as any child node succeeds. "
#         "If none of the child nodes succeed, it returns failure. "
#         "The third type is the \"Parallel\" node, a variation of the traditional parallel node concept. "
#         "While the traditional definition of a parallel node involves executing child nodes simultaneously, the \"Parallel\" node executes its child nodes independently, regardless of their individual success or failure. After all nodes are executed, the outcomes are aggregated according to a predefined policy to determine the overall success or failure. "

#         "Given the current high‑level goal, decide whether it should be decomposed. "
#         f"High‑level goal: {user_query_message}\n"
#     )
#     result_raw = llm_llama_ctrl_flow.invoke(prompt)
#     result = result_raw["parsed"]
#     return {"messages": [AIMessage(content=f"{result}")]}


# -----------------------------


class Name(BaseModel):
    de: str = Field(description="The name in German")
    en: str = Field(description="The name in English")


class Element(BaseModel):
    name: Name = Field(description="The name of the element in different languages")
    self: int = Field(description="The unique identifier of the element")
    type: str = Field(
        description="The type of the element", enum=["Activity", "Object Store"]
    )


class Edge(BaseModel):
    from_: int = Field(alias="from", description="The ID of the source element")
    to: int = Field(description="The ID of the target element")


class PetriNetTransition(BaseModel):
    elements: List[Element] = Field(description="Elements in the Petri net")
    edges: List[Edge] = Field(description="Edges connecting elements in the Petri net")


def structure(state):

    structure_prompt = structure_prompt = (
        process_structuring_prompt
    ) = """
    <prompt>
        <description>You are an expert in process modeling and Petri Nets. Your task is to structure a detailed process description in a way that facilitates its transformation into a Petri Net model. The structured description should follow the exact order of activities, decision points, parallel processes, loops, and endpoints as described in the original process. When a loop or cycle is present, ensure that the entire loop, including any decisions that lead back to the start of the loop, is described within the "Loops and Cycles" section, avoiding unnecessary subdivisions.</description>

        <Purpose>
            The goal is to accurately reflect the process flow by structuring the description in a clear and logical sequence. Each section should be maintained as a continuous block until a different type of section naturally occurs in the process. Loops and cycles should be fully contained within their section, including any related decisions, to ensure the model can be easily converted into a Petri Net without unnecessary subdivision.
        </Purpose>

        <Modeling_Guidelines>
            1. **Understand the Process:**
                - Carefully read the process description to understand the overall goal and sequence of the process.
                - Identify key activities, decisions, parallel processes, loops, and endpoints that define the workflow.

            2. **Group Related Activities Together:**
                - Group all activities that belong to the same logical phase into a single **Sequence of Activities** section.
                - Only transition to a new section type (e.g., **Decision Points**, **Parallel Activities**, **Loops and Cycles**) when there is a clear shift in the type of process element.

            3. **Avoid Unnecessary Subdivisions:**
                - Do not break a **Sequence of Activities** into multiple sections unless there is an explicit change in the process type.
                - When a loop or cycle is identified, include the entire loop, including any decision points that control the loop, within the **Loops and Cycles** section.

            4. **Identify and Respect Section Boundaries:**
                - Clearly mark where one section ends and another begins, but only when a different type of process element is introduced.
                - Ensure that all decisions that lead back to the start of a loop are incorporated within the **Loops and Cycles** section, and do not create a separate **Decision Points** section for them.

        </Modeling_Guidelines>

        <Examples>
            **Example 1**:
            ### Structured Process Description:

            #### Start Point:
            - **Questionnaire Process Initiation:**
            - The process begins with the customer office sending a questionnaire to the customer by e-mail.

            #### Sequence of Activities:
            1. **Send Questionnaire:**
            - The customer office sends the questionnaire to the customer by e-mail.
            2. **Customer Fills Out Questionnaire:**
            - The customer fills out the questionnaire.
            3. **Customer Sends Back Questionnaire:**
            - The customer sends the completed questionnaire back to the customer office.
            4. **Check Questionnaire:**
            - Upon receipt, the questionnaire is carefully checked in the office.

            #### Loops and Cycles:
            - **Questionnaire Completion Loop:**
            - The process may loop back to the initial step of sending the questionnaire if any information is missing.
            - **Condition to continue the loop:**
                - The office checks if the questionnaire is complete.
                - **If Complete:**
                - The complete questionnaire is entered into the system, and the process is finalized.
                - **If Incomplete:**
                - The email is sent to the customer again, and the loop starts over from the beginning.

            #### End Points:
            - **Process Finalized:**
            - The process ends when the complete questionnaire is entered into the system and the process is finalized.

            **Example 2**:
            ### Structured Process Description:

            #### Start Point:
            - **Initiation of Marketing Campaign:**
            - The process begins with the initiation of a new marketing campaign.

            #### Sequence of Activities:
            1. **Market Research:**
            - Research is conducted to understand the target audience and market trends.
            2. **Campaign Strategy Development:**
            - A strategy is developed based on the research findings.
            3. **Content Creation:**
            - Marketing content is created in line with the campaign strategy.
            4. **Campaign Launch:**
            - The campaign is launched across selected marketing channels.
            5. **Performance Monitoring:**
            - The performance of the campaign is monitored in real-time.

            #### Loops and Cycles:
            - **Campaign Adjustment Loop:**
            - The process may loop back to the strategy development phase if the campaign is not performing as expected.
            - **Condition to continue the loop:**
                - The campaign performance is reviewed.
                - **If Successful:**
                - The campaign continues without adjustment.
                - **If Unsuccessful:**
                - The strategy is adjusted, and the campaign is relaunched.

            #### End Points:
            - **Campaign Concluded:**
            - The process ends when the marketing campaign concludes successfully.

        </Examples>
    </prompt>
    """

    process = state["process_description"]
    process_description = process[-1]

    message = [
        SystemMessage(content=structure_prompt),
        HumanMessage(content=process_description),
    ]

    response = llm.invoke(message).content

    return {"process_description": [response]}

    # Modelliert die Prozessbeschreibung als Petri-Netz.

    # Diese Funktion nimmt den aktuellen AgentState entgegen, extrahiert
    # die strukturierte Prozessbeschreibung und wandelt sie schrittweise
    # in ein Petri-Netz um.

    # Args:
    # state (AgentState): Der aktuelle Status des Agentstate, enthält die Prozessbeschreibung.

    # Returns:
    # dict: Ein Dictionary, das das generierte Petri-Netz unter dem Schlüssel "process_modell" enthält.


def modell(state):

    # Allgemeiner Prompt für das LLM
    # Dieser Prompt enthält allgemeine Anweisungen zur Modellierung von Petri-Netzen
    # und eine Beschreibung der grundlegenden Elemente (Stellen, Transitionen, Kanten).
    general_prompt = """
        <prompt>
            <description>
                You are an expert in Petri nets and their modeling. Follow the specific instructions for each section to ensure the model is consistent and logical. Only model what is explicitly provided in the section by the human. Do not invent additional places, transitions, or negations of statuses (e.g., only "Project registered" should be modeled, not "Project not registered").
            </description>

            <constructs>
                <generalDescription>General Description of Constructs</generalDescription>

                <placesAndTransitions>
                    <place>
                        <description>Represents a state or condition in the process.</description>
                        <example>Participated in exam (state)</example>
                        <petrinetConstruct>Place (P)</petrinetConstruct>
                    </place>

                    <activity>
                        <description>Represents an action or event in the process.</description>
                        <example>Writing an exam (action)</example>
                        <petrinetConstruct>Transition (T)</petrinetConstruct>
                    </activity>

                    <important>
                        There should never be an edge between two transitions or two places. An edge must always go from a transition to a place or from a place to a transition.
                    </important>
                </placesAndTransitions>
            </constructs>
        </prompt>
    """

    # --- Spezifische Prompts für unterschiedliche Abschnitte der Prozessbeschreibung ---
    # Diese Prompts erweitern den allgemeinen Prompt um spezifische Anweisungen
    # zur Modellierung der verschiedenen Abschnitte einer Prozessbeschreibung
    # (Startpunkt, Sequenz von Aktivitäten, parallele Aktivitäten, Entscheidungspunkte, Schleifen, Endpunkte).
    prompts = {
        "Start Point": general_prompt
        + """
        <additional_instructions>
            <Purpose>
                Your task is to model the starting point of the process in a Petri net. This section defines the initial state where the process begins and should be represented with clarity and precision.
            </Purpose>
            
            <Modeling Guidelines>
                - The Start Point should be represented as a single Place (P) with no incoming edges and only outgoing edges.
                - Assign a unique and meaningful name to this Place that reflects the beginning of the process.
                - Ensure that the Start Point is clearly distinguished from other parts of the process, with a focus on initiating the sequence of activities.
                - Use the format: "[Place Name] (Place)" for the output.
            </Modeling Guidelines>
            
            <Examples>
                **Example 1**:
                - **Places**:
                    - Process Start (Place)
                - **Transitions**:
                    (No transitions in the Start Point)
                - **Edges**:
                    (No edges in the Start Point)
                
                **Example 2**:
                - **Places**:
                    - Customer Arrives (Place)
                - **Transitions**:
                    (No transitions in the Start Point)
                - **Edges**:
                    (No edges in the Start Point)
            </Examples>
        </additional_instructions>
    """,
        "Sequence of Activities": general_prompt
        + """
        <additional_instructions>
            <Purpose>
                Your task is to model the sequence of activities that occur in the process. This section focuses on representing each action or event in the process and the order in which they occur.
            </Purpose>
            
            <Modeling Guidelines>
                - Each activity should be represented as a unique Transition (T) connected by edges to corresponding Places (P) that represent the states before and after the activity.
                - Ensure that each Transition (T) and Place (P) has a unique and meaningful name that accurately reflects its role in the process.
                - Use the format: "[Place Name] (Place)" and "[Transition Name] (Transition)" for the output.
            </Modeling Guidelines>
            
            <Examples>
                **Example 1**:
                - **Places**:
                    - Order Placed (Place)
                    - Order Confirmed (Place)
                - **Transitions**:
                    - Confirm Order (Transition)
                - **Edges**:
                    - Order Placed (Place) --> Confirm Order (Transition)
                    - Confirm Order (Transition) --> Order Confirmed (Place)
                
                **Example 2**:
                - **Places**:
                    - Application Submitted (Place)
                    - Application Reviewed (Place)
                - **Transitions**:
                    - Review Application (Transition)
                - **Edges**:
                    - Application Submitted (Place) --> Review Application (Transition)
                    - Review Application (Transition) --> Application Reviewed (Place)
            </Examples>
        </additional_instructions>
    """,
        "Parallel Activities": general_prompt
        + """
        <additional_instructions>
            <Purpose>
                Your task is to model parallel activities in the process. This section should clearly represent activities that can occur simultaneously and must be synchronized later in the process.
            </Purpose>
            
            <Modeling Guidelines>
                - Start with a single Transition (T) that represents the initiation of parallel activities.
                - Each outgoing edge from this Transition (T) should lead to a separate, uniquely named Place (P).
                - Ensure that parallel paths are clearly distinct and are synchronized by having each parallel path converge back into a single Transition (T) later.
                - Use the format: "[Place Name] (Place)" and "[Transition Name] (Transition)" for the output.
            </Modeling Guidelines>
            
            <Examples>
                **Example 1**:
                - **Places**:
                    - Task A Started (Place)
                    - Task B Started (Place)
                - **Transitions**:
                    - Start Parallel Tasks (Transition)
                - **Edges**:
                    - Start Parallel Tasks (Transition) --> Task A Started (Place)
                    - Start Parallel Tasks (Transition) --> Task B Started (Place)

                **Example 2**:
                - **Places**:
                    - Start Documentation (Place)
                    - Start Development (Place)
                    - Documentation Completed (Place)
                    - Code Developed (Place)
                - **Transitions**:
                    - Start Parallel Work (Transition)
                    - Documenting (Transition)
                    - Developing (Transition)
                    - Synchronize Work (Transition)
                - **Edges**:
                    - Start Parallel Work (Transition) --> Start Documentation (Place)
                    - Start Parallel Work (Transition) --> Start Development (Place)
                    - Start Documentation (Place) --> Documenting (Transition)
                    - Documenting (Transition) --> Documentation Completed (Place)
                    - Documentation Completed (Place) --> Synchronize Work (Transition)
                    - Start Development (Place) --> Devoloping (Transition)
                    - Devoloping (Transition) --> Code Developed (Place)
                    - Code Developed (Place) --> Synchronize Work (Transition)
            </Examples>
        </additional_instructions>
    """,
        "Decision Points": general_prompt
        + """
        <additional_instructions>  
            <Purpose>  
            Your task is to model decision points in the process. This section should represent points where decisions are made, leading to different outcomes in the process. However, all possible outcomes must eventually merge back into a common point in the process.  
            </Purpose>  
            
            <Modeling Guidelines>  
                - Start with a single Place (P) that represents the decision point.  
                - Each outgoing edge from this Place (P) should lead to a separate Transition (T), representing different possible outcomes of the decision.  
                - Each Transition (T) should then connect to a respective Place (P) that represents the state after the decision.  
                - At the end, all different paths must converge back into a common Place (P), representing a unified state after the decision branches have been processed.  
                - Use the format: "[Place Name] (Place)" and "[Transition Name] (Transition)" for the output.  
            </Modeling Guidelines>  
            
            <Examples>  
            
            **Example 1**:  
            - **Places**:  
                - Decision Point (Place)  
                - Approved (Place)  
                - Rejected (Place)  
                - Final Status (Place)  
            - **Transitions**:  
                - Approve (Transition)  
                - Reject (Transition)  
            - **Edges**:  
                - Decision Point (Place) --> Approve (Transition)  
                - Decision Point (Place) --> Reject (Transition)  
                - Approve (Transition) --> Approved (Place)  
                - Reject (Transition) --> Rejected (Place)  
                - Approved (Place) --> Final Status (Place)  
                - Rejected (Place) --> Final Status (Place)  
            
            **Example 2**:  
            - **Places**:  
                - Review Completed (Place)  
                - Proceed to Next Stage (Place)  
                - Return for Revision (Place)  
                - Final Decision (Place)  
            - **Transitions**:  
                - Move Forward (Transition)  
                - Revise (Transition)  
            - **Edges**:  
                - Review Completed (Place) --> Move Forward (Transition)  
                - Review Completed (Place) --> Revise (Transition)  
                - Move Forward (Transition) --> Proceed to Next Stage (Place)  
                - Revise (Transition) --> Return for Revision (Place)  
                - Proceed to Next Stage (Place) --> Final Decision (Place)  
                - Return for Revision (Place) --> Final Decision (Place)  
            </Examples>  
        </additional_instructions>  
    """,
        "Loops and Cycles": general_prompt
        + """
        <additional_instructions>
            <Purpose>
                Your task is to model loops and cycles where actions repeat based on conditions. This section should represent processes that may need to be repeated.
            </Purpose>
            
            <Modeling Guidelines>
                - Each loop should connect back to a previous Place (P), which should be uniquely named.
                - Ensure that the loop logic is clear, with distinct Transitions (T) leading back to a common Place (P).
                - Use the format: "[Place Name] (Place)" and "[Transition Name] (Transition)" for the output.
            </Modeling Guidelines>
            
            <Examples>
                **Example 1**:
                    - **Places**:
                        - Review Application (Place)
                        - Application Requires Revision (Place)
                        - Application Approved (Place)
                        - Decision Point: Application Review Outcome (Place)
                    - **Transitions**:
                        - Request Revision (Transition)
                        - Revise Application (Transition)
                        - Approve Application (Transition)
                    - **Edges**:
                        - Review Application (Place) --> Decision Point: Application Review Outcome (Place)
                        - Decision Point: Application Review Outcome (Place) --> Request Revision (Transition)
                        - Request Revision (Transition) --> Application Requires Revision (Place)
                        - Application Requires Revision (Place) --> Revise Application (Transition)
                        - Revise Application (Transition) --> Review Application (Place) <!-- Loop-back path -->
                        - Decision Point: Application Review Outcome (Place) --> Approve Application (Transition)
                        - Approve Application (Transition) --> Application Approved (Place) <!-- Forward path -->
                
                **Example 2**:
                    - **Places**:
                        - Test Feature (Place)
                        - Bug Detected (Place)
                        - Feature Passed Testing (Place)
                        - Decision Point: Bug Detected? (Place)
                    - **Transitions**:
                        - Fix Bug (Transition)
                        - Retest Feature (Transition)
                        - Continue Process (Transition)
                    - **Edges**:
                        - Test Feature (Place) --> Decision Point: Bug Detected? (Place)
                        - Decision Point: Bug Detected? (Place) --> Fix Bug (Transition)
                        - Fix Bug (Transition) --> Bug Detected (Place)
                        - Bug Detected (Place) --> Retest Feature (Transition)
                        - Retest Feature (Transition) --> Test Feature (Place) <!-- Loop-back path -->
                        - Decision Point: Bug Detected? (Place) --> Continue Process (Transition)
                        - Continue Process (Transition) --> Feature Passed Testing (Place) <!-- Forward path -->
            </Examples>
        </additional_instructions>
    """,
        "End Points": general_prompt
        + """
        <additional_instructions>
            <Purpose>
                Your task is to model the conclusion of the process in the Petri net. This section represents the final state(s) of the process and should be clearly defined.
            </Purpose>
            
            <Modeling Guidelines>
                - The End Point should be represented as a single Place (P) with no outgoing edges.
                - Assign a unique and meaningful name to this Place that reflects the end of the process.
                - Ensure that the End Point is clearly distinguished from other parts of the process.
                - Use the format: "[Place Name] (Place)" for the output.
            </Modeling Guidelines>
            
            <Examples>
                **Example 1**:
                - **Places**:
                    - Process Completed (Place)
                - **Transitions**:
                    (No transitions in the End Point)
                - **Edges**:
                    (No edges in the End Point)
                
                **Example 2**:
                - **Places**:
                    - Invoice Approved (Place)
                - **Transitions**:
                    (No transitions in the End Point)
                - **Edges**:
                    (No edges in the End Point)
            </Examples>
        </additional_instructions>
    """,
    }

    # Extrahieren der Prozessbeschreibung aus dem Agentstate
    process = state["process_description"]
    process_parts = process[-1].split("###")

    # Nur Abschnitte, die in dieser Liste enthalten sind, werden modelliert.
    allowed_parts = [
        "Start Point",
        "Sequence of Activities",
        "Parallel Activities",
        "Decision Points",
        "Loops and Cycles",
        "End Points",
    ]

    # Abschnitte, die diese Schlüsselwörter enthalten, werden ignoriert (z. B. "Summary").
    excluded_keywords = ["Summary"]

    # Filtern der Abschnitte der Prozessbeschreibung
    # Es werden nur Abschnitte behalten, die in der Liste der erlaubten Abschnitte enthalten sind
    # und keine der ausgeschlossenen Schlüsselwörter enthalten.
    filtered_process_parts = []
    for part in process_parts:
        is_allowed = False
        contains_excluded = False

        for allowed_part in allowed_parts:
            if allowed_part in part:
                is_allowed = True
                break

        for excluded_keyword in excluded_keywords:
            if excluded_keyword in part:
                contains_excluded = True
                break

        if is_allowed and not contains_excluded:
            filtered_process_parts.append(part)

    process_parts = filtered_process_parts
    models = []

    # Modellierung der einzelnen Abschnitte
    # Jeder Abschnitt der Prozessbeschreibung wird separat modelliert und das Ergebnis
    # in der Liste "models" gespeichert.
    for part in process_parts:
        if part.strip():
            # Der Typ des Abschnitts (z. B. "Start Point", "Sequence of Activities")
            # wird anhand der in ihm enthaltenen Schlüsselwörter bestimmt.
            part_type = None
            for key in prompts.keys():
                if key in part:
                    part_type = key
                    break

            # Der zum Abschnittsyp passende Prompt wird aus dem Dictionary "prompts" ausgewählt.
            selected_prompt = prompts.get(part_type, general_prompt)

            # Die Nachricht besteht aus dem ausgewählten Prompt und dem zu modellierenden Abschnitt.
            message = [
                SystemMessage(content=selected_prompt),
                HumanMessage(content=part.strip()),
            ]

            # Die Antwort des Sprachmodells (das modellierte Teilstück des Petri-Netzes) wird gespeichert.
            response = llm.invoke(message).content

            # Hinzufügen der Antwort zur Modellsammlung
            models.append(f"### {part_type}:\n{response}")

    # Allgemeiner Integrationsprompt
    # Dieser Prompt enthält allgemeine Anweisungen zur Integration mehrerer Teilmodelle
    # zu einem einzigen, zusammenhängenden Petri-Netz.
    general_integration_prompt = """
    <prompt>
        <description>You are an expert in Petri nets and their modeling. Your task is to integrate two provided process models into a single, cohesive Petri net model.</description>

        <Purpose>
            The goal is to connect two sections of a Petri net model by analyzing their start- and endpoints and establishing logical connections. You will sequentially integrate these sections to form a consistent and continuous Petri net.
        </Purpose>

        <Modeling_Guidelines>
            1. **Identify and Analyze Endpoints**:
                - Identify the **ending element** (either a Place or Transition) of the current section.
                - Identify the **starting element** (either a Place or Transition) of the following section.
                - Ensure that these elements are clearly identified before attempting to connect them.

            2. **Establish Logical Connections**:
                - **If the current section ends with a Transition and the next section starts with a Place**: 
                    - Directly connect the Transition from the current section to the Place in the next section using an Edge.
                - **If the current section ends with a Place and the next section starts with a Transition**: 
                    - Directly connect the Place from the current section to the Transition in the next section using an Edge.
                - **If both the current section ends with a Transition and the next section starts with a Transition**: 
                    - Insert a new Place between them to connect the two Transitions, then create Edges to and from this Place.
                - **If both the current section ends with a Place and the next section starts with a Place**: 
                    - Insert a new Transition between them to logically connect the two Places, then create Edges to and from this Transition.

            3. **Model the Connections**:
                - After determining the correct connections between sections, model these connections in the Petri net.
                - Ensure that each connection is accurately represented as an Edge, following the format "Place --> Transition" or "Transition --> Place".

            4. **Renumber and Finalize Elements**:
                - Renumber all Places (P1, P2, etc.) and Transitions (T1, T2, etc.) to maintain sequential and unique identifiers.
                - Ensure that numbering is consistent and continuous across the entire model.

            5. **Final Output**:
                - Provide the updated integrated model in three sections: Places, Transitions, and Edges.
                - Do not include any summaries, explanations, or additional text.
        </Modeling_Guidelines>
    </prompt>
    """

    # Spezifische Integrationsprompts für unterschiedliche Abschnitte
    # Diese Prompts erweitern den allgemeinen Integrationsprompt um spezifische Anweisungen
    # zur Integration der verschiedenen Abschnitte.
    integration_prompts = {
        "Start Point": general_integration_prompt
        + """
            <additional_instructions>
                <Purpose>
                    Your task is to ensure the Start Point integrates smoothly with the following section by connecting the initial state of the process to the next step in a logical sequence.
                </Purpose>

                <Examples>
                    **Example 1**:
                    - **Input**:
                        - **Places**:
                            - P1: Customer Enquiry Received
                        - **Transitions**:
                            (No transitions in the Start Point)
                        - **Edges**:
                            (No edges in the Start Point) #Ends with a Place

                        ### Sequence of Activities:
                        - **Places**:
                            - Enquiry Logged (Place)
                        - **Transitions**:
                            - Log Enquiry (Transition)
                        - **Edges**:
                            - Enquiry Logged (Place) --> Log Enquiry (Transition) # Starts with a Place

                    - **Output**:
                        - **Places**:
                            - P1: Customer Enquiry Received
                            - P2: Enquiry Logged
                        - **Transitions**:
                            - T1: Start Process # Inserted to connect the two sections
                            - T2: Log Enquiry
                        - **Edges**:
                            - P1 --> T1 # Inserted to connect the two sections
                            - T1 --> P2 # Inserted to connect the two sections
                            - P2 --> T2

                    **Example 2**:
                    - **Input**:
                        - **Places**:
                            - P1: Job Application Submitted
                        - **Transitions**:
                            (No transitions in the Start Point)
                        - **Edges**:
                            (No edges in the Start Point) # Ends with a Place

                        ### Decision Point:
                        - **Places**:
                            - Application Reviewed (Place)
                            - Application Rejected (Place)
                        - **Transitions**:
                            - Review Application (Transition)
                            - Reject Application (Transition)
                        - **Edges**:
                            - Application Reviewed (Place) --> Review Application (Transition) # Starts with a Place
                            - Application Rejected (Place) --> Reject Application (Transition)

                    - **Output**:
                        - **Places**:
                            - P1: Job Application Submitted
                            - P2: Application Reviewed
                            - P3: Application Rejected
                        - **Transitions**:
                            - T1: Start Process # Inserted to connect the two sections
                            - T2: Review Application
                            - T3: Reject Application
                        - **Edges**:
                            - P1 --> T1 # Inserted to connect the two sections
                            - T1 --> P2 # Inserted to connect the two sections
                            - P2 --> T2
                            - P3 --> T3

                    **Example 3**:
                    - **Input**:
                        - **Places**:
                            - P1: Initial Setup Complete
                        - **Transitions**:
                            (No transitions in the Start Point)
                        - **Edges**:
                            (No edges in the Start Point) #Ends with a Place

                        ### Parallel Activities:
                        - **Places**:
                            - Component A Prepared (Place)
                            - Component B Prepared (Place)
                        - **Transitions**:
                            - Prepare Component A and B (Transition)
                        - **Edges**:
                            - Prepare Component A and B (Transition) --> Component A Prepared (Place) #Starts with a Transition
                            - Prepare Component A and B (Transition) --> Component B Prepared (Place)

                    - **Output**:
                        - **Places**:
                            - P1: Initial Setup Complete
                            - P2: Component A Prepared
                            - P3: Component B Prepared
                        - **Transitions**:
                            - T1: Prepare Component A and B
                        - **Edges**:
                            - P1 --> T1 # Inserted to connect the two sections
                            - T1 --> P2
                </Examples>
            </additional_instructions>
        """,
        "Sequence of Activities": general_integration_prompt
        + """
            <additional_instructions>
                <Purpose>
                    Your task is to integrate the sequence of activities from the current section with the subsequent section, ensuring that the process flows logically from one step to the next.
                </Purpose>
                
                <Examples>
                    **Example 1**:
                    - **Input**:
                        - **Places**:
                            - P1: Initial Request
                            - P2: Request Logged
                        - **Transitions**:
                            - T1: Log Request
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2 # Ends with a Place

                        ### Sequence of Activities:
                        - **Places**:
                            - Request Reviewed (Place)
                            - Request Approved (Place)
                        - **Transitions**:
                            - Review Request (Transition)
                            - Approve Request (Transition)
                        - **Edges**:
                            - Request Reviewed (Place) --> Review Request (Transition) #Starts with a Place
                            - Review Request (Transition) --> Request Approved (Place)

                    - **Output**:
                        - **Places**:
                            - P1: Initial Request
                            - P2: Request Logged
                            - P3: Request Reviewed
                            - P4: Request Approved
                        - **Transitions**:
                            - T1: Log Request
                            - T2: Review Request
                            - T3: Approve Request
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T2 # Inserted to connect the two sections
                            - T2 --> P3
                            - P3 --> T3
                            - T3 --> P4

                    **Example 2**:
                    - **Input**:
                        - **Places**:
                            - P1: Order Placed
                        - **Transitions**:
                            - T1: Confirm Payment
                            - T2: Prepare Shipment
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> T2 # Ends with a Transition

                        ### Sequence of Activities:
                        - **Places**:
                            - Shipment Prepared (Place)
                            - Shipment Dispatched (Place)
                        - **Transitions**:
                            - Dispatch Shipment (Transition)
                        - **Edges**:
                            - Shipment Prepared (Place) --> Dispatch Shipment (Transition) # Starts with Place
                            - Dispatch Shipment (Transition) --> Shipment Dispatched (Place)

                    - **Output**:
                        - **Places**:
                            - P1: Order Placed
                            - P2: Shipment Prepared
                            - P3: Shipment Dispatched
                        - **Transitions**:
                            - T1: Confirm Payment
                            - T2: Prepare Shipment
                            - T3: Dispatch Shipment
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> T2
                            - T2 --> P2 # Inserted to connect the two sections
                            - P2 --> T3
                            - T3 --> P3

                    **Example 3**:
                    - **Input**:
                        ### Start Point:
                            - **Places**:
                                - P1: Customer Order Received
                            - **Transitions**:
                                (No transitions in the Start Point)
                            - **Edges**:
                                (No edges in the Start Point) # Ends with Place

                        ### Sequence of Activities:
                        - **Places**:
                            - Order Processed (Place)
                            - Invoice Generated (Place)
                        - **Transitions**:
                            - Process Order (Transition)
                            - Generate Invoice (Transition)
                        - **Edges**:
                            - Order Processed (Place) --> Process Order (Transition) # Starts with Place
                            - Process Order (Transition) --> Invoice Generated (Place)

                    - **Output**:
                        - **Places**:
                            - P1: Customer Order Received
                            - P2: Order Processed
                            - P3: Invoice Generated
                        - **Transitions**:
                            - T1: Start Order Processing # Inserted to connect the two sections
                            - T2: Process Order
                            - T3: Generate Invoice
                        - **Edges**:
                            - P1 --> T1 # Inserted to connect the two sections
                            - T1 --> P2 # Inserted to connect the two sections
                            - P2 --> T2
                            - T2 --> P3
                </Examples>
            </additional_instructions>
        """,
        "Parallel Activities": general_integration_prompt
        + """
            <additional_instructions>
                <Purpose>
                    Your task is to integrate parallel activities into the existing process flow, ensuring that all paths are synchronized correctly and logically with subsequent or preceding sections.
                </Purpose>

                <Examples>
                    **Example 1**:
                    - **Input**:
                        - **Places**:
                            - P1: Order Received
                            - P2: Payment Processed
                        - **Transitions**:
                            - T1: Process Payment
                            - T2: Confirm Order
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T2 # Ends with a Transition

                        ### Parallel Activities:
                        - **Places**:
                            - Pack Order (Place)
                            - Generate Invoice (Place)
                            - Order packed (Place)
                            - Invoice generated (Place)
                        - **Transitions**:
                            - Start Order (Transition)
                            - Packing Order (Transition)
                            - Generating Invoice (Transition)
                            - Complete Order (Transition)
                        - **Edges**:
                            - Start Order (Transition) --> Pack Order (Place) #Starts with a Transition
                            - Start Order (Transition) --> Generate Invoice (Place)
                            - Pack Order (Place) --> Packing Order (Transition)
                            - Packing Order (Transition) --> Order packed (Place)
                            - Order packed (Place) --> Complete Order (Transition)
                            - Generate Invoice (Place) --> Generating Invoice (Transition)
                            - Generating Invoice (Transition) --> Invoice generated (Place)
                            - Invoice generated (Place) --> Complete Order (Transition)

                    - **Output**:
                        - **Places**:
                            - P1: Order Received
                            - P2: Payment Processed
                            - P3: Order confirmed #inserted to connect the two sections
                            - P4: Pack Order
                            - P5: Generate Invoice
                            - P6: Order packed
                            - P7: Invoice generated
                        - **Transitions**:
                            - T1: Process Payment
                            - T2: Confirm Order
                            - T3: Start Order
                            - T4: Packing Order
                            - T5: Generating Invoice
                            - T6: Complete Order
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T2 
                            - T2 --> P3
                            - P3 --> T3
                            - T3 --> P4
                            - T3 --> P5
                            - P4 --> T4
                            - T4 --> P6
                            - P5 --> T5
                            - T5 --> P7
                            - P6 --> T6
                            - P7 --> T6

                    **Example 2**:
                    - **Input**:
                        - **Places**:
                            1. P1: Project
                            2. P2: Project Started
                        - **Transitions**:
                            1. T1: Start Project
                        - **Edges**:
                            1. P1 --> T1
                            2. T1 --> P2 # Ends with a Place

                        ### Parallel Activities:
                            - **Places**:
                                - Design Phase Started (Place)
                                - Development Phase Started (Place)
                                - Design Phase Completed (Place) # New Place
                                - Development Phase Completed (Place) # New Place
                            - **Transitions**:
                                - Start Design and Development (Transition)
                                - Develop (Transition) # New Transition
                                - Design (Transition) # New Transition
                                - Synchronize Design and Development (Transition)
                            - **Edges**:
                                - Start Design and Development (Transition) --> Design Phase Started (Place) # Starts with a Transition
                                - Start Design and Development (Transition) --> Development Phase Started (Place)
                                - Design Phase Started (Place) --> Design (Transition)
                                - Design (Transition) --> Design Phase Completed (Place)
                                - Development Phase Started (Place) --> Develop (Transition)
                                - Develop (Transition) --> Development Phase Completed (Place)
                                - Design Phase Completed (Place) --> Synchronize Design and Development (Transition)
                                - Development Phase Completed (Place) --> Synchronize Design and Development (Transition)

                    - **Output**:
                        - **Places**:
                            - P1: Project
                            - P2: Project Started
                            - P3: Design Phase Started
                            - P4: Development Phase Started
                            - P5: Design Phase Completed
                            - P6: Development Phase Completed
                        - **Transitions**:
                            - T1: Start Project
                            - T2: Complete Initial Planning
                            - T3: Start Design and Development
                            - T4: Develop # New Transition
                            - T5: Design # New Transition
                            - T6: Synchronize Design and Development
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T3 # Inserted to connect the two sections
                            - T3 --> P3
                            - T3 --> P4
                            - P3 --> T5
                            - T5 --> P5
                            - P4 --> T4
                            - T4 --> P6
                            - P5 --> T6
                            - P6 --> T6
                </Examples>
            </additional_instructions>
        """,
        "Decision Point": general_integration_prompt
        + """
            <additional_instructions>
                <Purpose>
                    Your task is to correctly integrate a decision point within the current process section, ensuring that the decision starts from a Place and branches into different Transitions representing the possible outcomes. Ensure that all decision pathways are accurately modeled and logically connected to the subsequent sections.
                </Purpose>
                
                <Examples>
                    **Example 1**:
                    - **Input**:
                        - **Places**:
                            - P1: Application Received
                            - P2: Application Reviewed
                        - **Transitions**:
                            - T1: Review Application
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2 # Ends with a Place

                        ### Decision Point:
                        - **Places**:
                            - Decision (Place)
                            - Application Approved (Place)
                            - Application Rejected (Place)
                        - **Transitions**:
                            - Approve Application (Transition)
                            - Reject Application (Transition)
                        - **Edges**:
                            - Decision (Place) --> Approve Application (Transition) #starts with a Place
                            - Decision (Place) --> Reject Application (Transition)
                            - Approve Application (Transition) --> Application Approved (Place)
                            - Reject Application (Transition) --> Application Rejected (Place)

                    - **Output**:
                        - **Places**:
                            - P1: Application Received
                            - P2: Application Reviewed
                            - P3: Decision Point
                            - P4: Application Approved
                            - P5: Application Rejected
                        - **Transitions**:
                            - T1: Review Application
                            - T2: Make Decision #inserted to connect the two sections
                            - T3: Approve Application
                            - T4: Reject Application
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T2 # inserted to connect the two sections
                            - T2 --> P3 # inserted to connect the two sections
                            - P3 --> T3
                            - P3 --> T4
                            - T3 --> P4
                            - T4 --> P5

                    **Example 2**:
                    - **Input**:
                        - **Places**:
                            - P1: Order Placed
                        - **Transitions**:
                            - T1: Process Order
                        - **Edges**:
                            - P1 --> T1 # Ends with a Transition
                        ### Decision Point:
                        - **Places**:
                            - Order Processed (Place)
                            - Payment Confirmed (Place)
                            - Payment Failed (Place)
                        - **Transitions**:
                            - Confirm Payment (Transition)
                            - Deny Payment (Transition)
                        - **Edges**:
                            - Order Processed (Place) --> Confirm Payment (Transition) # starts with Place
                            - Order Processed (Place) --> Deny Payment (Transition)
                            - Confirm Payment (Transition) --> Payment Confirmed (Place)
                            - Deny Payment (Transition) --> Payment Failed (Place)
                    - **Output**:
                        - **Places**:
                            - P1: Order Placed
                            - P2: Order Processed # Decision Point
                            - P3: Payment Confirmed
                            - P4: Payment Failed
                        - **Transitions**:
                            - T1: Process Order
                            - T2: Confirm Payment
                            - T3: Retry Payment
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2 # Inserted to connect the two sections
                            - P2 --> T2
                            - P2 --> T3
                            - T2 --> P3
                            - T3 --> P4
                </Examples>
            </additional_instructions>
        """,
        "Loops and Cycles": general_integration_prompt
        + """
            <additional_instructions>
                <Purpose>
                    Your task is to correctly integrate loops and cycles within the current process section, ensuring that the flow can return to a previous state or repeat a set of activities based on certain conditions. Ensure that the loop starts and ends at the correct Places and that the cycle is logically connected to the subsequent sections.
                </Purpose>
                
                <Examples>
                    **Example 1**:
                    - **Input**:
                        - **Places**:
                            - P1: Task Started
                            - P2: Task In Progress
                            - P3: Task Performed
                        - **Transitions**:
                            - T1: Start Task
                            - T2: Perform Task
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2 
                            - P2 --> T2
                            - T2 --> P3 # Ends with a Place

                        ### Loops and Cycles:
                        - **Places**:
                            - Task Reviewed (Place)
                            - Task Confirmed (Place)
                            - Task Repeated (Place)
                        - **Transitions**:
                            - Review Task (Transition)
                            - Confirm Task (Transition)
                            - Repeat Task (Transition)
                        - **Edges**:
                            - Review Task (Transition) --> Task Reviewed (Place) # Starts with a Transition
                            - Task Reviewed (Place) --> Repeat Task (Transition)
                            - Task Reviewed (Place) --> Confirm Task (Transition)
                            - Confirm Task (Transition) --> Task Confirmed (Place)
                            - Repeat Task (Transition) --> Task Repeated (Place)
                            - Task Repeated --> Review Task (Transition)

                    - **Output**:
                        - **Places**:
                            - P1: Task Started
                            - P2: Task In Progress
                            - P3: Task Performed
                            - P4: Task Reviewed
                            - P5: Task Confirmed
                            - P6: Task Repeated
                        - **Transitions**:
                            - T1: Start Task
                            - T2: Perform Task
                            - T3: Review Task
                            - T4: Confirm Task
                            - T5: Repeat Task
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T2
                            - T2 --> P3
                            - P3 --> T3 # inserted this edge to connect the two sections correctly
                            - T3 --> P4
                            - P4 --> T4
                            - P4 --> T5
                            - T4 --> P5
                            - T5 --> P6
                            - P6 --> T3 # Loops back
            </additional_instructions>
        """,
        "Endpoints": general_integration_prompt
        + """
            <additional_instructions>
                <Purpose>
                    Your task is to correctly integrate the endpoint within the current process section, ensuring that the process flow concludes logically at a single final Place. This Place represents the end of the process, and no further transitions should occur after it.
                </Purpose>
                
                <Examples>
                    **Example 1**:
                    - **Input**:
                        - **Places**:
                            - P1: Customer Invoice Generated
                            - P2: Payment Processed
                            - P3: Shipment Dispatched
                        - **Transitions**:
                            - T1: Generate Invoice
                            - T2: Process Payment
                            - T3: Dispatch Shipment
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T2
                            - T2 --> P3
                            - P3 --> T3 # Ends with a Transition

                        ### Endpoint:
                        - **Places**:
                            - Process Completed (Place)
                        - **Transitions**:
                            - None (This is the final place)
                        - **Edges**:
                            - None

                    - **Output**:
                        - **Places**:
                            - P1: Customer Invoice Generated
                            - P2: Payment Processed
                            - P3: Shipment Dispatched
                            - P4: Process Completed
                        - **Transitions**:
                            - T1: Generate Invoice
                            - T2: Process Payment
                            - T3: Dispatch Shipment
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T2
                            - T2 --> P3
                            - T3 --> P4 # Final connection to the endpoint

                    **Example 2**:
                    - **Input**:
                        - **Places**:
                            - P1: Final Product Tested
                            - P2: Quality Assurance Passed
                            - P3: Product Packaged
                            - P4: Ready for Shipment
                            - P5: Product Shipped
                        - **Transitions**:
                            - T1: Test Final Product
                            - T2: Perform Quality Assurance
                            - T3: Package Product
                            - T4: Prepare Shipment
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T2
                            - T2 --> P3
                            - P3 --> T3
                            - T3 --> P4
                            - P4 --> T4
                            - T4 --> P5 # Ends with a Place

                        ### Endpoint:
                        - **Places**:
                            - Product Shipped (Place)
                        - **Transitions**:
                            - None (This is the final place)
                        - **Edges**:
                            - None

                    - **Output**:
                        - **Places**:
                            - P1: Final Product Tested
                            - P2: Quality Assurance Passed
                            - P3: Product Packaged
                            - P4: Ready for Shipment
                            - P5: Product Shipped
                        - **Transitions**:
                            - T1: Test Final Product
                            - T2: Perform Quality Assurance
                            - T3: Package Product
                            - T4: Prepare Shipment
                        - **Edges**:
                            - P1 --> T1
                            - T1 --> P2
                            - P2 --> T2
                            - T2 --> P3
                            - P3 --> T3
                            - T3 --> P4
                            - T4 --> P5 # Final connection to the endpoint
                </Examples>
            </additional_instructions>
        """,
    }

    # Integration der einzelnen Modelle
    # Die modellierten Abschnitte werden sequentiell miteinander verbunden,
    # um ein zusammenhängendes Petri-Netz zu erstellen.
    combined_model = models[0]  # Beginne mit dem ersten Modell

    for i in range(1, len(models)):
        # Bestimme den Abschnittstyp (z.B. "Start Point", "Sequence of Activities", etc.)
        part_type = None
        for key in integration_prompts.keys():
            if key in models[i]:
                part_type = key
                break

        # Wähle den entsprechenden Integration-Prompt
        selected_integration_prompt = integration_prompts.get(
            part_type, general_integration_prompt
        )

        # Kombinieren des aktuellen Petri-Netz mit dem nächsten Abschnitt
        combined_input = f"{combined_model}\n###\n{models[i]}"

        # Erstelle die Nachricht mit dem Integration-Prompt
        integration_message = [
            SystemMessage(content=selected_integration_prompt),
            HumanMessage(content=combined_input),
        ]

        # Führe die Integration durch und speichere das aktualisierte Petri-Netz
        combined_model = llm.invoke(integration_message).content

    # Rückgabe des Petri-Netzes
    return {"process_modell": [combined_model]}


def critique(state):

    critique_prompt = """
    You are an expert in process modeling and Petri Nets. Your task is to review the provided Petri Net model for correctness and provide detailed feedback on its accuracy. Follow these steps:
    **Verify Structural Integrity:**
    1. Check if there are edges that connect two places or two transitions with each other. That is the only thing that is not allowed in a petri net. Edges between the same type of object.
    **Check Process Flow:**
    1. Verify that the petri net starts with a Place and ends with a Place.
    **Provide Feedback:**
    1. Highlight any detected errors in the model.
    2. Confirm the correctness of the model if no errors are found.
    

    **Example Valid Output:**
    
    Correctness Feedback:
    The model starts with Place P1 and ends with Place P2.
    No invalid edges detected (Place to Place or Transition to Transition).
    The model is correct and does not require any changes.
    
    **Example Invalid Output with Feedback:**
    
    Errors Detected:
    Invalid Edge Detected:
    Edge from T1 to T2 (Error: Transition to Transition)
    Net Does Not Start with Place:
    First edge is from Transition T1 (Error: Net starts with Transition)
    Correct Invalid Edge:
    Change the edge from T1 to T2 to connect via a Place, e.g., P3.
    Corrected Edge: T1 --> P3, P3 --> T2
    Start Net with Place:
    Ensure the first edge starts from a Place, e.g., P1.
    Corrected Edge: P1 --> T1
    
    **Output:**
    Only answer with the issues and then the recommendation on how to solve the issues.
    """

    modell = state["process_modell"]
    process_modell = modell[-1]

    message = [
        SystemMessage(content=critique_prompt),
        HumanMessage(content=process_modell),
    ]

    response = llm.invoke(message).content

    return {"critique": [response]}


def improve(state):

    improve_prompt = """You are an expert in process modeling and Petri Nets. Your task is to improve a provided Petri Net model based on the given feedback. You should only answer with the improved Petri Net, don't explain what you changed or anything else, just the Petri Net. Follow these steps to update the model accurately:

    Input:
    Petri Net Model:

    Places, Transitions, and Edges in the current model.
    Feedback:

    Detailed feedback highlighting errors and suggested improvements.
    Steps to Improve the Petri Net:
    Review Feedback:

    Thoroughly understand the feedback provided.
    Identify specific errors and the recommended changes.
    Modify the Petri Net:

    Correct invalid edges (e.g., Place to Place or Transition to Transition).
    Just answer with the improved Petri Net nothing more.
    
    <output>
            <places>List all places with their names.</places>
            <transitions>List all transitions with their names.</transitions>
            <edges>List all edges in the format "Place --> Transition" or "Transition --> Place".</edges>
            <summary>Do not include any summaries or explanations. Only provide the structured lists of places, transitions, and edges.</summary>
        </output>
    """

    modell = state["process_modell"]
    process_modell = modell[-1]
    critique = state["critique"]
    last_critique = critique[-1]

    process_modell_str = str(process_modell)
    last_critique_str = str(last_critique)

    process_modell_and_critique = (
        "The process modell: "
        + process_modell_str
        + "and the critique: "
        + last_critique_str
    )

    message = [
        SystemMessage(content=improve_prompt),
        HumanMessage(content=process_modell_and_critique),
    ]

    response = llm.invoke(message).content

    return {"process_modell": [response]}


def call_pydantic_output_parser(state):
    modell = state["process_modell"]
    process_modell = modell[-1]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
        You are an expert in transforming an input into a desired output.
        You only use the information provided named Transitions, Places and Edges to create a Petri net.
        Label Places as 'Object Store'.
        Label Transitions as 'Activity'.
        Don't ever create an edge between an 'Activity' and an 'Activity'.
        Don't ever create an edge between an 'Object Store' and an 'Object Store'.
        Edges are only allowed between an 'Object Store' and an 'Activity'.

        {format_instructions}

        Make sure to answer in the correct format
        """,
            ),
            ("human", "{input}"),
        ]
    )

    parser = JsonOutputParser(pydantic_object=PetriNetTransition)

    chain = prompt | llm | parser

    result = chain.invoke(
        {
            "input": process_modell,
            "format_instructions": parser.get_format_instructions(),
        }
    )

    with open("process_description.json", "w") as json_file:
        json.dump(result, json_file, indent=4, ensure_ascii=False)

    print("Die JSON-Datei wurde erfolgreich erstellt und gespeichert.")

    return result
