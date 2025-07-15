from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

async def read_notes(app: MCPApp):
    logger = app.logger
    context = app.context

    logger.info("Current config:", data=context.config.model_dump())

    data_aggregator = Agent(
        name="data_aggregator",
        instruction="You are a data agent with filesystem access.",
        server_names=["filesystem"]
    )

    async with data_aggregator:
        logger.info("data_aggregator connected")
        llm = await data_aggregator.attach_llm(OpenAIAugmentedLLM)

        result = await llm.generate_str(
                message="Print the contents of /home/me/Downloads/notes.txt")
        logger.info(f"Result: {result}")

        result = await llm.generate_str(
                message="Summarize these notes")
        logger.info(f"Result: {result}")
