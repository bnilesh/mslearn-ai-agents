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




# Function to initialize the Azure Project Client
def initialize_client():
    # Ensure environment variables are loaded
    project_conn_str = os.getenv("PROJECT_CONNECTION")
    
    if not project_conn_str:
        raise ValueError("Environment variable PROJECT_CONNECTION must be set")
        
    # Create a project client using the project connection string
    # Use DefaultAzureCredential to authenticate the client
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(
            exclude_environment_credential=True, 
            exclude_managed_identity_credential=True 
        ),
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