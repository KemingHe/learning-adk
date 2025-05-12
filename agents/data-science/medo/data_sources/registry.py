"""
Registry for managing data source providers.
"""

from typing import Dict, List


class DataSourceRegistry:
    """
    Registry for managing data source providers.
    Handles registration, retrieval, and enumeration of data sources.
    """
    
    def __init__(self):
        """
        Initialize an empty registry.
        """
        self._sources = {}
    
    def register(self, source):
        """
        Register a data source provider.
        
        Args:
            source: A data source provider implementing the required interface
        """
        self._sources[source.get_name()] = source
    
    def unregister(self, name: str):
        """
        Unregister a data source provider.
        
        Args:
            name: The name of the data source to unregister
        """
        if name in self._sources:
            del self._sources[name]
    
    def get_source(self, name: str):
        """
        Get a specific data source by name.
        
        Args:
            name: The name of the data source to retrieve
            
        Returns:
            The data source provider or None if not found
        """
        return self._sources.get(name)
    
    def get_all_sources(self) -> Dict:
        """
        Get all registered data sources.
        
        Returns:
            Dict: A dictionary of all registered data sources
        """
        return self._sources
    
    def get_all_source_names(self) -> List[str]:
        """
        Get the names of all registered data sources.
        
        Returns:
            List[str]: A list of data source names
        """
        return list(self._sources.keys())
    
    def source_exists(self, name: str) -> bool:
        """
        Check if a data source exists in the registry.
        
        Args:
            name: The name of the data source to check
            
        Returns:
            bool: True if the data source exists, False otherwise
        """
        return name in self._sources
