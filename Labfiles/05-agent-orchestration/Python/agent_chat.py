import asyncio
import os

from semantic_kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.agents.open_ai import AzureAssistantAgent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (AzureChatPromptExecutionSettings,)
from semantic_kernel.agents.strategies.selection.kernel_function_selection_strategy import (KernelFunctionSelectionStrategy,)
from semantic_kernel.agents.strategies.termination.kernel_function_termination_strategy import (KernelFunctionTerminationStrategy,)
from log_file_plugin import log_file_plugin
from devops_plugin import devops_plugin

async def main():
    print("Remove this")

if __name__ == "__main__":
    asyncio.run(main())