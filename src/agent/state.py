from typing import Annotated
from pydantic import BaseModel, ConfigDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from src.infrastructure.big_query import BigQueryRunner



class AgentState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    query_retries: int = 0


class AgentContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    big_query_service: BigQueryRunner