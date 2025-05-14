"""
Registry for managing data source providers.
"""

from typing import Dict, List, Any, Optional

class DataSourceRegistry:
    """
    Registry for managing data source providers.
    Handles registration, retrieval, enumeration of data sources,
    and state management for data sources.
    """
    
    # State key constants
    ACTIVE_SOURCE_KEY = "active_data_source"
    ACTIVE_SOURCES_KEY = "active_data_sources"
    SOURCE_SETTINGS_PREFIX = "source_settings_"
    ALL_DB_SETTINGS_KEY = "all_db_settings"
    
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
        
    # State management methods
    
    def get_active_source(self, context) -> Optional[str]:
        """
        Get the currently active data source name.
        
        Args:
            context: The callback or tool context
            
        Returns:
            str: The name of the active data source or None if not set
        """
        return context.state.get(self.ACTIVE_SOURCE_KEY)
    
    def set_active_source(self, context, source_name: str) -> bool:
        """
        Set the active data source if it exists in the registry.
        
        Args:
            context: The callback or tool context
            source_name: Name of the data source to set as active
            
        Returns:
            bool: True if successful, False if the source doesn't exist
        """
        if self.source_exists(source_name):
            context.state[self.ACTIVE_SOURCE_KEY] = source_name
            return True
        return False
    
    def get_active_sources(self, context) -> List[str]:
        """
        Get all active data source names.
        
        Args:
            context: The callback or tool context
            
        Returns:
            List[str]: List of active data source names
        """
        return context.state.get(self.ACTIVE_SOURCES_KEY, [])
    
    def ensure_active_sources_initialized(self, context) -> None:
        """
        Initialize active data sources list if not already set.
        
        Args:
            context: The callback or tool context
        """
        if self.ACTIVE_SOURCES_KEY not in context.state:
            context.state[self.ACTIVE_SOURCES_KEY] = self.get_all_source_names()
            
    def add_active_source(self, context, source_name: str) -> bool:
        """
        Add a data source to the active sources list.
        
        Args:
            context: The callback or tool context
            source_name: Name of the data source to add
            
        Returns:
            bool: True if added, False if not found or already in list
        """
        if not self.source_exists(source_name):
            return False
            
        active_sources = self.get_active_sources(context)
        if source_name not in active_sources:
            active_sources.append(source_name)
            context.state[self.ACTIVE_SOURCES_KEY] = active_sources
            return True
        return False
    
    def remove_active_source(self, context, source_name: str) -> bool:
        """
        Remove a data source from the active sources list.
        
        Args:
            context: The callback or tool context
            source_name: Name of the data source to remove
            
        Returns:
            bool: True if removed, False if not in list
        """
        active_sources = self.get_active_sources(context)
        if source_name in active_sources:
            active_sources.remove(source_name)
            context.state[self.ACTIVE_SOURCES_KEY] = active_sources
            
            # If removing current active source, select a new one if available
            if self.get_active_source(context) == source_name:
                if active_sources:
                    context.state[self.ACTIVE_SOURCE_KEY] = active_sources[0]
                elif self.ACTIVE_SOURCE_KEY in context.state:
                    del context.state[self.ACTIVE_SOURCE_KEY]
            
            return True
        return False
    
    def get_source_settings(self, context, source_name: str = None) -> Dict:
        """
        Get settings for a specific data source.
        
        Args:
            context: The callback or tool context
            source_name: Name of the data source (uses active source if None)
            
        Returns:
            Dict: The data source settings
        """
        # Use provided source name, active source, or default to first available
        source_name = source_name or self.get_active_source(context)
        if not source_name and self.get_all_source_names():
            source_name = self.get_all_source_names()[0]
            
        if not source_name:
            return {}
            
        # Check if settings are already in state
        key = f"{self.SOURCE_SETTINGS_PREFIX}{source_name}"
        if key not in context.state:
            # Get and store settings from source
            source = self.get_source(source_name)
            if source:
                context.state[key] = source.get_settings()
            else:
                logging.warning(f"Data source '{source_name}' not found. Unable to retrieve settings.")
                
        return context.state.get(key, {})
    
    def get_all_db_settings(self, context) -> Dict:
        """
        Get the all_db_settings dictionary, initializing if needed.
        
        Args:
            context: The callback or tool context
            
        Returns:
            Dict: The all_db_settings dictionary
        """
        if self.ALL_DB_SETTINGS_KEY not in context.state:
            active_source = self.get_active_source(context)
            context.state[self.ALL_DB_SETTINGS_KEY] = {
                "use_database": active_source or "BigQuery"
            }
        return context.state[self.ALL_DB_SETTINGS_KEY]
