# Data Sources Module

## Overview

The Data Sources module provides a flexible plugin architecture for connecting to different data storage systems. It uses dependency injection to support multiple data sources without modifying core agent code.

## Design Pattern

1. **Provider Interface**: All data sources implement a common interface (`DataSourceProvider`)
2. **Registry**: Central manager for data source registration, retrieval, and state management
3. **Capability Exposure**: Sources self-document their available functionality

## Key Components

### DataSourceProvider (`base.py`)

Abstract interface all data sources must implement:

```python
def get_name() -> str        # Unique identifier
def get_settings() -> Dict   # Configuration parameters
def get_schema() -> str      # Data structure information
def get_capabilities() -> Dict # Available tools/functions
def validate_connection() -> bool # Connection testing
```

### DataSourceRegistry (`registry.py`)

Manager for available data sources with integrated state management:

```python
# Source registration and access
registry = DataSourceRegistry()
registry.register(source)    # Add a source
registry.get_source(name)    # Retrieve a source
registry.get_all_sources()   # Get all sources

# State management
registry.get_active_source(context)           # Get current active source
registry.set_active_source(context, "BigQuery") # Set active source
registry.get_source_settings(context, "BigQuery") # Get source settings
registry.ensure_active_sources_initialized(context) # Initialize active sources list
```

## Usage Examples

### Registering Existing Sources

```python
from medo.data_sources import DataSourceRegistry
from medo.data_sources.bq_source import BigQueryDataSource

registry = DataSourceRegistry()
registry.register(BigQueryDataSource())
```

### Creating a New Source

```python
from medo.data_sources.base import DataSourceProvider

class CSVDataSource(DataSourceProvider):
    def get_name(self): return "CSV"
    def get_settings(self): return {"path": "/data/files"}
    def get_schema(self): return "table1(col1, col2)"
    def get_capabilities(self): return {
        "Read CSV": {"tool_name": "read_csv", "description": "Reads CSV files"}
    }
    def validate_connection(self): return True

# Register the new source
registry.register(CSVDataSource())
```

### Using State Management

```python
# In setup_before_agent_call
registry.ensure_active_sources_initialized(callback_context)
if not registry.get_active_source(callback_context):
    registry.set_active_source(callback_context, "BigQuery")

settings = registry.get_source_settings(callback_context)

# In a tool
active_source = registry.get_active_source(tool_context)
settings = registry.get_source_settings(tool_context)
```

### Using Multiple Data Sources

```python
# Add sources to active list
registry.add_active_source(context, "BigQuery")
registry.add_active_source(context, "CSV")

# Get active sources
active_sources = registry.get_active_sources(context)

# Switch active source
registry.set_active_source(context, "CSV")

# Remove a source
registry.remove_active_source(context, "BigQuery")
```

## State Management Details

The registry provides these state management functions:

- **`get_active_source(context)`**: Get the currently selected data source
- **`set_active_source(context, name)`**: Set the current data source
- **`get_active_sources(context)`**: Get list of all active data sources
- **`add_active_source(context, name)`**: Add a source to the active list
- **`remove_active_source(context, name)`**: Remove a source from the active list
- **`get_source_settings(context, name)`**: Get settings for a source
- **`get_all_db_settings(context)`**: Get general database settings
- **`ensure_active_sources_initialized(context)`**: Initialize active sources list

All state is stored in a serializable format within the context.state dictionary.

## Best Practices

- Each source should handle one data store type
- Follow the interface contract exactly
- Use registry's state management for consistent state handling
- Only store serializable data in the context state
