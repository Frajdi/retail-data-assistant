from .schema_tool import get_table_schema
from .query_tool import execute_query

tools = [
    get_table_schema,
    execute_query
]