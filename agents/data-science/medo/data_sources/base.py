"""
Base provider interface for data sources.
"""

from abc import ABC, abstractmethod
from typing import Dict


class DataSourceProvider(ABC):
    """
    Abstract base class for data source providers.
    All data source implementations should inherit from this class.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this data source.
        
        Returns:
            str: The data source name
        """
        pass
    
    @abstractmethod
    def get_settings(self) -> Dict:
        """
        Get the settings for this data source.
        
        Returns:
            Dict: A dictionary containing the data source settings
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> str:
        """
        Get the schema information for this data source.
        
        Returns:
            str: The schema information as a formatted string
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict:
        """
        Get the capabilities information for the orchestrator prompt builder.
        
        Returns:
            Dict: A dictionary containing capability definitions
        """
        pass
    
    def validate_connection(self) -> bool:
        """
        Validate the connection to the data source.
        
        Returns:
            bool: True if the connection is valid, False otherwise
        """
        # Default implementation returns True
        # Subclasses can override this to implement actual validation
        return True 