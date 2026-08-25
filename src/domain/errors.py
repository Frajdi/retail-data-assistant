from enum import Enum

class QueryErrorType(str, Enum):
    INVALID_SQL = "invalid_sql"
    POLICY_VIOLATION = "policy_violation"
    EMPTY_RESULT = "empty_result"
    PERMISSION = "permission"
    RATE_LIMIT = "rate_limit"
    SERVICE = "service"
    UNKNOWN = "unknown"

class QueryExecutionError(Exception):
    def __init__(
        self,
        error_type: QueryErrorType,
        message: str,
    ):
        self.error_type = error_type
        self.message = message
        super().__init__(message)