import json
from pydantic import BaseModel

from langchain_core.tools import tool
from langchain.tools import ToolRuntime

from src.agent.state import AgentContext
from src.domain.query_models import QuerySuccess, QueryFailure
from src.domain.errors import QueryExecutionError, QueryErrorType
from src.domain.sql_policy import validate_read_only_query, get_output_policies, sanitize_query_result

class ExecuteQueryArgs(BaseModel):
    sql_query: str


@tool("execute_query", args_schema=ExecuteQueryArgs)
def execute_query(
    sql_query: str,
    runtime: ToolRuntime[AgentContext],
) -> dict:
    """
    Execute a read-only SQL query against the allowed retail dataset.
    Use this tool only after inspecting the relevant table schemas.
    """

    big_query_service = runtime.context.big_query_service

    try:

        expression = validate_read_only_query(sql_query)
        output_policies = get_output_policies(expression)
        result = big_query_service.execute_query(sql_query)
        if result.empty:
            return QuerySuccess(data=[]).model_dump(mode="json")

        safe_result = sanitize_query_result(
            result=result,
            output_policies=output_policies,
        )

        data = json.loads(
            safe_result.to_json(
                orient="records",
                date_format="iso",
            )
        )

        return QuerySuccess(data=data).model_dump(mode="json")

    except QueryExecutionError as e:
        return QueryFailure(
            error_type=e.error_type,
            error_message=e.message
        ).model_dump(mode="json")
    except Exception:
        return QueryFailure(
            error_type=QueryErrorType.UNKNOWN,
            error_message="Unexpected query execution failure."
        ).model_dump(mode="json")
