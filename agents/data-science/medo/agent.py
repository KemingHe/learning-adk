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
from google.adk.tools import load_artifacts

from .sub_agents.bigquery.tools import get_database_settings
#from .data_sources.bq_source import BigQueryDataSource
from .prompts import build_orchestrator_prompt
from .tools import call_db_agent, call_ds_agent


date_today = date.today()

# def add_data_source(callback_context: CallbackContext, source_name: str):
#     """
#     Add a new data source to the active sources list.
    
#     Args:
#         callback_context: The callback context
#         source_name: Name of the data source to add
#     """
#     # Initialize data sources list if needed
#     if "data_sources" not in callback_context.state:
#         callback_context.state["data_sources"] = []
        
#     # Add the source if not already present
#     if source_name not in callback_context.state["data_sources"]:
#         callback_context.state["data_sources"].append(source_name)

# Original hardcoded data source capabilities  
data_sources = {
    "Retrieve Data": {
        "tool_name": "call_db_agent",
        "description": "If you need to query the database, use this tool. Make sure to provide a proper SQL query to it to fulfill the task.",
        "usage_summary": "Once you return the answer, provide additional explanations.",
        "key_reminder": "DO NOT generate SQL code, ALWAYS USE call_db_agent to generate the SQL if needed."
    },
    "SQL Database": {
        "tool_name": "call_db_agent",
        "description": "If the question needs SQL executions, forward it to the database agent.",
        "usage_summary": "Used for database queries that can be solved with SQL."
    },
    "SQL & Analysis": {
        "tool_name": "call_db_agent",
        "description": "If the question needs SQL execution and additional analysis, first forward it to the database agent to retrieve the data.",
        "usage_summary": "For compound questions requiring both SQL and further analysis, first use this to get the data."
    },
    "Data Science": {
        "tool_name": "call_ds_agent",
        "description": "If you need to perform data analysis or predictive modeling after retrieving data, use this tool.",
        "usage_summary": "Used for Python-based data analysis after data has been retrieved.",
        "key_reminder": "DO NOT generate Python code, ALWAYS USE call_ds_agent to generate further analysis if needed. IF data is available from previous agent calls, YOU CAN DIRECTLY USE call_ds_agent TO DO NEW ANALYZE USING THE DATA FROM PREVIOUS STEPS."
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

# def setup_before_agent_call(callback_context: CallbackContext):
#     """Setup the agent with all available data sources."""
    
#     # Initialize data sources if needed
#     if "data_sources" not in callback_context.state:
#         # Add default data sources
#         add_data_source(callback_context, "BigQuery")
        
#     # Get active data sources
#     active_sources = callback_context.state["data_sources"]
    
#     # Build combined capabilities for prompt
#     all_capabilities = {}
#     all_schemas = []
    
#     # Process each active data source
#     for source_name in active_sources:
#         # Create the appropriate data source provider based on name
#         if source_name == "BigQuery":
#             source = BigQueryDataSource()
            
#             # Get source settings (serializable)
#             settings = source.get_settings()
#             callback_context.state["source_settings_" + source_name] = settings
            
#             # Get capabilities for prompt builder
#             all_capabilities.update(source.get_capabilities())
            
#             # Get schema for instruction
#             schema = source.get_schema()
#             if schema:
#                 all_schemas.append(f"--------- {source_name} Schema ---------\n{schema}")
    
#     # Build orchestrator prompt with combined capabilities
#     combined_prompt = build_orchestrator_prompt(available_data_sources=all_capabilities)
    
#     # Inject all schemas into instruction
#     callback_context._invocation_context.agent.instruction = (
#         combined_prompt + "\n\n" + "\n\n".join(all_schemas)
#     )


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
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
