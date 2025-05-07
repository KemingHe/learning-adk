# Multi-Data Source Scaling Approaches

## Introduction

This document outlines strategies for scaling the current Google ADK-based agent architecture to support multiple data sources. The current implementation uses a top-level agent with access to a BigQuery database agent and a data science agent. We aim to expand this design to accommodate multiple data sources (SQL databases like BigQuery/PostgreSQL and NoSQL document stores like Firestore/MongoDB) while maintaining clean architecture and adherence to ADK best practices.

## Key Terms and Concepts

Before diving into the approaches, let's clarify some key ADK terms and concepts:

- **Agent**: A unit that can process requests and produce responses, often using an LLM for reasoning
- **Sub-agent**: An agent that exists within the hierarchy of another (parent) agent
- **Tool**: A function that an agent can call to perform specific actions
- **AgentTool**: A special tool type that allows one agent to invoke another agent as a function
- **A2A Protocol**: Agent-to-Agent protocol, a standardized way for agents to communicate
- **Agent Card**: A metadata description of an agent's capabilities, used for discovery in A2A
- **Agent Engine**: Google's managed service for deploying and running agents at scale
- **Workflow Agents**: Specialized agents (SequentialAgent, ParallelAgent) that orchestrate other agents' execution
- **Session State**: Shared memory that agents can use to store and retrieve data during execution

## Approach 1: Simplified Adapter Pattern

### Concept

This approach extends the current architecture by introducing a lightweight "Data Source Adapter" layer. Instead of directly modifying the top-level agent structure, we create a configurable adapter that routes data requests to the appropriate data source agent.

### Implementation

1. Create a new `data_source_adapter` tool in the root agent that acts as a router
2. Implement specialized data source agents for each database type (BigQuery, PostgreSQL, Firestore, MongoDB)
3. Configure the adapter with a simple mapping of data source types to agent handlers
4. Update the root agent's state initialization to include configuration for multiple data sources

```python
# Conceptual implementation (not actual code)
async def data_source_adapter(
    question: str,
    source_name: str,  # e.g., "bigquery", "firestore"
    tool_context: ToolContext,
):
    """Tool to route to appropriate data source agent based on source_name."""
    
    # Get the appropriate agent based on source_name
    agent_map = {
        "bigquery": db_agent,
        "postgresql": pg_agent,
        "firestore": firestore_agent,
        "mongodb": mongo_agent,
    }
    
    if source_name not in agent_map:
        return f"Error: Unknown data source '{source_name}'"
    
    target_agent = agent_map[source_name]
    agent_tool = AgentTool(agent=target_agent)
    
    # Call the appropriate agent
    result = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    
    # Store result in state for potential further processing
    tool_context.state[f"{source_name}_result"] = result
    return result
```

### Pros

- Minimal changes to the existing architecture
- Simple to understand and implement
- Follows KISS principle while remaining flexible
- Root agent's interface stays essentially the same
- Easy to add new data sources by updating the agent map

### Cons

- Not as scalable for very large numbers of data sources
- All data source agents run in the same process/environment
- Limited ability to distribute load across multiple machines
- Configuration is more static and requires code changes

### Justification

This approach is ideal for teams just beginning to scale beyond a single data source who want to minimize architectural complexity. It follows the adapter pattern, which provides a clean abstraction layer between the root agent and specific data source implementations. By centralizing the routing logic, we maintain a single point of control while enabling the flexibility to work with multiple data sources.

## Approach 2: Distributed A2A Network

### Concept

This approach leverages Google's Agent-to-Agent (A2A) protocol to create a fully distributed network of specialized data source agents. Each data source agent becomes an independent service with its own endpoint, allowing for true horizontal scaling across different machines and environments.

### Implementation

1. Convert each data source agent into a standalone A2A-compatible service
2. Implement a "Data Hub" agent that uses A2A client capabilities to discover and communicate with data source agents
3. Use Agent Cards for dynamic discovery of available data sources and their capabilities
4. Deploy specialized data source agents to Agent Engine for managed scaling

```text
                       ┌───────────────┐
                       │               │
                       │    Data Hub   │
                       │     Agent     │
                       │   (A2A Client)│
                       │               │
                       └───────┬───────┘
                               │
                               ▼
           ┌─────────────┬─────────────┬─────────────┐
           │             │             │             │
┌──────────▼─────┐ ┌─────▼───────┐ ┌───▼─────────┐ ┌─▼──────────────┐
│  BigQuery Agent │ │PostgreSQL  │ │ Firestore   │ │ MongoDB Agent  │
│  A2A Service    │ │Agent       │ │ Agent       │ │ A2A Service    │
│                 │ │A2A Service │ │ A2A Service │ │                │
└─────────────────┘ └─────────────┘ └─────────────┘ └────────────────┘
```

### Pros

- Highly scalable architecture capable of handling many data sources
- True separation of concerns with independent service deployment
- Data source agents can be developed, deployed, and scaled independently
- Load balancing and fault tolerance can be implemented at the service level
- New data sources can be added dynamically without modifying the Data Hub

### Cons

- More complex to implement and deploy
- Requires understanding of A2A protocol and Agent Engine deployment
- Network overhead for inter-agent communication
- More moving parts to monitor and maintain
- Potential complexity in managing authentication between services

### Justification

This approach is ideal for production environments that need to scale to many data sources or have high throughput requirements. By leveraging the A2A protocol, we gain a standardized communication mechanism that promotes loose coupling between components. The use of Agent Cards enables dynamic discovery, making the system more flexible and resilient.

Agent Engine provides managed scaling, monitoring, and deployment capabilities, reducing the operational burden of maintaining many agent services. This architecture aligns with microservice best practices while leveraging Google ADK's specific strengths in the A2A protocol.

## Approach 3: Modular Plugin Architecture

### Concept

This approach focuses on maintainability and flexibility through a plugin-based architecture. It introduces the concept of "Data Source Plugins" - encapsulated modules that contain all the logic needed to interact with a specific data source, which can be registered with the system at runtime.

### Implementation

1. Define a standard interface for data source plugins with clear dependency injection points
2. Create a plugin registry that manages available data sources
3. Implement specialized workflow agents to coordinate interactions between plugins
4. Use ADK's session state to share context between the root agent and plugins

```python
# Conceptual plugin interface (not actual code)
class DataSourcePlugin:
    """Interface for all data source plugins."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration."""
        self.config = config
        
    async def query(self, request: str, context: ToolContext) -> str:
        """Execute a query against this data source."""
        raise NotImplementedError()
        
    @property
    def source_type(self) -> str:
        """Return the type of this data source."""
        raise NotImplementedError()
        
    @property
    def capabilities(self) -> List[str]:
        """Return a list of capabilities this plugin supports."""
        raise NotImplementedError()


# Root agent would use a PluginRegistry
class PluginRegistry:
    """Manages data source plugins."""
    
    def __init__(self):
        self.plugins = {}
        
    def register(self, plugin: DataSourcePlugin):
        """Register a new plugin."""
        self.plugins[plugin.source_type] = plugin
        
    async def execute_query(self, source_type: str, query: str, context: ToolContext) -> str:
        """Execute a query on the specified data source."""
        if source_type not in self.plugins:
            return f"Error: Unknown data source '{source_type}'"
            
        return await self.plugins[source_type].query(query, context)
```

### Pros

- Highly modular design with clean separation of concerns
- Plugins can be developed, tested, and deployed independently
- New data sources can be added without modifying existing code
- Clear interfaces make the system more maintainable
- Dependency injection provides flexibility in implementation details
- Enables advanced features like capability-based routing

### Cons

- More initial design work compared to the adapter approach
- Requires careful interface design to ensure future compatibility
- May introduce some performance overhead due to abstraction layers
- Needs well-defined testing strategies for plugin integrations

### Justification

This approach is ideal for teams focused on long-term maintainability and flexibility. By creating a plugin architecture with clear interfaces, we enable better separation of concerns and make the system more adaptable to changing requirements.

The plugin design allows specialists in different database technologies to work independently, following their own development cycles. The registry pattern centralizes management while keeping implementations decoupled. Dependency injection enables easier testing and flexible configuration.

This approach strikes a balance between the simplicity of Approach 1 and the scalability of Approach 2, with a focus on code organization and maintainability principles that align with software engineering best practices and the ADK's component-based architecture.

## Recommendation

Based on your current stage of development and requirements:

1. Start with **Approach 1 (Simplified Adapter Pattern)** if you're just beginning to scale beyond a single data source and want to minimize complexity while learning the ADK patterns.

2. Plan to move toward **Approach 3 (Modular Plugin Architecture)** as your system matures and more developers join the project, to gain better maintainability and flexibility.

3. Consider **Approach 2 (Distributed A2A Network)** when your production needs require true horizontal scaling across multiple machines or when you need to integrate with other teams' agents that run in separate environments.

Each approach can evolve into the next as your requirements grow, allowing for incremental development rather than requiring a complete rewrite.
