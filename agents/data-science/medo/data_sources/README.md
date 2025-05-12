# Data Sources Module

## Overview

The Data Sources module provides a flexible plugin architecture for connecting to different data storage systems. It uses dependency injection to support multiple data sources without modifying core agent code.

## Design Pattern

1. **Provider Interface**: All data sources implement a common interface (`DataSourceProvider`)
2. **Registry**: Central manager for data source registration and retrieval
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

Manager for available data sources:

```python
registry = DataSourceRegistry()
registry.register(source)    # Add a source
registry.get_source(name)    # Retrieve a source
registry.get_all_sources()   # Get all sources
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

### Using in Agent Code

```python
source = registry.get_source("BigQuery")
schema = source.get_schema()
capabilities = source.get_capabilities()
```

## Best Practices

- Each source should handle one data store type
- Follow the interface contract exactly
- Document source-specific requirements
