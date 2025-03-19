---
lab:
    title: 'Implement custom tools in an AI agent'
    description: 'Learn how define callback functions as function tools to add capabilities to your agents.'
---

# Implement custom tools in an AI agent

In this exercise you will explore creating an agent with a function call.

Tasks performed in this exercise:

- Create an Azure AI Foundry project and deploy a model
- Develop an agent that uses function tools
- Clean up resources

This exercise should take approximately **30** minutes to complete.

## Before you start

To complete this exercise, you'll need:

- An Azure subscription. If you don't already have one, you can [sign up for one](https://azure.microsoft.com/).

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

1. Wait for the deployment provisioning state to be **Completed**.

## Develop an agent that uses function tools

Now that you've created your project in AI Foundry, let's develop an app that implements an agent using custom function tools.

### Clone the repo containing the starter code

1. Open a new browser tab (keeping the Azure AI Foundry portal open in the existing tab). Then in the new tab, browse to the [Azure portal](https://portal.azure.com) at `https://portal.azure.com`; signing in with your Azure credentials if prompted.
1. Use the **[\>_]** button to the right of the search bar at the top of the page to create a new Cloud Shell in the Azure portal, selecting a ***PowerShell*** environment. The cloud shell provides a command line interface in a pane at the bottom of the Azure portal.

    > **Note**: If you have previously created a cloud shell that uses a *Bash* environment, switch it to ***PowerShell***.

1. In the cloud shell toolbar, in the **Settings** menu, select **Go to Classic version** (this is required to use the code editor).
1. In the PowerShell pane, enter the following commands to clone the GitHub repo containing the code files for this exercise:

    ```
   rm -r ai-agents -f
   git clone https://github.com/MicrosoftLearning/mslearn-ai-agents ai-agents
    ```

    > **Tip**: As you enter commands into the cloudshell, the ouput may take up a large amount of the screen buffer and the cursor on the current line may be obscured. You can clear the screen by entering the `cls` command to make it easier to focus on each task.

1. Enter the following command to change the working directory to the folder containing the code files and list them all.

    ```
   cd ai-agents/Labfiles/03-enhance-ai-agent/Python
   ls -a -l
    ```

    The provided files include application code and a file for configuration settings.

### Configure the application settings

1. In the cloud shell command line pane, enter the following command to install the libraries you'll use:

    ```
   pip install python-dotenv azure-identity azure-ai-projects==1.0.0b7
    ```

    >**Note:** You can ignore any warning or error messages displayed during the library installation.

1. Enter the following command to edit the configuration file that has been provided:

    ```
   code .env
    ```

    The file is opened in a code editor.

1. In the code file, replace the **your_project_connection_string** placeholder with the connection string for your project (copied from the project **Overview** page in the Azure AI Foundry portal), and the **your_model_deployment** placeholder with the name you assigned to your gpt-4 model deployment.
1. After you've replaced the placeholders, use the **CTRL+S** command to save your changes and then use the **CTRL+Q** command to close the code editor while keeping the cloud shell command line open.

### Write code to connect to your project and chat with your model

Now that you've configured the app, you'll add the necessary code to build an agent that uses a custom function. 

1. Enter the following command to begin editing the code.

    ```
    code agent-tool-starter.py
    ```

1. Add the following code in the **Define the function and toolset** section. This code defines a function and adds it to the toolset.

    > **Tip**: As you add code, be sure to maintain the correct indentation.


    ```python
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
    ```

1. Review the code you just entered. The comments explain how the function interacts with the agent.

Now that the *FunctionTool* is defined, you need to add code to monitor the agent run status and handle the function calls.

1. Add the following code in the **Monitor and process the run status, and handle the function calls** section to monitor the agent and invoke the *FunctionTool* when needed.

    > **Tip**: As you add code, be sure to maintain the correct indentation.

    ```python
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
    ```

1. Review the code you just entered. The comments explain how the code monitors the call to the agent, and how the function responds to the agent.

1. Use the **CTRL+S** command to save the changes, and then **CTRL+Q** to exit the editor.

### Sign into Azure and run the app

Now that the code is complete, it's time to run the application.

1. In the cloud shell command line pane, enter the following command to sign into Azure.

    ```
    az login
    ```

    **<font color="red">You must sign into Azure - even though the cloud shell session is already authenticated.</font>**    

1. When prompted, follow the instructions to open the sign-in page in a new tab and enter the authentication code provided and your Azure credentials. Then complete the sign in process in the command line, selecting the subscription containing your Azure AI Foundry hub if prompted.

1. After you have signed in, enter the following command to run the application:

    ```
    python agent-tool-starter.py
    ```

1. When you are asked to enter a prompt, press **Enter** to accept the default prompt which will trigger the function. You should see output similar to the following example.

    ```
    Last Message: Here is the final version of the email with the added disclaimer:
    
    "Dear Customer,
    
    We are pleased to inform you that your order has been shipped. You can expect to receive it 
    within the customary shipping time. We appreciate your patience and your business.
    
    Best,
    [Your Company]
    
    This is an automated email. Please do not reply."
    ```

## Clean up

Now that you've finished the exercise, you should delete the cloud resources you've created to avoid unnecessary resource usage.

1. Open the [Azure portal](https://portal.azure.com) at `https://portal.azure.com` and view the contents of the resource group where you deployed the hub resources used in this exercise.
1. On the toolbar, select **Delete resource group**.
1. Enter the resource group name and confirm that you want to delete it.