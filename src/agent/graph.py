import json

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage

from langgraph.types import Command
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from src.agent.tools import tools
from src.agent.prompts import SYSTEM_PROMPT
from src.domain.errors import QueryErrorType
from src.agent.state import AgentState, AgentContext
from src.domain.query_models import QuerySuccess, QueryFailure


# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
)

MAX_QUERY_RETRIES = 3

# llm = ChatOpenAI(
#     model="gpt-4.1-mini",
#     temperature=0,
#     max_retries=5,
# )
# llm = ChatOpenAI(
#     model="gpt-5.6-terra",
#     use_responses_api=True,
#     reasoning={
#         "effort": "medium",
#         "summary": "auto",
#     },
#     output_version="responses/v1",
# )

# Bind tools to the llm
model = llm.bind_tools(tools)

# Orchestrator Node
def call_model_node(state: AgentState):

    response = model.invoke(
        input=[
            SystemMessage(content=SYSTEM_PROMPT),
            *state.messages
        ]
    )

    if response.tool_calls:
        return Command(
            update={"messages": response},
            goto="call_tool_node"
        )
    else:
        return Command(
            update={"messages": response},
            goto=END
        )

# Tool Calling Node
call_tool_node = ToolNode(name="call_tool_node", tools=tools)




def get_latest_tool_messages(state: AgentState) -> list[ToolMessage]:
    tool_messages = []
    for message in reversed(state.messages):
        if not isinstance(message, ToolMessage):
            break
        tool_messages.append(message)

    return list(reversed(tool_messages))


# This node based on tool result routes accordingly if we need to retry or stop
def evaluate_tool_result_node(state: AgentState):

    tool_messages = get_latest_tool_messages(state)

    if not tool_messages:
        return Command(goto="call_model_node")

    query_messages = [
        message for message in tool_messages
        if message.name == "execute_query"
    ]

    if not query_messages:
        return Command(goto="call_model_node")

    has_recoverable_result = False

    for message in query_messages:
        content = message.content
        if not isinstance(content, str):

            return Command(
                update={
                    "messages": AIMessage(
                        content=(
                            "Something went wrong while processing "
                            "the query result. Please try again later."
                        )
                    )
                },
                goto=END,
            )

        # Classify response type based on data key
        try:
            data = json.loads(content)
            if "data" in data:
                result = QuerySuccess(**data)
            else:
                result = QueryFailure(**data)

        except (json.JSONDecodeError, ValueError):
            return Command(
                update={
                    "messages": AIMessage(
                        content=(
                            "Something went wrong while processing "
                            "the query result. Please try again later."
                        )
                    )
                },
                goto=END,
            )


        # Query executed successfully
        if isinstance(result, QuerySuccess):
            # Empty result is recoverable
            if not result.data:
                has_recoverable_result = True
            continue

        # Query execution failed
        if isinstance(result, QueryFailure):
            if result.error_type in {
                QueryErrorType.INVALID_SQL,
                QueryErrorType.POLICY_VIOLATION,
            }:
                has_recoverable_result = True
                continue

            return Command(
                update={
                    "messages": AIMessage(
                        content=(
                            "Something went wrong while accessing "
                            "the data. Please try again later."
                        )
                    )
                },
                goto=END,
            )

    if has_recoverable_result:
        if state.query_retries >= MAX_QUERY_RETRIES:

            return Command(
                update={
                    "query_retries": 0,
                    "messages": AIMessage(
                        content=(
                            "I couldn't complete the analysis after "
                            "multiple query attempts."
                        )
                    ),
                },
                goto=END,
            )

        return Command(
            update={
                "query_retries": state.query_retries + 1,
            },
            goto="call_model_node",
        )

    return Command(
        update={
            "query_retries": 0,
        },
        goto="call_model_node",
    )
        





# Attach our custom state and context schemas to graph initialization
graph = StateGraph(state_schema=AgentState, context_schema=AgentContext)


# Add Nodes and Edges for agent graph flow
graph.add_node(
    "call_model_node",
    call_model_node,
    destinations=("call_tool_node", END,)
)

graph.add_node(
    "call_tool_node",
    call_tool_node,
    destinations=("evaluate_tool_result_node",)
)

graph.add_node(
    "evaluate_tool_result_node",
    evaluate_tool_result_node,
    destinations=("call_model_node", END,)
)

graph.add_edge(
    "call_tool_node",
    "evaluate_tool_result_node"
)

# Set entrypoint the model Node
graph.set_entry_point("call_model_node")

# Compiling with InMemorySaver to presist memory accross agent human turns
# This is an in memory and will use the service memory instead of a DB for now
agent = graph.compile(checkpointer=InMemorySaver())