---
lab:
    title: 'Develop a multi-agent solution'
    description: 'Learn to configure multiple agents to collaborate using the Semantic Kernel SDK'
---

# Develop a multi-agent solution

In this exercise, you'll create a project that orchestrates two AI agents using the Semantic Kernel SDK. The Incident Manager agent will analyze service log files for issues. If an issue is found, the Incident Manager will recommend a resolution action. The Devops Assistant agent will receive the recommendation from the Incident Manager and invoke the corrective function to perform the resolution. The Incident Manager agent will review the updated logs to make sure the resolution is successful. For this exercise, four sample log files are provided. The Devops Assistant agent code only updates the sample log files with some example log messages.

This exercise should take approximately **30** minutes to complete.

## Before you start

To complete this exercise, you'll need:

- [Visual Studio Code](https://code.visualstudio.com/Download?azure-portal=true) installed.
- [Python](https://www.python.org/downloads/?azure-portal=true) installed on your machine.
- An Azure subscription. If you don't already have one, you can [sign up for one](https://azure.microsoft.com/?azure-portal=true).

## Create an Azure AI Foundry project

Let's start by creating an Azure AI Foundry project.

1. In a web browser, open the [Azure AI Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that might open.

1. In the home page, select **+ Create project**.

1. In the **Create a project** wizard, enter a suitable project name (for example, `my-agent-project`).

1. If you don't have a hub yet created, you'll see the new hub name and can expand the section below to review the Azure resources that will be automatically created to support your project. If you are reusing a hub, skip the following step.

1. Select **Customize** and specify the following settings for your hub:

    - **Hub name**: *A unique name - for example `my-ai-hub`*

    - **Subscription**: *Your Azure subscription*

    - **Resource group**: *Create a new resource group with a unique name (for example, `my-ai-resources`), or select an existing one*

    - **Location**: Select **Help me choose** and then select **gpt-4** in the Location helper window and use the recommended region\*

    - **Connect an Azure OpenAI service**: *Create a new AI Services resource with an appropriate name (for example, `my-ai-services`) or use an existing one*

    - **Connect Azure AI Search**: Skip connecting

    > \* Model quotas are constrained at the tenant level by regional quotas. In the event of a quota limit being reached later in the exercise, there's a possibility you may need to create another project in a different region.

1. Select **Next** and review your configuration. Then select **Create** and wait for the process to complete.

### Prepare the application configuration

1. Open VS Code and **Clone** the `https://github.com/MicrosoftLearning/mslearn-ai-agents` repository.

1. Store the clone on a local drive, and open the folder after cloning.

1. In the VS Code Explorer (left pane), right-click on the **Labfiles/05-agent-orchestration/Python** folder and select **Open in Integrated Terminal**.

1. In the terminal, enter `pip install semantic-kernel==1.22.1` to install the project dependencies.

1. In the VS Code Explorer (left pane), open the **.env** Python configuration file.

1. In your web browser, navigate to the home page of the [Azure AI Foundry portal](https://ai.azure.com) at `https://ai.azure.com`

1. Under **Project details**, copy the **Project connection string**.

1. Use this string as the value for **PROJECT_CONNECTION** in the .env file.

1. In the Azure AI Foundry portal, select **Models + endpoints** in the side panel.

    You should see the details for a gpt model deployment.

1. Copy the deployment name and set it as the **MODEL_DEPLOYMENT** value in the .env file.

1. Save your changes.

## Create an AI agent

Now you're ready to create your agent! In this exercise, you'll build an Incident Manager agent that can analyze service log files, identify potential issues, and recommend resolution actions or escalate issues when necessary. Let's get started!

1. Navigate to the **agent_chat.py** file.

1. Add the following code to the `main()` method to create the kernel:

    ```python
    # Create a kernel with chat completion service
    kernel = Kernel()
    kernel.add_service(chat_completion_service)
    ```

1. Create settings to enable auto-function calling behavior with the following code:

    ```python
    # Configure the function choice behavior to auto invoke kernel functions
    settings = kernel.get_prompt_execution_settings_from_service_id(service_id="chat_completion")
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    ```

1. Create a chat completion agent with the following code:

    ```python
    # Create an agent to identify issues from log files and suggest fixes
    incident_agent = ChatCompletionAgent(
        kernel=kernel,
        arguments=KernelArguments(settings=settings),
        name=INCIDENT_MANAGER,
        description="An AI assistant that reads log files and recommends corrective actions.",
        instructions="""
    ```

1. Add the following instructions to the agent:

    ```python
        instructions="""
            Analyze the given log file or the response from the devops assistant.
            Recommend which one of the following actions should be taken:

            Restart service {service_name}
            Rollback transaction
            Redeploy resource {resource_name}
            Increase quota

            If there are no issues or if the issue has already been resolved, respond with "No action needed."
            If none of the options resolve the issue, respond with "Escalate issue."

            RULES:
            - Read the log file on every turn.
            - Prepend your response with this text: "INCIDENT_MANAGER > {logfilepath} | "
            - Only respond with the corrective action instructions.
            - Do not perform any of the actions yourself.
            """
    ```

    For this exercise, only a few resolution actions are explicitly defined.

1. Setup the agent chat with the following code:

    ```python
    # Create the history for the agent chat log
    history = ChatHistory()

    for filename in os.listdir("sample_logs"):
        # Append the current log file to the chat
        history.add_user_message(f"Log file: sample_logs/{filename}")
        
        # Invoke a response from the agent
        async for response in incident_agent.invoke(history=history):
            print(f"{response.content}")
    # End of chat
    ```

    This code will prompt the agent to analyze each log file and recommend a resolution.

1. Add code to close the Azure Open AI client connection:

    ```python
    # Close the client connection
    await chat_completion_service.client.close()
    ```

1. You can review your `main` method to check that it is similar to the following:

    ```python
    async def main():
        # Define agent names
        INCIDENT_MANAGER = "INCIDENT_MANAGER"
        DEVOPS_ASSISTANT = "DEVOPS_ASSISTANT"

        model = os.getenv("MODEL_DEPLOYMENT")

        # Create the project client
        project_client = AIProjectClient.from_connection_string(
                conn_str=os.getenv("PROJECT_CONNECTION"),
                credential=DefaultAzureCredential())
        
        # Get the connection proeprties of the Azure Open AI Service
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

        # Create a kernel with chat completion service
        kernel = Kernel()
        kernel.add_service(chat_completion_service)

        # Configure the function choice behavior to auto invoke kernel functions
        settings = kernel.get_prompt_execution_settings_from_service_id(service_id="chat_completion")
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Create an agent to identify issues from log files and suggest fixes
        incident_agent = ChatCompletionAgent(
            kernel=kernel,
            arguments=KernelArguments(settings=settings),
            name=INCIDENT_MANAGER,
            description="An AI assistant that reads log files and recommends corrective actions.",
            instructions="""
                Analyze the given log file or the response from the devops assistant.
                Recommend which one of the following actions should be taken:

                Restart service {service_name}
                Rollback transaction
                Redeploy resource {resource_name}
                Increase quota

                If there are no issues or if the issue has already been resolved, respond with "No action needed."
                If none of the options resolve the issue, respond with "Escalate issue."

                RULES:
                - Do not perform any corrective actions yourself.
                - Read the log file on every turn.
                - Prepend your response with this text: "INCIDENT_MANAGER > {logfilepath} | "
                - Only respond with the corrective action instructions.
                """
        )

        # Create the history for the agent chat log
        history = ChatHistory()

        for filename in os.listdir("sample_logs"):
            # Append the current log file to the chat
            history.add_user_message(f"Log file: sample_logs/{filename}")
            
            # Invoke a response from the agent
            async for response in incident_agent.invoke(history=history):
                print(f"{response.content}")
        # End of chat

        # Close the client connection
        await chat_completion_service.client.close()
    ```

    Before you can run the agent, you'll need to provide a plugin that will allow the agent to read and write to log files.

1. Navigate to the **log_file_plugin.py** file.

1. Add a function that can read files to the `log_file_plugin` class

    ```python
    @kernel_function(description="Accesses the given file path string and returns the file contents as a string")
    def read_log_file(self, filepath: str = "") -> str:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    ```

    Now you can import your plugin to the kernel.

1. Navigate to the **agent_chat.py** file

1. Locate the kernel setup code `kernel.add_service()` and add  a line to import the plugin:

    ```python
    # Create a kernel with chat completion service
    kernel = Kernel()
    kernel.add_service(chat_completion_service)
    # Add plugins to the kernel
    kernel.add_plugin(LogFilePlugin(), plugin_name="LogFilePlugin")
    ```

    Now you're ready to run the code and see what resolutions the agent recommends!

1. Run the **agent_chat.py** file and observe the results

    To run the file, you can right-click **agent_chat.py** and then click **Open in Integrated Terminal**. Then enter `python agent_chat.py` in the terminal.

    You should see some output similar to the following:

    ```output
    INCIDENT_MANAGER > sample_logs/log1.log | Restart service ServiceX
    INCIDENT_MANAGER > sample_logs/log2.log | Rollback transaction
    INCIDENT_MANAGER > sample_logs/log3.log | Increase quota
    INCIDENT_MANAGER > sample_logs/log4.log | Redeploy resource ResourceX
    ```

## Create an AI agent group chat

In this exercise, you'll introduce a second agent to the chat. This devops agent will take the resolution recommendation from the incident manager agent and invoke the necessary function to resolve the issue. Let's get started!

1. Navigate to the **agent_chat.py** file.

1. Remove the agent chat logic you created in the previous task:

    ```python
    # Create the history for the agent chat log
    history = ChatHistory()

    for filename in os.listdir("sample_logs"):
        # Append the current log file to the chat
        history.add_user_message(f"Log file: sample_logs/{filename}")
        
        # Invoke a response from the agent
        async for response in incident_agent.invoke(history=history):
            print(f"{response.content}")
    # End of chat
    ```

    For multi agent collaboration, you'll create a different object for the agent group chat. But first, let's setup the code for the second devops agent.

1. In the `main` method near the kernel setup code, add the devops plugin:
    
    ```python
    # Add plugins to the kernel
    kernel.add_plugin(LogFilePlugin(), plugin_name="LogFilePlugin")
    kernel.add_plugin(DevopsPlugin(), plugin_name="DevopsPlugin")
    ```

    This plugin will allow the agents to invoke functions to carry out the recommended resolutions.

1. Add a new line after the `incident_agent` object initialization.

1. On the new line, add the following code to create the devops agent:

    ```python
    devops_agent = ChatCompletionAgent(
        kernel=kernel,
        arguments=KernelArguments(settings=settings),
        name=DEVOPS_ASSISTANT,
        description="An AI assistant that invokes service functions.",
        instructions="""
            Read the instructions from the INCIDENT_MANAGER and apply the appropriate resolution function. 
            Return the response as "{function_response}"
            If the instructions indicate there are no issues or actions needed, 
            take no action and respond with "No action needed."

            RULES:
            - Use the instructions provided.
            - Do not read any log files yourself.
            - Prepend your response with this text: "DEVOPS_ASSISTANT > "
            """
    )
    ```

1. Add the following code to create the agent group chat:

    ```python
    # Create a history reducer object
    history_reducer = ChatHistoryTruncationReducer(target_count=3)

    # Create the agent group chat
    chat = AgentGroupChat(
        agents=[incident_agent, devops_agent],
        termination_strategy=KernelFunctionTerminationStrategy(
            agents=[incident_agent, devops_agent],
            kernel=kernel,
            history_variable_name="lastmessage",
            automatic_reset=True,
            history_reducer=history_reducer,
        ),
    )
    ```

    In this code, you create an agent group chat object with the incident manager and devops agents. You also define a termination strategy for the chat.

    Note that the automatic reset flag will automatically clear the chat when it ends. This way, the agent can continue analyzing the files without the chat history object using too many unnecessary tokens. 

    Now let's define a termination function that will let the AI know when to end the current chat thread.

1. Enter the following code above the agent group chat object to define the termination function:

    ```python
    # Define the chat termination function
    termination_keyword = "yes"
    termination_function = KernelFunctionFromPrompt(
        function_name="termination", 
        prompt=f"""
        Identify who the last message is from.
        If the last message is from {INCIDENT_MANAGER}, respond with no.
        If the last message is from {DEVOPS_ASSISTANT} determine whether there is no action needed.
        If no action is needed, respond with: {termination_keyword}.
        Otherwise, respond with: no
        
        Last message:
        {{{{$lastmessage}}}}
        """
    )
    ```

1. Add the termination flags to the termination strategy definition:

    ```python
    chat = AgentGroupChat(
        agents=[incident_agent, devops_agent],
        termination_strategy=KernelFunctionTerminationStrategy(
            agents=[incident_agent, devops_agent],
            kernel=kernel,
            history_variable_name="lastmessage",
            automatic_reset=True,
            history_reducer=history_reducer,
            function=termination_function,
            result_parser=lambda result: termination_keyword in str(result.value[0]).lower(),
        ),
    )
    ```
    Next, let's add a selection strategy so the AI can allow the two agents to take turns.

1. Add the selection strategy function to the agent group chat definition:

    ```python
        selection_strategy=KernelFunctionSelectionStrategy(
            initial_agent=incident_agent,
            kernel=kernel,
            history_variable_name="lastmessage",
            history_reducer=history_reducer,
        )
    ```

    Next you need to define a selection function for the kernel to run.

1. Add the following code above the agent group chat object:

    ```python
    # Define a selection function to determine which agent should take the next turn.
    selection_function = KernelFunctionFromPrompt(
        function_name="selection",
        prompt=f"""
        If the last message is from the user or the {DEVOPS_ASSISTANT}, choose the {INCIDENT_MANAGER}.
        If the last message is from the {INCIDENT_MANAGER} and NOT the user, then choose the {DEVOPS_ASSISTANT}.
        Respond with only the name, give no explanation. 

        Last message:
        {{{{$lastmessage}}}}
        """
    )
    ```

1. Now you can update the `KernelFunctionSelectionStrategy` definition:

    ```python
        selection_strategy=KernelFunctionSelectionStrategy(
            initial_agent=incident_agent,
            kernel=kernel,
            history_variable_name="lastmessage",
            history_reducer=history_reducer,
            function=selection_function,
            result_parser=lambda result: str(result.value[0]).strip() if result.value[0] is not None else DEVOPS_ASSISTANT,
        )
    ```

    Now you're ready to initiate the agent group chat!

1. Add the following code that invokes an agent chat for each log file:

    ```python
    for filename in os.listdir("sample_logs"):
        # Append the current log file to the chat
        logfile_msg = ChatMessageContent(role=AuthorRole.USER, content=f"USER > sample_logs/{filename}")
        await chat.add_chat_message(logfile_msg)
        print()

        try:
            # Invoke a response from the agents
            async for response in chat.invoke():
                if response is None or not response.name:
                    continue
                print(f"{response.content}")

        except Exception as e:
            print(f"Error during chat invocation: {e}")
    ```

    Now you're ready to run the code and watch the agents collaborate!

## Check your work

In this exercise, you'll run your code and verify that your agent collaboration is working as expected.

1. Review your `main` method to check that it is similar to the following:

    ```python
        # Create a kernel with chat completion service
        kernel = Kernel()
        kernel.add_service(chat_completion_service)
        kernel.add_plugin(LogFilePlugin(), plugin_name="LogFilePlugin")
        kernel.add_plugin(DevopsPlugin(), plugin_name="DevopsPlugin")

        # Configure the function choice behavior to auto invoke kernel functions
        settings = kernel.get_prompt_execution_settings_from_service_id(service_id="chat_completion")
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Create an agent to identify issues from log files and suggest fixes
        incident_agent = ChatCompletionAgent(
            kernel=kernel,
            arguments=KernelArguments(settings=settings),
            name=INCIDENT_MANAGER,
            description="An AI assistant that reads log files and recommends corrective actions.",
            instructions="""
                Analyze the given log file or the response from the devops assistant.
                Recommend which one of the following actions should be taken:

                Restart service {service_name}
                Rollback transaction
                Redeploy resource {resource_name}
                Increase quota

                If there are no issues or if the issue has already been resolved, respond with "No action needed."
                If none of the options resolve the issue, respond with "Escalate issue."

                RULES:
                - Do not perform any corrective actions yourself.
                - Read the log file on every turn.
                - Prepend your response with this text: "INCIDENT_MANAGER > {logfilepath} | "
                - Only respond with the corrective action instructions.
                """
        )

        devops_agent = ChatCompletionAgent(
            kernel=kernel,
            arguments=KernelArguments(settings=settings),
            name=DEVOPS_ASSISTANT,
            description="An AI assistant that invokes service functions.",
            instructions="""
                Read the instructions from the INCIDENT_MANAGER and apply the appropriate resolution function. 
                Return the response as "{function_response}"
                If the instructions indicate there are no issues or actions needed, 
                take no action and respond with "No action needed."

                RULES:
                - Use the instructions provided.
                - Do not read any log files yourself.
                - Prepend your response with this text: "DEVOPS_ASSISTANT > "
                """
        )

        # Define a selection function to determine which agent should take the next turn.
        selection_function = KernelFunctionFromPrompt(
            function_name="selection",
            prompt=f"""
            If the last message is from the user or the {DEVOPS_ASSISTANT}, choose the {INCIDENT_MANAGER}.
            If the last message is from the {INCIDENT_MANAGER} and NOT the user, then choose the {DEVOPS_ASSISTANT}.
            Respond with only the name, give no explanation. 

            Last message:
            {{{{$lastmessage}}}}
            """
        )

        # Define the chat termination function
        termination_keyword = "yes"
        termination_function = KernelFunctionFromPrompt(
            function_name="termination", 
            prompt=f"""
            Identify who the last message is from.
            If the last message is from {INCIDENT_MANAGER}, respond with no.
            If the last message is from {DEVOPS_ASSISTANT} determine whether there is no action needed.
            If no action is needed, respond with: {termination_keyword}.
            Otherwise, respond with: no
            
            Last message:
            {{{{$lastmessage}}}}
            """
        )

        # Create a history reducer object
        history_reducer = ChatHistoryTruncationReducer(target_count=3)

        def result_parser(result):
            if result.value[0] is not None:
                parsed_value = str(result.value[0]).strip()
                return parsed_value
            else:
                return DEVOPS_ASSISTANT
            
        def termination_parser(result):
            value_str = str(result.value[0]).lower()
            return termination_keyword in value_str

        # Create the agent group chat
        chat = AgentGroupChat(
            agents=[incident_agent, devops_agent],
            termination_strategy=KernelFunctionTerminationStrategy(
                agents=[incident_agent, devops_agent],
                function=termination_function,
                kernel=kernel,
                result_parser=termination_parser,
                history_variable_name="lastmessage",
                automatic_reset=True,
                history_reducer=history_reducer,
            ),
            selection_strategy=KernelFunctionSelectionStrategy(
                initial_agent=incident_agent,
                function=selection_function,
                kernel=kernel,
                result_parser=result_parser,
                history_variable_name="lastmessage",
                history_reducer=history_reducer,
            )
        )

        for filename in os.listdir("sample_logs"):
            # Append the current log file to the chat
            logfile_msg = ChatMessageContent(role=AuthorRole.USER, content=f"USER > sample_logs/{filename}")
            await chat.add_chat_message(logfile_msg)
            print()

            try:
                # Invoke a response from the agents
                async for response in chat.invoke():
                    if response is None or not response.name:
                        continue
                    print(f"{response.content}")
                    
            except Exception as e:
                print(f"Error during chat invocation: {e}")

        await chat_completion_service.client.close()
    ```

1. In the terminal, enter `python agent_chat.py`

    You should see some output similar to the following:

    ```output
    
    INCIDENT_MANAGER > sample_logs/log1.log | Restart service ServiceX
    DEVOPS_ASSISTANT > Service ServiceX restarted successfully.
    INCIDENT_MANAGER > sample_logs/log1.log | No action needed.
    DEVOPS_ASSISTANT > No action needed.

    INCIDENT_MANAGER > sample_logs/log2.log | Rollback transaction for transaction ID 987654.
    DEVOPS_ASSISTANT > Transaction rolled back successfully.
    INCIDENT_MANAGER > sample_logs/log2.log | No action needed.
    DEVOPS_ASSISTANT > No action needed.

    INCIDENT_MANAGER > sample_logs/log3.log | Increase quota.
    DEVOPS_ASSISTANT > Successfully increased quota.
    (continued)
    ```

1. Verify that the log files are updated with resolution operation messages from the DevopsAssistant.

    For example, log1.log should have the following log messages appended:

    ```log
    [2025-02-27 12:43:38] ALERT  DevopsAssistant: Multiple failures detected in ServiceX. Restarting service.
    [2025-02-27 12:43:38] INFO  ServiceX: Restart initiated.
    [2025-02-27 12:43:38] INFO  ServiceX: Service restarted successfully.
    ```

Now you've successfully created AI incident and devops agents that can automatically detect issues and apply resolutions. Great work!