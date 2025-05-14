# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use NL2Py to do further data analysis as needed
"""
import os

from google.adk.tools import ToolContext
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import ds_agent, db_agent


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    agent_tool = AgentTool(agent=db_agent)

    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output


async def call_ds_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call data science (nl2py) agent."""

    if question == "N/A":
        return tool_context.state["db_agent_output"]

    input_data = tool_context.state["query_result"]

    question_with_data = f"""
  Question to answer: {question}

  Actual data to analyze prevoius quesiton is already in the following:
  {input_data}

  """

    agent_tool = AgentTool(agent=ds_agent)

    ds_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    tool_context.state["ds_agent_output"] = ds_agent_output
    return ds_agent_output

def get_store_description() -> str:
    """
    Retrieves the description of all available stores.

    Returns:
        str: Combined description of all available stores.
    """
# Module-level constant for store descriptions
STORE_DESCRIPTIONS = {
    "Discount Stickers": "Budget-friendly stickers for all occasions with thousands of designs. Features unique eco-friendly paper options popular with teachers and event planners who value sustainability without sacrificing quality.",
    
    "Stickers for Less": "High-volume, customizable stickers with a proprietary online design tool. Offers seasonal designs and durable materials with industry-leading shipping times for both businesses and individuals.",
    
    "Premium Sticker Mart": "Luxury holographic and metallic stickers using patented materials and 3D printing. Known for limited-edition artist collaborations and exceptional durability that appeals to collectors and designers."
}

def get_store_description() -> str:
    """
    Retrieves the description of all available stores.

    Returns:
        str: Combined description of all available stores.
    """
    # Return combined description of all stores
    return "\n\n".join(STORE_DESCRIPTIONS.values())

google_search_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL"),
    name="google_search_agent",
    description="Agent to answer questions using Google Search.",
    instruction="You are an expert researcher. You always stick to the facts.",
    tools=[google_search]
)

call_search_agent = AgentTool(agent=google_search_agent)
