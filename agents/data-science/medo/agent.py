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
from datetime import date

from google.genai import types

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_artifacts, google_search

from .sub_agents.bigquery.tools import get_database_settings

from .prompts import build_orchestrator_prompt
from .tools import (
    call_db_agent,
    call_ds_agent,
    get_store_description,
    call_search_agent,
)

date_today = date.today()

data_sources = {
    "Retrieve Data": {
        "tool_name": "call_db_agent",
        "description": "If you need to query the database, use this tool. Make sure to provide a proper SQL query to it to fulfill the task.",
        "usage_summary": "Once you return the answer, provide additional explanations.",
        "key_reminder": "DO NOT generate SQL code, ALWAYS USE call_db_agent to generate the SQL if needed."
    },
    "Get Store Info": {
        "tool_name": "get_store_description",
        "description": "If you need text description about available stores, use this tool to retrieve all descriptions.",
        "usage_summary": "Use store details to recommend appropriate options or explain differences between stores.",
        "key_reminder": "ALWAYS reference specific store features and specialties when making recommendations based on store information."
    },
    "Perform Google Search": {
        "tool_name": "call_search_agent",
        "description": "If the user EXPLICITLY requests to search for external information or if the question clearly requires up-to-date information beyond today's date, use this tool.",
        "usage_summary": "After receiving search results, critically evaluate the information before incorporating it into your response.",
        "key_reminder": "DO NOT use search unless explicitly requested by the user or absolutely necessary for time-sensitive information. Always prioritize internal data sources first."
    }
}

# Example usage of build_orchestrator_prompt with data_sources
orchestrator_prompt = build_orchestrator_prompt(available_data_sources=data_sources)

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    # setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # setting up schema in instruction
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        callback_context._invocation_context.agent.instruction = (
            orchestrator_prompt
            + f"""

    --------- The BigQuery schema of the relevant data with a few sample rows. ---------
    {schema}

    """
        )


root_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL"),
    name="medo_agent",
    instruction=orchestrator_prompt,
    global_instruction=(
        f"""
        You are a Data Science and Data Analytics Multi Agent System.
        Todays date: {date_today}
        """
    ),
    tools=[
        call_db_agent,
        call_ds_agent,
        load_artifacts,
        get_store_description,
        call_search_agent,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
