from dotenv import load_dotenv

load_dotenv()

import asyncio
from uuid import uuid4, UUID

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.agent.graph import agent, AgentState, AgentContext
from src.infrastructure.big_query import BigQueryRunner


async def ask_agent(question: str, thread_id: UUID, big_query_service: BigQueryRunner):

    input = AgentState(
            messages=[
                HumanMessage(content=question)
            ]
        )

    config = RunnableConfig(
        configurable={
            "thread_id": thread_id
        }
    )

    task = asyncio.create_task(agent.ainvoke(
        input = input,
        config = config,
        context=AgentContext(
            big_query_service=big_query_service
        )
    ))

    await task

    return task.result()





async def run_cli():

    conversation_thread_id = uuid4()
    big_query_service = BigQueryRunner()

    print("Retail Data Assistant")

    while True:
        question = input("You: ").strip()

        if not question:
            continue

        try: 
            result = await ask_agent(
                question=question,
                thread_id=conversation_thread_id,
                big_query_service=big_query_service
            )

            response = result["messages"][-1].content

            print(f"\nAssistant:\n{response}\n")

        except Exception as e:
            print(str(e))





if __name__ == '__main__':
    asyncio.run(run_cli())


