# Complete Guide to Output and Logging in Google ADK

Based on my research, there are several ways to display output and provide feedback in Google ADK applications. Here's a comprehensive guide on how to properly handle output in your ADK applications:

## 1. Print to Console vs UI Output

### Console Output

When you use `print()` statements in your ADK tools, they appear in the terminal/console where you launched the application, not in the web UI. This is useful for debugging but not visible to end users.

```python
def my_tool(parameter: str) -> dict:
    print("Debug: Processing parameter", parameter)  # Only visible in terminal
    return {"status": "success", "result": "Processed data"}
```

### Return Values for UI Output

The primary way to output content to the user interface is through the tool's return values or agent responses:

```python
def my_tool(parameter: str) -> dict:
    # Process data
    return {
        "status": "success",
        "message": "This will be visible to the user in the UI",
        "data": processed_data
    }
```

## 2. Logging Options

### Python's Standard Logging

For more structured console output, use Python's built-in logging module instead of print:

```python
import logging

# Configure logging at the start of your application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def my_tool(parameter: str) -> dict:
    logging.info(f"Processing parameter: {parameter}")
    logging.debug("Debug details here")  # Only shown if level is DEBUG
    
    if some_error_condition:
        logging.error("Something went wrong")
        
    return {"status": "success", "result": "Processed data"}
```

### Structured Logging for Tools

For more comprehensive debugging, log the input/output of your tools:

```python
import logging

def my_tool(parameter: str, tool_context) -> dict:
    logging.info(f"Tool called with: {parameter}")
    
    # Log to state for potential review
    tool_invocations = tool_context.state.get("tool_invocation_log", [])
    tool_invocations.append({
        "tool": "my_tool",
        "input": parameter,
        "timestamp": time.time()
    })
    tool_context.state["tool_invocation_log"] = tool_invocations
    
    result = {"status": "success", "result": "Processed data"}
    logging.info(f"Tool returning: {result}")
    return result
```

## 3. User Interface Feedback

### Direct UI Responses

For direct communication to the user through the UI, return clear, formatted messages from your agent or tools:

```python
def process_data(input_data: str) -> dict:
    # Process the data
    return {
        "status": "success",
        "user_message": "Your data has been processed successfully!",
        "details": "Here are the results: ..."
    }
```

### Streaming Output for Real-time Feedback

For operations that take time, you can use ADK's streaming capability to provide real-time updates:

```python
# In a FastAPI web application using ADK Streaming
async def agent_to_client_messaging(websocket, live_events):
    """Agent to client communication"""
    while True:
        async for event in live_events:
            # Get the text from the event
            text = event.content and event.content.parts and event.content.parts[0].text
            if text:
                # Send the text to the client through WebSocket
                await websocket.send_text(json.dumps({"message": text}))
```

## 4. State Updates for Persistent Information

Use session state to maintain information across interactions:

```python
def track_progress(step: str, tool_context) -> dict:
    # Update progress in state
    progress = tool_context.state.get("progress_tracker", [])
    progress.append({
        "step": step,
        "completed_at": time.time()
    })
    tool_context.state["progress_tracker"] = progress
    
    # Return visible feedback
    return {
        "status": "success",
        "message": f"Completed step: {step}"
    }
```

## 5. Best Practices

1. **Separate Logging Types**:
   - Use logging for developer information
   - Use return values for user-visible responses
   - Use state for persistent data

2. **Structured Output**:
   - Always include a "status" field ("success" or "error")
   - Provide descriptive error messages when things go wrong
   - Format complex data for readability

3. **Progressive Disclosure**:
   - For complex operations, show high-level progress first
   - Provide mechanisms to get more details if needed

4. **Error Handling**:
   - Log detailed error information to console
   - Return user-friendly error messages to the UI
   - Include recovery options when possible

5. **Internationalization**:
   - Consider storing user messages as templates
   - Apply localization as needed before display

## 6. Implementation Example

Here's a complete example of a tool with comprehensive logging and feedback:

```python
import logging
import time
from google.adk.tools import ToolContext

def analyze_data(data_source: str, analysis_type: str, tool_context: ToolContext) -> dict:
    """Analyzes data from the specified source.
    
    Args:
        data_source: The source of the data to analyze.
        analysis_type: The type of analysis to perform.
        tool_context: Provides access to session state.
        
    Returns:
        dict: Analysis results or error information.
    """
    # Console logging (for developers)
    logging.info(f"Starting analysis of {data_source} using {analysis_type}")
    
    try:
        # Track operation in state (persistent)
        operation_history = tool_context.state.get("analysis_operations", [])
        operation_id = f"analysis_{int(time.time())}"
        operation_history.append({
            "id": operation_id,
            "type": analysis_type,
            "source": data_source,
            "start_time": time.time(),
            "status": "in_progress"
        })
        tool_context.state["analysis_operations"] = operation_history
        
        # Simulate analysis
        # In a real tool, this would be your actual data processing
        time.sleep(1)  # Simulating work
        
        # Example success case
        if data_source != "invalid":
            # Update operation status
            for op in operation_history:
                if op["id"] == operation_id:
                    op["status"] = "completed"
                    op["end_time"] = time.time()
            tool_context.state["analysis_operations"] = operation_history
            
            # Return user-visible result (will appear in UI)
            return {
                "status": "success",
                "message": f"Successfully analyzed {data_source} data",
                "results": {
                    "type": analysis_type,
                    "summary": "This is a summary of the analysis results",
                    "findings": ["Finding 1", "Finding 2", "Finding 3"]
                }
            }
        else:
            # Example error case
            logging.error(f"Invalid data source: {data_source}")
            
            # Update operation status
            for op in operation_history:
                if op["id"] == operation_id:
                    op["status"] = "failed"
                    op["end_time"] = time.time()
                    op["error"] = "Invalid data source"
            tool_context.state["analysis_operations"] = operation_history
            
            # Return user-visible error (will appear in UI)
            return {
                "status": "error",
                "error_message": f"Unable to analyze data from '{data_source}'",
                "suggestions": ["Check that the data source exists", 
                               "Verify your access permissions",
                               "Try a different data source"]
            }
            
    except Exception as e:
        # Log the detailed error (for developers)
        logging.exception(f"Analysis failed: {str(e)}")
        
        # Return user-friendly error (for users)
        return {
            "status": "error",
            "error_message": "An unexpected error occurred during analysis",
            "support_id": operation_id  # Reference ID for support
        }
```

By following these patterns, you can create ADK applications that provide clear feedback to users while maintaining detailed logs for debugging and monitoring.
