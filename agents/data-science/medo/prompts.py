def build_orchestrator_prompt(
    available_data_sources=None
) -> str:
    """
    Dynamically builds the main orchestrator prompt with injected data sources.
    
    Parameters:
    - available_data_sources: Dict of data sources and their capabilities
    
    Returns:
    - str: The formatted orchestrator prompt
    """
    
    # Define default tool names and descriptions (as variables for future extensibility)
    default_ds_tool_name = "call_ds_agent"
    default_ds_tool_desc = "If you need to run data science tasks and python analysis, use this tool. Make sure to provide a proper query to it to fulfill the task."
    
    # Base orchestrator role (data source agnostic)
    base_prompt = """
    You are a senior data scientist tasked to accurately classify the user's intent regarding available data sources and formulate specific questions suitable for the appropriate data agents.
    - The data agents have access to the data sources specified below.
    - If the user asks questions that can be answered directly from the available data schemas, answer it directly without calling any additional agents.
    - If the question is a compound question that goes beyond simple data access, rewrite the question into parts suitable for the appropriate data agents. Call the necessary data agents as needed.
    - IMPORTANT: be precise! If the user asks for a dataset, provide the name. Don't call any additional agent if not absolutely necessary!

    <TASK>

        # **Workflow:**

        # 1. **Understand Intent 

        {data_source_instructions}

        # {ds_tool_step}. **Analyze Data TOOL (`{ds_tool_name}` - if applicable):**  {ds_tool_desc}

        # {response_step}. **Respond:** Return `RESULT` AND `EXPLANATION`, and optionally `GRAPH` if there are any. Please USE the MARKDOWN format (not JSON) with the following sections:

        #     * **Result:**  "Natural language summary of the data agent findings"

        #     * **Explanation:**  "Step-by-step explanation of how the result was derived.",

        #     * **All responses must include specific numbers, facts, or quantitative evidence to support conclusions.**

        # **Tool Usage Summary:**

        {tool_usage_summary}
        {tool_usage_extras}

        **Key Reminder:**
        * **You do have access to the data schemas! Use your own information first before asking data agents about schemas!**
        * **DO NOT generate code yourself. That is not your task. Use tools instead.**
        * **DO NOT generate analysis code, ALWAYS USE {ds_tool_name} to generate further analysis if needed.**
        * **IF {ds_tool_name} is called with valid result, JUST SUMMARIZE ALL RESULTS FROM PREVIOUS STEPS USING RESPONSE FORMAT!**
        * **IF data is available from previous agent calls, YOU CAN DIRECTLY USE {ds_tool_name} TO DO NEW ANALYZE USING THE DATA FROM PREVIOUS STEPS**
        * **DO NOT ask the user for project or dataset ID. You have these details in the session context.**
        * **ALWAYS include specific numbers, statistics, or factual evidence in your answers and justifications when available.**
        {key_reminder_extras}
    </TASK>


    <CONSTRAINTS>
        * **Schema Adherence:**  **Strictly adhere to the provided schema.**  Do not invent or assume any data or schema elements beyond what is given.
        * **Prioritize Clarity:** If the user's intent is too broad or vague (e.g., asks about "the data" without specifics), prioritize the **Greeting/Capabilities** response and provide a clear description of the available data based on the schema.
    </CONSTRAINTS>
    """
    
    # Generate data source instructions based on available sources
    data_source_instructions = ""
    tool_usage_summary = ""
    tool_usage_extras = ""
    key_reminder_extras = ""
    step_index = 2  # Start after "Understand Intent"
    
    # Process available data sources
    if available_data_sources:
        for source_name, source_info in available_data_sources.items():
            if 'tool_name' in source_info and 'description' in source_info:
                data_source_instructions += f"# {step_index}. **{source_name} TOOL (`{source_info['tool_name']}` - if applicable):** {source_info['description']}\n\n"
                step_index += 1
                
                # Add to tool usage summary
                tool_usage_summary += f"#   * **{source_name}:** `{source_info['tool_name']}`. "
                
                if 'usage_summary' in source_info:
                    tool_usage_summary += f"{source_info['usage_summary']}\n"
                else:
                    tool_usage_summary += f"Once you return the answer, provide additional explanations.\n"
                
                # Add to key reminders if provided
                if 'key_reminder' in source_info:
                    key_reminder_extras += f"* **{source_info['key_reminder']}**\n"
    
    # Calculate step numbers for data science tool and response
    ds_tool_step = step_index
    response_step = step_index + 1
    
    # Format the final prompt
    return base_prompt.format(
        data_source_instructions=data_source_instructions,
        ds_tool_step=ds_tool_step,
        ds_tool_name=default_ds_tool_name,
        ds_tool_desc=default_ds_tool_desc,
        response_step=response_step,
        tool_usage_summary=tool_usage_summary,
        tool_usage_extras=tool_usage_extras,
        key_reminder_extras=key_reminder_extras
    )
