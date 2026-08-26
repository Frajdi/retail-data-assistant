from dotenv import load_dotenv

load_dotenv()

from typing import cast
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI




class FinalResponseEvaluation(BaseModel):
    score: int = Field(
        ge=0,
        le=1,
        description="1 if the response satisfies the expected answer, otherwise 0."
    )
    reasoning: str = Field(description="Short explanation of why the response passed or failed.")




judge = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
).with_structured_output(FinalResponseEvaluation)




def agent_final_response_correct(run, example):
    """
    Evaluate the agent's final response against the golden expected response.

    An LLM judge is used instead of exact string matching because the agent may
    express the correct answer using different wording or formatting. The judge
    evaluates semantic correctness rather than requiring a verbatim match.
    """

    messages = run.outputs["messages"]

    if not messages:
        return {
            "key": "agent_final_response_correct",
            "score": 0,
            "comment": "The agent produced no messages.",
        }

    final_response = messages[-1].content
    expected_response = example.outputs["final_response_must_include"]
    question = example.inputs["question"]

    evaluation = cast(
        FinalResponseEvaluation,
        judge.invoke(
            f"""
                You are evaluating the final response of a retail data analysis agent.

                Determine whether the agent's response correctly satisfies the expected
                answer for the user's question.

                USER QUESTION:
                {question}

                EXPECTED ANSWER:
                {expected_response}

                AGENT RESPONSE:
                {final_response}

                EVALUATION RULES:
                - Score 1 if the agent response communicates the expected answer correctly.
                - Score 0 if the expected answer is missing, contradicted, or incorrect.
                - Do not require exact wording or formatting.
                - Equivalent wording and numerical formatting should be accepted.
                - Ignore additional information unless it contradicts the expected answer.
                - Evaluate only the final response, not the agent's internal tool usage.
            """
        )
    )

    return {
        "key": "agent_final_response_correct",
        "score": evaluation.score,
        "comment": evaluation.reasoning,
    }