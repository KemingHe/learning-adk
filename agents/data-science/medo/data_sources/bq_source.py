"""
BigQuery data source implementation.
"""

from typing import Dict

from ..sub_agents.bigquery.tools import get_database_settings
from .base import DataSourceProvider


class BigQueryDataSource(DataSourceProvider):
    """
    BigQuery data source provider implementation.
    """
    
    def get_name(self) -> str:
        """
        Get the name of this data source.
        
        Returns:
            str: The data source name
        """
        return "BigQuery"
    
    def get_settings(self) -> Dict:
        """
        Get the settings for this data source.
        
        Returns:
            Dict: A dictionary containing BigQuery settings
        """
        # Reuse existing BigQuery settings function
        return get_database_settings()
    
    def get_schema(self) -> str:
        """
        Get the schema information for this data source.
        
        Returns:
            str: The BigQuery schema information as a formatted string
        """
        settings = self.get_settings()
        return settings.get("bq_ddl_schema", "")
    
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities information for the orchestrator prompt builder.
        
        Returns:
            Dict: A dictionary containing BigQuery capability definitions
        """
        return {
            "Retrieve SQL Data": {
                "tool_name": "call_db_agent",
                "description": "If you need to query the BigQuery database, use this tool. Make sure to provide a proper SQL query to fulfill the task.",
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
            }
        }
    
    def validate_connection(self) -> bool:
        """
        Validate the connection to BigQuery.
        
        Returns:
            bool: True if the connection is valid, False otherwise
        """
        # In a real implementation, we would check if we can connect to BigQuery
        # For now, just return True
        return True
