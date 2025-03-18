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
    
    # Function Purpose:
    This function appends a standard disclaimer text to any email content.
    It's used as a tool by the AI agent to process emails before sending.
    
    # Parameters Explained:
    :param email (str): The email content provided by the AI agent.
                        This is the complete text of the email that needs a disclaimer.
    
    # Return Value:
    :return: The original email with the disclaimer added at the end.
    :rtype: str (a string containing the modified email)
    
    # How It Works:
    1. The function receives the email content as a string
    2. It concatenates (joins) the original email with the disclaimer
    3. It returns the complete email including the disclaimer
    
    # Usage in AI Context:
    When the AI needs to generate an email, it will call this function
    and pass the email content as an argument. The function returns the
    modified email which the agent can then present to the user.
    """
    # Define the disclaimer with newlines for spacing
    disclaimer = "\n\nThis is an automated email. Please do not reply."
    
    # Concatenate the original email with the disclaimer and return
    return email + disclaimer

# Register our Python function as a tool that the AI can use
functions = FunctionTool({add_disclaimer})

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
    
    print("Project client created.")

    # Create an agent with the function tool
    agent = project_client.agents.create_agent(
        model=os.getenv("MODEL_DEPLOYMENT"),
        name="my-assistant",
        instructions="You are a helpful support agent. You can answer any question. However, if the user asks for an email to a customer - and ONLY for a customer, use the add_disclaimer function and pass it the email, return the information from the function.",
        tools=functions.definitions,
    )
    print(f"Created agent, agent ID: {agent.id}")

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    return project_client, thread, agent

# Initialize the agent client
project_client, thread, agent = initialize_client()


while True:
    # Clear the terminal for better readability
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Get prompt from the user and send the prompt to the agent
    print("To trigger the function, ask the agent to send an email to a customer.")
    print ("You can also ask any other question.\n")
    user_prompt = input("Enter the prompt (or type 'quit' to exit): ")
    if user_prompt == "quit":
        break
    if len(user_prompt) == 0:
        print("Please enter a prompt.")
        continue

    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=user_prompt
    )

    # Run the agent
    run = project_client.agents.create_run(thread_id=thread.id, agent_id=agent.id)

    # Monitor and process the run status, and handle the function calls
    
    # This loop keeps checking the agent's status until the interaction is complete
    while run.status in ["queued", "in_progress", "requires_action"]:
        # Sleep briefly to prevent excessive API calls
        time.sleep(1)
        
        # Get the latest status of the run - this polls the agent to see what state it's in
        run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

        # If the agent needs to execute a tool/function, we need to handle that request
        # "requires_action" means the AI needs us to run a function and give it the results
        if run.status == "requires_action" and run.required_action.type == "submit_tool_outputs":

            # Extract the list of tool calls the AI wants us to perform
            # A single response might require multiple function calls
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []  # We'll collect all function results here
            
            # Process each function call request from the AI
            for tool_call in tool_calls:
                # Get the name of the function to call and its arguments
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Executing function to add disclaimer.")
                
                # Execute the requested function with its arguments
                # In this case we only have one function, but you could have multiple
                if function_name == "add_disclaimer":
                    email = function_args.get("email")
                    output = add_disclaimer(email)
                    
                    # Store both the function result and which function call it belongs to
                    # The tool_call_id links the result back to the specific request
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": output
                    })
            
            # Send all the function results back to the AI agent so it can continue
            run = project_client.agents.submit_tool_outputs_to_run(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        
        # Exit the loop if the run is no longer active
        # This happens when processing is complete or failed
        if run.status not in ["queued", "in_progress", "requires_action"]:
            break

    # Check if the run failed and print the error message
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Get messages from the assistant thread
    messages = project_client.agents.list_messages(thread_id=thread.id)

    # Get the last message from the assistant
    last_msg = messages.get_last_text_message_by_role("assistant")
    if last_msg:
        print(f"\nAgent response: {last_msg.text.value}\n")

    # Give the user a chance to see the output before continuing
    input("Press Enter to continue...")

# Delete the agent once done
project_client.agents.delete_agent(agent.id)
print("Deleted agent")