from langchain_core.messages import AIMessage


def _get_tool_calls(run) -> list[dict]:
    """Extract tool calls and their arguments in execution order."""

    messages = run.outputs["messages"]

    if not messages:
        return []

    tool_calls = []

    for message in messages:
        if isinstance(message, AIMessage):
            for tool_call in message.tool_calls:
                tool_calls.append({
                    "name": tool_call["name"],
                    "args": tool_call["args"],
                })

    return tool_calls


def _value_matches(actual, expected) -> bool:
    """
    Compare an actual tool argument against its golden expectation.

    Normal values require an exact match. String arguments can use an
    `includes` constraint when multiple equivalent values are acceptable,
    such as semantically equivalent SQL queries with different formatting.
    """

    if isinstance(expected, dict) and "includes" in expected:
        if not isinstance(actual, str):
            return False

        return all(
            required.casefold() in actual.casefold()
            for required in expected["includes"]
        )

    return actual == expected


def _args_match(
    actual_args: dict,
    expected_args: dict,
) -> bool:
    """
    Check only arguments specified by the golden dataset.

    Additional tool arguments are allowed so the evaluator does not become
    coupled to optional arguments that are irrelevant to the behavior being
    tested.
    """

    for arg_name, expected_value in expected_args.items():
        if arg_name not in actual_args:
            return False

        if not _value_matches(
            actual=actual_args[arg_name],
            expected=expected_value,
        ):
            return False

    return True


def agent_tool_args_correct(run, example):
    """
    Evaluate whether tools were called with the expected arguments.

    A tool may be called multiple times during investigation or recovery.
    The evaluation passes when at least one call to each expected tool
    satisfies its golden argument constraints. This avoids penalizing the
    agent for valid retries or additional analytical steps.
    """

    tool_calls = _get_tool_calls(run)
    expected_tool_args = example.outputs["tool_args"]

    if not tool_calls:
        return {
            "key": "agent_tool_args_correct",
            "score": False,
            "comment": "No tool calls were made",
        }

    for tool_name, expected_args in expected_tool_args.items():

        matching_tool_calls = [
            tool_call
            for tool_call in tool_calls
            if tool_call["name"] == tool_name
        ]

        if not matching_tool_calls:
            return {
                "key": "agent_tool_args_correct",
                "score": False,
                "comment": f"Expected tool '{tool_name}' was not called",
            }

        has_valid_args = any(
            _args_match(
                actual_args=tool_call["args"],
                expected_args=expected_args,
            )
            for tool_call in matching_tool_calls
        )

        if not has_valid_args:
            return {
                "key": "agent_tool_args_correct",
                "score": False,
                "comment": (
                    f"Tool '{tool_name}' was not called with "
                    "the expected arguments"
                ),
            }

    return {
        "key": "agent_tool_args_correct",
        "score": True,
        "comment": "All expected tools were called with valid arguments",
    }