from pydantic import BaseModel, Field
from langchain_core.tools import tool


class ThinkArgs(BaseModel):
    problem: str = Field(
        description="The specific analytical problem that needs to be resolved."
    )
    known_facts: list[str] = Field(
        default_factory=list,
        description="Facts already established from previous query results."
    )
    uncertainties: list[str] = Field(
        default_factory=list,
        description="Assumptions or unknowns that still need to be verified."
    )
    next_steps: list[str] = Field(
        default_factory=list,
        description=(
            "Small, concrete analytical steps that would resolve the uncertainties. "
            "Prefer targeted diagnostic queries and independent queries that can be "
            "executed separately."
        )
    )


@tool("think", args_schema=ThinkArgs)
def think(
    problem: str,
    known_facts: list[str],
    uncertainties: list[str],
    next_steps: list[str],
):
    """
    Use this tool as a planning checkpoint when an analysis is complex,
    a query returns no data, or the direct analytical path fails.
    Break the problem into smaller evidence-gathering steps.
    Identify what is already known, what assumptions remain uncertain,
    and the smallest useful next steps.
    Do not use this tool to answer the user.
    Do not repeat equivalent failed queries.
    Prefer testing uncertain assumptions before retrying the original analysis.
    """
    return {
        "problem": problem,
        "known_facts": known_facts,
        "uncertainties": uncertainties,
        "next_steps": next_steps,
    }
