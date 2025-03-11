import logging
import os
import json
import time
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the function and toolset
def add_disclaimer(email: str) -> str:
    """
    Adds a disclaimer to the email content.
    :param email (str): The email content.
    :return: Email content with disclaimer.
    :rtype: str
    """
    disclaimer = "\n\nThis is an automated email. Please do not reply."
    return email + disclaimer

# Add the disclaimer function to the toolset
functions = FunctionTool({add_disclaimer})

# Function to initialize the Azure Project Client
def initialize_client():
    # Ensure environment variables are loaded
    project_conn_str = os.getenv("PROJECT_CONNECTION_STRING")
    
    if not project_conn_str:
        raise ValueError("Environment variable PROJECT_CONNECTION_STRING must be set")
        
    # Create a project client using the connection string
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True),
        conn_str=project_conn_str
    )
    print("Project client created:")

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create an agent with the function tool
    agent = project_client.agents.create_agent(
        model=os.getenv("MODEL_DEPLOYMENT"),
        name="my-assistant",
        instructions="You are a helpful support agent. If the user asks for an email to a customer, use the add_disclaimer function and pass it the email, return the information from the function.",
        tools=functions.definitions,
    )
    print(f"Created agent, agent ID: {agent.id}")

    return project_client, thread, agent

# Initialize the agent client
project_client, thread, agent = initialize_client()

# Get prompt from the user and send the prompt to the agent
user_prompt = input("Enter your prompt: (default: 'Write an email to a customer'): ")
if not user_prompt:
    user_prompt = "Write an email to a customer that their order shipped."

print(f"User Prompt: {user_prompt}")

message = project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content=user_prompt
)
print(f"Created message, message ID: {message.id}")

# Run the agent
run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

# Monitor and process the run status, and handle the function calls
while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

    # Handle required actions (function calls)
    if run.status == "requires_action" and run.required_action.type == "submit_tool_outputs":
        print("Tool execution required")
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        
        # Process each tool call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"Executing function: {function_name}.")
            
            # Execute the appropriate function
            if function_name == "add_disclaimer":
                email = function_args.get("email")
                output = add_disclaimer(email)
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output
                })
        
        # Submit the outputs back to the agent
        print(f"Submitting tool outputs: {tool_outputs}")
        run = project_client.agents.submit_tool_outputs_to_run(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    
    if run.status not in ["queued", "in_progress", "requires_action"]:
        break

# Print the final status of the run
print(f"Run finished with status: {run.status}")

# Check if the run failed and print the error message
if run.status == "failed":
    print(f"Run failed: {run.last_error}")

# Get messages from the assistant thread
messages = project_client.agents.list_messages(thread_id=thread.id)

# Get the last message from the assistant
last_msg = messages.get_last_text_message_by_role("assistant")
if last_msg:
    print(f"Last Message: {last_msg.text.value}")

# Delete the agent once done
project_client.agents.delete_agent(agent.id)
print("Deleted agent")