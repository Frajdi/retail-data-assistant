from .schema_tool import get_table_schema
from .think_tool import think
from .query_tool import execute_query

tools = [
    get_table_schema,
    think,
    execute_query
]