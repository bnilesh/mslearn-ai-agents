---
lab:
    title: 'Develop a multi-agent solution'
    description: 'Learn to configure multiple agents to collaborate using the Semantic Kernel SDK'
---

# Develop a multi-agent solution

In this exercise, you'll create a project that orchestrates two AI agents using the Semantic Kernel SDK. The Incident Manager agent will analyze service log files for issues. If an issue is found, the Incident Manager will recommend a resolution action. The Devops Assistant agent will receive the recommendation from the Incident Manager and invoke the corrective function to perform the resolution. The Incident Manager agent will review the updated logs to make sure the resolution is successful. For this exercise, four sample log files are provided. The Devops Assistant agent code only updates the sample log files with some example log messages.

This exercise should take approximately **30** minutes to complete.

## Create an Azure AI Foundry project

Let's start by creating an Azure AI Foundry project.

1. In a web browser, open the [Azure AI Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that are opened the first time you sign in, and if necessary use the **Azure AI Foundry** logo at the top left to navigate to the home page, which looks similar to the following image:

    ![Screenshot of Azure AI Foundry portal.](./Media/ai-foundry-home.png)

1. In the home page, select **+ Create project**.

1. In the **Create a project** wizard, enter a suitable project name for (for example, `my-ai-project`) and if an existing hub is suggested, choose the option to create a new one. Then review the Azure resources that will be automatically created to support your hub and project.

1. Select **Customize** and specify the following settings for your hub:

    - **Hub name**: *A unique name - for example `my-ai-hub`*
    - **Subscription**: *Your Azure subscription*
    - **Resource group**: *Create a new resource group with a unique name (for example, `my-ai-resources`), or select an existing one*
    - **Location**: Select a region from the following:\*
        - australiaeast
        - eastus
        - eastus2
        - francecentral
        - swedencentral
    - **Connect Azure AI Services or Azure OpenAI**: *Create a new AI Services resource with an appropriate name (for example, `my-ai-services`) or use an existing one*
    - **Connect Azure AI Search**: Skip connecting

    > \* Model quotas are constrained at the tenant level by regional quotas. In the event of a quota limit being reached later in the exercise, there's a possibility you may need to create another project in a different region.

1. Select **Next** and review your configuration. Then select **Create** and wait for the process to complete.

1. When your project is created, close any tips that are displayed and review the project page in Azure AI Foundry portal, which should look similar to the following image:

    ![Screenshot of a Azure AI project details in Azure AI Foundry portal.](./Media/ai-foundry-project.png)

1. In the project overview page, in the **Project details** area, note the **Project connection string**. Later, you'll use this connection string to connect to your project in a client application.

## Deploy a generative AI model

Now you're ready to deploy a generative AI language model to support your agent.

1. In the pane on the left for your project, in the **My assets** section, select the **Models + endpoints** page.

1. In the **Models + endpoints** page, in the **Model deployments** tab, in the **+ Deploy model** menu, select **Deploy base model**.

1. Search for the **gpt-4** model in the list, and then select and confirm it.

1. Deploy the model with the following settings by selecting **Customize** in the deployment details:

    - **Deployment name**: *A unique name for your model deployment - for example `gpt-4-model` (remember the name you choose - you'll need it later)*
    - **Deployment type**: Standard
    - **Model version**: 0613
    - **Connected AI resource**: *Select your Azure OpenAI resource connection*
    - **Tokens per Minute Rate Limit (thousands)**: 5K
    - **Content filter**: DefaultV2
    - **Enable dynamic quota**: Disabled
      
    > **Note**: Reducing the TPM helps avoid over-using the quota available in the subscription you are using. 5,000 TPM is sufficient for the data used in this exercise.

1. Wait for the deployment to complete.

## Create an AI Agent client app

Now you're ready to create a client app that defines an agent and a custom function. Some code is provided for you in a GitHub repository.

### Prepare the environment

1. Open a new browser tab (keeping the Azure AI Foundry portal open in the existing tab). Then in the new tab, browse to the [Azure portal](https://portal.azure.com) at `https://portal.azure.com`; signing in with your Azure credentials if prompted.
1. Use the **[\>_]** button to the right of the search bar at the top of the page to create a new Cloud Shell in the Azure portal, selecting a ***PowerShell*** environment. The cloud shell provides a command line interface in a pane at the bottom of the Azure portal.

    > **Note**: If you have previously created a cloud shell that uses a *Bash* environment, switch it to ***PowerShell***.

1. In the PowerShell pane, enter the following commands to clone the GitHub repo containing the code files for this exercise:

    ```
    rm -r ai-agents -f
    git clone https://github.com/MicrosoftLearning/mslearn-ai-agents ai-agents
    ```

    > **Tip**: As you enter commands into the cloud shell, the output may take up a large amount of the screen buffer and the cursor on the current line may be obscured. You can clear the screen by entering the `cls` command to make it easier to focus on each task.

1. Enter the following command to install the required version of Python in the cloud shell:

    ```
    sh ~/ai-agents/Labfiles/update-python.sh
    ```

1. After the installation is complete, in the cloud shell toolbar, in the **Settings** menu, select **Go to Classic version** (this starts a new session, and is required to use the code editor).

    **<font color="red">Ensure you've switched to the classic version of the cloud shell and a new session has started before continuing.</font>**

1. Enter the following command to change the working directory to the folder containing the code files and list them all.

    ```
    cd ai-agents/Labfiles/05-agent-orchestration/Python
    ls -a -l
    ```

    The provided files include application code and a file for configuration settings.

### Configure the application settings

1. In the cloud shell command line pane, enter the following command to install the libraries you'll use:

    ```
    pip install python-dotenv azure-identity semantic-kernel[azure] 
    ```

    > **Note**: Installing *semantic-kernel[azure]* automatically installs a semantic kernel-compatible version of *azure-ai-projects*.

1. Enter the following command to edit the configuration file that is provided:

    ```
    code .env
    ```

    The file is opened in a code editor.

1. In the code file, replace the **your_project_connection_string** placeholder with the connection string for your project (copied from the project **Overview** page in the Azure AI Foundry portal), and the **your_model_deployment** placeholder with the name you assigned to your gpt-4 model deployment.

1. After you've replaced the placeholders, use the **CTRL+S** command to save your changes and then use the **CTRL+Q** command to close the code editor while keeping the cloud shell command line open.

### Create AI agents

Now you're ready to create your agent! In this exercise, you'll build an Incident Manager agent that can analyze service log files, identify potential issues, and recommend resolution actions or escalate issues when necessary. You'll also create a devops agent will take the resolution recommendation from the incident manager agent and invoke the necessary function to resolve the issue. Let's get started!

1. Enter the following command to edit the **agent_chat.py** file:

    ```
    code agent_chat.py
    ```

1. Note the **INCIDENT_MANAGER_INSTRUCTIONS** string. These are the instructions you'll provide to your agent.

1. Add the following code under the comment **Create the incident manager agent on the Azure AI agent service**

    ```python
    # Create the incident manager agent on the Azure AI agent service
    incident_agent_definition = await client.agents.create_agent(
        model=ai_agent_settings.model_deployment_name,
        name=INCIDENT_MANAGER,
        instructions=INCIDENT_MANAGER_INSTRUCTIONS
    )
    ```

    This code creates the agent definition on your Azure AI Project client.

1. Add the following code under the comment **Create a Semantic Kernel agent for the Azure AI incident manager agent**

    ```python
    # Create a Semantic Kernel agent for the Azure AI incident manager agent
    agent_incident = AzureAIAgent(
        client=client,
        definition=incident_agent_definition,
        plugins=[LogFilePlugin()]
    )
    ```

    This code creates the Semantic Kernel agent with access to the **LogFilePlugin**. This plugin allows the agent to read the log file contents.

1. Take a moment to observe the **DEVOPS_ASSISTANT_INSTRUCTIONS** string. These are the instructions you'll provide to the new devops assistant agent.

1. Add the following code under the comment **Create the devops agent on the Azure AI agent service**
    
    ```python
    # Create the devops agent on the Azure AI agent service
    devops_agent_definition = await client.agents.create_agent(
        model=ai_agent_settings.model_deployment_name,
        name=DEVOPS_ASSISTANT,
        instructions=DEVOPS_ASSISTANT_INSTRUCTIONS,
    )
    ```

1. Add the following code under the comment **Create a Semantic Kernel agent for the devops Azure AI agent**
    
    ```python
    # Create a Semantic Kernel agent for the devops Azure AI agent
    agent_devops = AzureAIAgent(
        client=client,
        definition=devops_agent_definition,
        plugins=[DevopsPlugin()]
    )
    ```

    The **DevopsPlugin** allows the agent to perform mock devops tasks, such as restarting the service or rolling back a transaction.

### Define group chat strategies

In this task, you define approval and selection strategies that guide the AI agent collaboration. The **ApprovalTerminationStrategy** helps signal when the goal is complete. The **SelectionStrategy** identifies which agent should take the next turn. Once the strategies are in place, you can create and run your AI agent group chat. Let's get started!

1. Locate the **ApprovalTerminationStrategy** class located above the **main** method.

1. Add the following code under the comment **End the chat if the agent has indicated there is no action needed**:

    ```python
    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return "no action needed" in history[-1].content.lower()
    ```

    The kernel invokes this function after the agent's response to determine if the completion criteria is complete. In this case, the goal is met when the incident manager responds with "No action needed." This phrase is defined in the incident manager agent instructions.

1. Locate the **SelectionStrategy** class located above the **main** method.

1. Add the following code under the comment **Select the next agent that should take the next turn in the chat**:

    ```python
    async def select_agent(self, agents, history):
        """"Check which agent should take the next turn in the chat."""

        # The Incident Manager should go after the User or the Devops Assistant
        if (history[-1].name == DEVOPS_ASSISTANT or history[-1].role == AuthorRole.USER):
            agent_name = INCIDENT_MANAGER
            return next((agent for agent in agents if agent.name == agent_name), None)
        
        # Otherwise it is the Devops Assistant's turn
        return next((agent for agent in agents if agent.name == DEVOPS_ASSISTANT), None)
    ```

    This code runs on every turn to determine which agent should respond. Now you're ready to initiate the agent group chat!

1. In the main method, under the comment **Add the agents to a group chat with a custom termination and selection strategy** add the following code to create the group chat:

    ```python
    # Add the agents to a group chat with a custom termination and selection strategy
    chat = AgentGroupChat(
        agents=[agent_incident, agent_devops],
        termination_strategy=ApprovalTerminationStrategy(
            agents=[agent_incident], 
            maximum_iterations=10, 
            automatic_reset=True
        ),
        selection_strategy=SelectionStrategy(agents=[agent_incident,agent_devops]),      
    )
    ```

    In this code, you create an agent group chat object with the incident manager and devops agents. You also define the termination and selection strategies for the chat. Notice that the **ApprovalTerminationStrategy** is tied to the incident manager agent only, and not the devops agent. This makes it so the incident manager agent is responsible for signaling the end of the chat. The **SelectionStrategy** includes all agents that should take a turn in the chat.

    Note that the automatic reset flag will automatically clear the chat when it ends. This way, the agent can continue analyzing the files without the chat history object using too many unnecessary tokens. 

1. Add the following code under the comment **Append the current log file to the chat**:

    ```python
    # Append the current log file to the chat
    await chat.add_chat_message(logfile_msg)
    print()
    ```

1. Add the following code under the comment **Invoke a response from the agents**:

    ```python
    # Invoke a response from the agents
    async for response in chat.invoke():
        if response is None or not response.name:
            continue
        print(f"{response.content}")
    ```

1. Let's check that everything is as it should be. Review your **main** method to check that it is similar to the following:

    ```python
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    ai_agent_settings = AzureAIAgentSettings.create()

    async with (
        DefaultAzureCredential(
            exclude_environment_credential=True, 
            exclude_managed_identity_credential=True) as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
    
        # Create the incident manager agent on the Azure AI agent service
        incident_agent_definition = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=INCIDENT_MANAGER,
            instructions=INCIDENT_MANAGER_INSTRUCTIONS,

        )

        # Create a Semantic Kernel agent for the Azure AI incident manager agent
        agent_incident = AzureAIAgent(
            client=client,
            definition=incident_agent_definition,
            plugins=[LogFilePlugin()]
        )

        # Create the copy writer agent on the Azure AI agent service
        devops_agent_definition = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=DEVOPS_ASSISTANT,
            instructions=DEVOPS_ASSISTANT_INSTRUCTIONS,
        )

        # Create a Semantic Kernel agent for the devops Azure AI agent
        agent_devops = AzureAIAgent(
            client=client,
            definition=devops_agent_definition,
            plugins=[DevopsPlugin()]
        )

        # Add the agents to a group chat with a custom termination and selection strategy
        chat = AgentGroupChat(
            agents=[agent_incident, agent_devops],
            termination_strategy=ApprovalTerminationStrategy(agents=[agent_incident], maximum_iterations=10, automatic_reset=True),
            selection_strategy=SelectionStrategy(agents=[agent_incident,agent_devops]),      
        )

        for filename in os.listdir("sample_logs"):
            logfile_msg = ChatMessageContent(role=AuthorRole.USER, content=f"USER > sample_logs/{filename}")
            # Append the current log file to the chat
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

1. Use the **CTRL+S** command to save your changes to the code file and then use the **CTRL+Q** command to close the code editor while keeping the cloud shell command line open.

### Sign into Azure and run the app

Now you're ready to run your code and watch your AI agents collaborate.

1. In the cloud shell command line pane, enter the following command to sign into Azure.

    ```
    az login
    ```

    **<font color="red">You must sign into Azure - even though the cloud shell session is already authenticated.</font>**    

1. When prompted, follow the instructions to open the sign-in page in a new tab and enter the authentication code provided and your Azure credentials. Then complete the sign in process in the command line, selecting the subscription containing your Azure AI Foundry hub if prompted.

1. After you have signed in, enter the following command to run the application:

    ```
    python agent_chat.py
    ```

    You should see some output similar to the following:

    ```output
    
    INCIDENT_MANAGER > sample_logs/log1.log | Restart service ServiceX
    DEVOPS_ASSISTANT > Service ServiceX restarted successfully.
    INCIDENT_MANAGER > sample_logs/log1.log | No action needed.

    INCIDENT_MANAGER > sample_logs/log2.log | Rollback transaction for transaction ID 987654.
    DEVOPS_ASSISTANT > Transaction rolled back successfully.
    INCIDENT_MANAGER > sample_logs/log2.log | No action needed.

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

## Summary

In this exercise, you used the Semantic Kernel SDK to create AI incident and devops agents that can automatically detect issues and apply resolutions. Great work!

## Clean up

If you've finished exploring Azure AI Agent Service, you should delete the resources you have created in this exercise to avoid incurring unnecessary Azure costs.

1. Return to the browser tab containing the Azure portal (or re-open the [Azure portal](https://portal.azure.com) at `https://portal.azure.com` in a new browser tab) and view the contents of the resource group where you deployed the resources used in this exercise.

1. On the toolbar, select **Delete resource group**.

1. Enter the resource group name and confirm that you want to delete it.