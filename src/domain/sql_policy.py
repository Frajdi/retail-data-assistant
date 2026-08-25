from pandas import DataFrame

from sqlglot import parse_one
from sqlglot.expressions import (
    Select,
    Table,
    Column,
    Count,
    Sum,
    Avg
)
from sqlglot.errors import ParseError

from src.domain.errors import QueryErrorType, QueryExecutionError
from src.domain.data_policy import ExposurePolicy, FIELD_POLICIES


# Aggregations that produce analytical values rather than exposing the
# underlying source value directly. Aggregates such as MIN/MAX are excluded
# because they may return an actual sensitive value from the dataset.
SAFE_AGGREGATES = (
    Count,
    Sum,
    Avg,
)

def _is_safe_aggregate(projection) -> bool:
    return any(
        projection.find(aggregate) is not None
        for aggregate in SAFE_AGGREGATES
    )




def _get_table_aliases(expression) -> dict[str, str]:

    """
    Map SQL table aliases back to their physical table names.
    Example:
        FROM users u
        -> {"u": "users"}
    """

    aliases = {}

    for table in expression.find_all(Table):
        aliases[table.alias_or_name] = table.name

    return aliases




def _resolve_column_source(
    column: Column,
    aliases: dict[str, str],
) -> str | None:

    """
    Resolve a SQL column to the field used by the data policy.
    Examples:

        u.email -> users.email
        email FROM users -> users.email

    Ambiguous unqualified columns in multi-table queries are not guessed.
    """

    # Qualified column: u.email -> users.email
    if column.table:
        table_name = aliases.get(
            column.table,
            column.table,
        )

        return f"{table_name}.{column.name}"

    # An unqualified column can be safely resolved when the query
    # references exactly one physical table.
    unique_tables = set(aliases.values())

    if len(unique_tables) == 1:
        table_name = next(iter(unique_tables))

        return f"{table_name}.{column.name}"

    # Multiple possible source tables: do not infer lineage.
    return None




def validate_read_only_query(sql_query: str) -> Select:
    """
    Parse the generated SQL and enforce the read-only query boundary.
    Returning the parsed AST allows downstream policy checks to reuse it
    without parsing the SQL again.
    """

    try:
        expression = parse_one(
            sql=sql_query,
            dialect="bigquery"
        )
    except ParseError as e:
        raise QueryExecutionError(
            error_type=QueryErrorType.INVALID_SQL,
            message=f"Invalid SQL: {e}",
        ) from e

    if not isinstance(expression, Select):
        raise QueryExecutionError(
            error_type=QueryErrorType.POLICY_VIOLATION,
            message="Only read-only SELECT queries are allowed.",
        )

    return expression


def get_output_policies(
    expression: Select,
) -> dict[str, ExposurePolicy]:

    """
    Determine the exposure policy for each projected query result column
    from its source-column lineage.
    """

    aliases = _get_table_aliases(expression)
    output_policies = {}

    for projection in expression.expressions:
        output_name = projection.alias_or_name

        source_columns = []

        # Track the physical fields contributing to this output expression.
        # This preserves PII classification through aliases and transformations.
        for column in projection.find_all(Column):
            source = _resolve_column_source(
                column=column,
                aliases=aliases,
            )

            if source is not None:
                source_columns.append(source)

        policies = [
            FIELD_POLICIES[source].exposure
            for source in source_columns
            if source in FIELD_POLICIES
        ]

        # Safe aggregates may operate on sensitive fields because their
        # result does not expose the original value.
        #
        # Example:
        # COUNT(DISTINCT email) -> 84137       ALLOW
        # MAX(email)            -> user@...    MASK

        if _is_safe_aggregate(projection):
            output_policies[output_name] = ExposurePolicy.ALLOW
            continue

        # Apply the most restrictive policy inherited from source fields.
        if ExposurePolicy.DROP in policies:
            output_policies[output_name] = ExposurePolicy.DROP

        elif ExposurePolicy.MASK in policies:
            output_policies[output_name] = ExposurePolicy.MASK

        else:
            output_policies[output_name] = ExposurePolicy.ALLOW

    return output_policies



def sanitize_query_result(
    result: DataFrame,
    output_policies: dict[str, ExposurePolicy],
) -> DataFrame:

    """
    Apply output policies before query results are returned to the agent.
    Raw sensitive values therefore never enter the model's conversation
    context when they are classified as MASK or DROP.
    """
    
    safe_result = result.copy()

    for column, policy in output_policies.items():
        if column not in safe_result.columns:
            continue

        if policy == ExposurePolicy.MASK:
            safe_result[column] = "[REDACTED]"

        elif policy == ExposurePolicy.DROP:
            safe_result.drop(
                columns=[column],
                inplace=True,
            )

    return safe_result