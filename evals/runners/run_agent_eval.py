from dotenv import load_dotenv

load_dotenv()

import asyncio
from uuid import uuid4

from langsmith import aevaluate

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.agent.graph import agent
from src.agent.state import AgentState, AgentContext

from src.infrastructure.big_query import BigQueryRunner

from evals.evals import evaluators



async def run_agent_eval(inputs:dict) -> dict:
    user_query = inputs["question"]

    initial_state = AgentState(
        messages=[
            HumanMessage(
                content=user_query,
            )
        ]
    )

    context = AgentContext(
        big_query_service=BigQueryRunner()
    )

    config = RunnableConfig(
            configurable={
                "thread_id": uuid4()
            }
        )


    result = await agent.ainvoke(input=initial_state, context=context, config=config)

    return {
        "result": result,
        "messages": result["messages"],
        "final_answer": result["messages"][-1].text,
    }

if __name__ == "__main__":
    asyncio.run(
        aevaluate(
            run_agent_eval,
            data="retail_data_agent_evals",
            evaluators=evaluators,
            experiment_prefix="agent_eval",
        )
    )
