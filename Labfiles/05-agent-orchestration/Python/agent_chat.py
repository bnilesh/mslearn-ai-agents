import asyncio
import os

from azure.ai.inference.aio import ChatCompletionsClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.core.credentials import AzureKeyCredential

from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies.selection.kernel_function_selection_strategy import KernelFunctionSelectionStrategy
from semantic_kernel.agents.strategies.termination.kernel_function_termination_strategy import KernelFunctionTerminationStrategy
from semantic_kernel.connectors.ai.azure_ai_inference import AzureAIInferenceChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions.kernel_function_from_prompt import KernelFunctionFromPrompt

from devops_plugin import DevopsPlugin
from log_file_plugin import LogFilePlugin

async def main():
    # Define agent names
    INCIDENT_MANAGER = "INCIDENT_MANAGER"
    DEVOPS_ASSISTANT = "DEVOPS_ASSISTANT"

    model = os.getenv("MODEL_DEPLOYMENT")
    
    # Create the project client
    project_client = AIProjectClient.from_connection_string(
            conn_str=os.getenv("PROJECT_CONNECTION"),
            credential=DefaultAzureCredential())
    
    # Get the connection properties of the Azure Open AI Service
    connection = project_client.connections.get_default(
        connection_type=ConnectionType.AZURE_OPEN_AI,
        include_credentials=True
    )
    
    # Use the connection information to get the endpoint for the service
    client_endpoint = f"{str(connection.endpoint_url).strip('/')}/openai/deployments/{model}"
    
    # Create the chat completion service with the connection key and service endpoint
    chat_completion_service = AzureAIInferenceChatCompletion(
        ai_model_id=model,
        client=ChatCompletionsClient(
            endpoint=client_endpoint,
            credential=AzureKeyCredential(key=connection.key),
        ),
        service_id="chat_completion"
    )

    # Begin your code here
    

if __name__ == "__main__":
    asyncio.run(main())