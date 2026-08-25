from enum import Enum
from pydantic import BaseModel

from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from src.agent.state import AgentContext


class TableName(Enum):
    PRODUCTS = "products"
    ORDERS = "orders"
    ORDER_ITEMS = "order_items"
    USERS = "users"

class GetTableSchemaArgs(BaseModel):
    table_name: TableName


@tool("get_table_schema", args_schema=GetTableSchemaArgs)
def get_table_schema(
    table_name: TableName,
    runtime: ToolRuntime[AgentContext]
):
    """
        Retrieve the schema of an available database table,
        including its column names and data types.
    """

    big_query_service = runtime.context.big_query_service

    try:
        return big_query_service.get_table_schema(table_name=table_name.value)
    except Exception as e:
        return str(e)