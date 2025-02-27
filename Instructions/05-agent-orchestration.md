---
lab:
    title: 'Agent Orchestration'
    description: 'Learn to configure mutliple agents to collaborate using the Semantic Kernel SDK'
---

# Agent Orchestration

In this exercise you'll .

This exercise should take approximately **30** minutes to complete.

## Before you start

To complete this exercise, you'll need:

- [Visual Studio Code](https://code.visualstudio.com/Download?azure-portal=true) installed.
- [Python](https://www.python.org/downloads/?azure-portal=true) installed on your machine.
- An Azure subscription. If you don't already have one, you can [sign up for one](https://azure.microsoft.com/?azure-portal=true).

## Create an Azure AI Foundry project

Let's start by creating an Azure AI Foundry project.

> [!NOTE] If you created an Azure AI Foundry project in the previous exercises, you may skip this task.

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

1. In your web browser, navigate to the home page of the [Azure AI Foundry portal](https://ai.azure.com) at `https://ai.azure.com`

1. On the home page, click **Let's go** under **Work outside of a project**

    This should navigate you to the the **Home** page for your Azure OpenAI Service.

1. Open VS Code and **Clone** the `https://github.com/MicrosoftLearning/mslearn-ai-agents` respository.

1. Store the clone on a local drive, and open the folder after cloning.

1. In the VS Code Explorer (left pane), right-click on the **Labfiles/05-agent-orchestration/Python** folder and select **Open in Integrated Terminal**.

1. In the VS Code Explorer (left pane), open the **.env** Python configuration file.

1. Set the **AZURE_OPENAI_API_KEY** value with the Azure OpenAI key for your project.

    You can copy this key from the **Home** page of your Azure OpenAI resource in the Azure AI Foundry portal. Either key 1 or key 2 will work. 

1. Set the **AZURE_OPENAI_ENDPOINT** value with **Azure OpenAI Service Endpoint** value copied from the **Home** page.

1. Set the **AZURE_OPENAI_CHAT_DEPLOYMENT_NAME** value with the name you assigned to your GPT-4 model deployment.

    You can find the name of your deployment on the **Deployments** page of the portal

1. Set the **AZURE_OPENAI_API_VERSION** value with the version of your deployment.

1. After you've set all of the values, save your changes.

## Create an AI agent

Now you're ready to create your agent! In this exercise, you'll build an incident manager agent that can analyze service log files, identify potential issues, and recommend resolution actions or escalate issues when necessary. Let's get started!

1. Navigate to the **agent_chat.py** file.

1. Add the following code to the `main()` method to create the kernel:

    ```python
        kernel = Kernel()
    ```

1. Create an Azure assistant agent with the following code:

    ```python
        incident_agent = await AzureAssistantAgent.create(
            kernel=kernel,
            name="INCIDENT_AGENT",
            description="An AI assistant that reads log files and recommends corrective actions.",
            instructions="""
            """
    ```

1. Add the following instructions to the agent:

    ```python
        instructions="""
            Read the given log file. Determine which one of the following actions should be taken:
            Restart service
            Rollback transaction
            Redeploy resource
            Increase quota
            No action needed
            Escalate issue
            Keep any resoning or explanations very brief.
            """
    ```

    For this exercise, only a few resolution actions are explicitly defined.

1. Setup a thread for the agent chat with the following code:

    ```python
        thread_id = await incident_agent.create_thread()

        try:
           
        finally:
            print("\nCleaning up resources...")
            if incident_agent is not None:
                await incident_agent.delete_thread(thread_id)
                await incident_agent.delete()
    ```

    This code creates the agent thread and cleans up resources on completion.

1. In the `try` block, add code to retrieve each of the log file names and add them to a chat message object:

    ```python
        try:
            for filename in os.listdir("sample_logs"):
                logfile_msg = ChatMessageContent(role=AuthorRole.USER, content="sample_logs/" + filename)
    ```

1.  Add the message to the assistant agent chat:

    ```python:
        await incident_agent.add_chat_message(
            thread_id=thread_id, 
            message=logfile_msg
        )
    ```

1. Invoke the agent thread and retrieve any responses with the following code:

    ```python
        async for response in incident_agent.invoke(thread_id=thread_id):
            print(incident_agent.name + ": " + response.content)
    ```

1. You can review your `main` method to check that it is similar to the following:

    ```python
    async def main():
        kernel = Kernel()

        incident_agent = await AzureAssistantAgent.create(
            kernel=kernel,
            name="INCIDENT_AGENT",
            description="An AI assistant that reads log files and recommends corrective actions.",
            instructions="""
                Read the given log file. Determine which one of the following actions should be taken:
                Restart service
                Rollback transaction
                Redeploy resource
                Increase quota
                No action needed
                Escalate issue
                Keep any resoning or explanations very brief.
                """
        )

        thread_id = await incident_agent.create_thread()

        try:
            for filename in os.listdir("sample_logs"):
                logfile_msg = ChatMessageContent(role=AuthorRole.USER, content="sample_logs/" + filename)
                await incident_agent.add_chat_message(
                    thread_id=thread_id, 
                    message=logfile_msg
                )

                async for response in incident_agent.invoke(thread_id=thread_id):
                    print(incident_agent.name + ": " + response.content)
        finally:
            print("\nCleaning up resources...")
            if incident_agent is not None:
                await incident_agent.delete_thread(thread_id)
                await incident_agent.delete()
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

1. Let's also add a function that can append messages to the log file:

    ```python
    @kernel_function(description="Appends a string to the given log file and saves it")
    def append_to_log_file(self, filepath: str, content: str) -> None:
        with open(filepath, 'a', encoding='utf-8') as file:
            file.write(content + '\n')
    ```

    Now you can import your plugin to the kernel.

1. Navigate to the **agent_chat.py** file

1. Locate the code that creates the kernel object and add code to import the plugin:

    ```python
    kernel = Kernel()
    kernel.add_plugin(log_file_plugin(), plugin_name="log_file_plugin")
    ```

    Now you're ready to run the code and see what resolutions the agent recommends!

1. Run the **agent_chat.py** file and observe the results

    To run the file, you can right-click **agent_chat.py** and then click **Open in Integrated Terminal**. Then enter `python agent_chat.py` in the terminal.

    You should see some output similar to the following:

    ```output
    INCIDENT_AGENT: Restart service
    INCIDENT_AGENT: Rollback transaction
    INCIDENT_AGENT: Increase quota
    INCIDENT_AGENT: Redeploy resource

    Cleaning up resources...
    ```

## Create an AI agent group chat

In this exercise, you'll introduce a second agent to the chat. This devops agent will take the resolution recommendation from the incident manager agent and invoke the necessary function to resolve the issue. Let's get started!

1. Navigate to the **agent_chat.py** file.

1. In the `main` method, add the devops plugin to the kernel:
    
    ```python
    kernel.add_plugin(devops_plugin(), plugin_name="devops_plugin")
    ```

    This plugin will allow the agents to invoke functions to carry out the recommended resolutions.

1. In the `main` method, create a new line above the `thread_id` object creation.

1. On the new line, add the following code to create the devops agent:

    ```python
    devops_agent = await AzureAssistantAgent.create(
        kernel=kernel,
        name="DEVOPS_AGENT",
        description="An AI assistant that invokes service functions.",
        instructions="""
            Analyze the resolution instructions from the incident manager.
            If there are no issues, do nothing.
            Otherwise, apply the appropriate resolution function.
            """
    )
    ```

1. Remove the code that creates tje agent thread:

    ```python
    # remove this code
    thread_id = await incident_agent.create_thread()
    ```

1. Add the following code to create the agent group chat:

    ```python
    chat = AgentGroupChat(
        agents=[incident_agent, devops_agent],
        termination_strategy=KernelFunctionTerminationStrategy(
            agents=[incident_agent],
            kernel=kernel,
            result_parser=lambda result: "No action needed" in str(result.value[0]).lower(),
            automatic_reset=True
        ),
    )
    ```

    In this code, you create an agent group chat object with the incident manager and devops agents. You also define a termination strategy for the chat.

    Note that the automatic reset flag will automatically clear the chat when it ends. This way, the agent can continue analyzing the files without the chat history object using too many unnecessary tokens. 

1. Now let's define a termination function that will let the AI know when to end the current chat thread.

    ```python
    TODO
    ```

1. Add the termination function flag to the agent group chat definition:

    ```python
    TODO
    ```

1. Remove the `try`-`finally` code block you added in the previous task.

1. Add the following code that invokes an agent chat for each log file:

    ```python
    for filename in os.listdir("sample_logs"):
        logfile_msg = ChatMessageContent(role=AuthorRole.USER, content="sample_logs/" + filename)
        await chat.add_chat_message(logfile_msg)

        try:
            async for response in chat.invoke():
                if response is None or not response.name:
                    continue
                print()
                print(f"# {response.name.upper()}:\n{response.content}")
        except Exception as e:
            print(f"Error during chat invocation: {e}")
    ```

    Now you're ready to run the code and watch the agents collaborate!

1. In the terminal, enter `python agent_chat.py`

    You should see some output similar to the following:

## Check your work

    TODO:

    Verify that the log files are updated with resolution operation messages from the DevopsManager.

Now you've successfully created AI incident and devops agents that can automatically detect issues and apply resolutions. Great work!