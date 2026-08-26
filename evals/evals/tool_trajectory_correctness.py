from langchain_core.messages import AIMessage


def _get_tool_calls(run) -> list[str]:
    """Extract tool calls from the agent execution in the order they occurred."""

    messages = run.outputs["messages"]

    if not messages:
        return []

    tool_calls = []

    for message in messages:
        if isinstance(message, AIMessage):
            for tc in message.tool_calls:
                tool_calls.append(tc["name"])

    return tool_calls





def _contains_sequence(
    actual: list[str],
    expected: list[str],
) -> bool:
    """
    Check that the expected tool trajectory occurred in the required order.

    The trajectory is treated as a required subsequence rather than an exact
    sequence. This allows the agent to make additional valid tool calls for
    planning, investigation, or recovery without being penalized, as long as
    the required workflow is still followed.
    """

    if not expected:
        return True

    expected_index = 0

    for tool_name in actual:
        if tool_name == expected[expected_index]:
            expected_index += 1

            if expected_index == len(expected):
                return True

    return False





def _required_tools_used(run, example):
    """Verify that all tools required by the golden example were used."""

    tool_calls = _get_tool_calls(run)
    expected_tools = example.outputs["tool_trajectory"]

    if not tool_calls:
        raise ValueError("No tool calls were made")

    if len(tool_calls) < len(expected_tools):
        raise ValueError("Too few tool calls were made")

    all_required_tools_used = set(expected_tools).issubset(set(tool_calls))

    if not all_required_tools_used:
        raise ValueError("The required tools were not used")






def agent_used_required_tools(run, example):
    """
    Evaluate whether the agent used all tools required to complete the task.

    This evaluator checks tool presence only. Ordering is evaluated separately
    so failures can clearly distinguish missing capabilities from an incorrect
    execution trajectory.
    """

    try:
        _required_tools_used(run, example)

    except Exception as e:
        return {
            "key": "agent_used_required_tools",
            "score": False,
            "comment": str(e),
        }

    return {
        "key": "agent_used_required_tools",
        "score": True,
        "comment": "All required tools were used",
    }






def agent_tool_sequence_valid(run, example):
    """
    Evaluate whether required tools were called in the expected relative order.

    Extra tool calls are intentionally allowed. An agent may need additional
    schema inspection, reasoning, or recovery steps, and should not fail the
    evaluation simply because it successfully recovered from uncertainty.
    """

    tool_calls = _get_tool_calls(run)
    expected_tools = example.outputs["tool_trajectory"]

    try:
        _required_tools_used(run, example)

    except Exception as e:
        return {
            "key": "agent_used_valid_tools_sequence",
            "score": False,
            "comment": str(e),
        }

    if _contains_sequence(tool_calls, expected_tools):
        return {
            "key": "agent_used_valid_tools_sequence",
            "score": True,
            "comment": "All required tools were used in correct sequence",
        }

    return {
        "key": "agent_used_valid_tools_sequence",
        "score": False,
        "comment": "The required tools were not used in correct sequence",
    }