---
lab:
    title: 'Implement custom tools in an AI agent'
    description: 'TODO.'
---

# Implement custom tools in an AI agent

In this exercise you will explore ....

Tasks performed in this exercise:

* Create an Azure AI Foundry project
* Create an Azure Function Apps resource
* Create a user-assigned managed identity 

This exercise should take approximately **30** minutes to complete.

## Before you start

To complete this exercise, you'll need:

* Azure Functions Core Tools. Version 4.0.6x, or greater, recommended.
    * Windows [v4.x - Windows 64-bit](https://go.microsoft.com/fwlink/?linkid=2174087)
    * For installation on other operating systems visit [Azure Functions Core Tools on GitHub](https://github.com/Azure/azure-functions-core-tools/blob/v4.x/README.md)
* [Python](https://www.python.org/downloads/) installed on your machine. 
* An Azure subscription. If you don't already have one, you can [sign up for one](https://azure.microsoft.com/).
* [Visual Studio Code](https://code.visualstudio.com/Download) installed.

## Create an Azure AI Foundry project

Let's start by creating an Azure AI Foundry project.

1. In a web browser, open the [Azure AI Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that might open.
1. In the home page, select **+ Create project**.
1. In the **Create a project** wizard, enter project name or accept the name provided.
1. If you don't have a hub yet created, you'll see the new hub name and can expand the section below to review the Azure resources that will be automatically created to support your project. If you are reusing a hub, skip the following step.
1. Select **Customize** and specify the following settings for your hub:

    | Setting | Value |
    |--|--|
    | Hub name | You can accept the provided name, or enter your own unique name - for example `my-ai-hub`. |  |
    | Subscription | Your Azure subscription. |
    | Resource group | Create a new resource group with a unique name (for example, `my-ai-resources`). Make note of the name you choose, it will be used later in this exercise. |
    | Location | Select **Help me choose** and then select **gpt-4o-mini** in the Location helper window and use the recommended region. |
    | Connect Azure AI Services or Azure OpenAI | Create a new AI Services resource with an appropriate name (for example, `my-ai-services`) or use an existing one.

    >**Note:** Model quotas are constrained at the tenant level by regional quotas. In the event of a quota limit being reached later in the exercise, there's a possibility you may need to create another project in a different region.

1. Select **Next** and review your configuration. Then select **Create** and wait for the process to complete.
1. After the deployment process completes, add a model to your project by selecting **Models + endpoints** in the **My assets** section of the navigation pane.
1. Select the **+ Deploy model**  drop down, and then select **Deploy base model**.
1. Select **gpt-4o-mini** from the list of available models, and then select **Confirm**. 
1. Select **Deploy** to deploy the model to your project. Don't change any of the values on the deployment summary.

## Create resources in Azure

In this section of the exercise you create the Azure Function App, the Azure Storage account used by the Function App, and a user-assigned managed identity. You created these in the Azure Cloud Shell using Azure CLI commands. The managed identity provides the authentication between the various resources in Azure.

### Launch the cloud shell and create the resources

1. Open the [Azure Portal](https://portal.azure.com) in a browser and launch the cloud shell. Select **bash** for the shell version.

1. Set variables used by the commands with the following commands. Replace `<myLocation>` and `<my-resource-group>` with the same values you used when creating the AI Foundry project earlier. **Note:** The `rndId` variable is used to help with unique service names.

    ```bash
    let "rndId=$RANDOM"
    location="<myLocation>"
    resourceGroup="<my-resource-group>"
    storage="staifunctool$rndId"
    functionApp="aifunctool$rndId"
    skuStorage="Standard_LRS"
    functionsVersion="4"
    pythonVersion="3.11" 
    managedIdentity="id-functool$rndId"
    ```

1. Create a storage account for the Azure Function App with the `az storage account create` command.

    ```bash
    echo "Creating $storage"
    az storage account create --name $storage --location "$location" \
        --resource-group $resourceGroup --sku $skuStorage
    ```

1. Create the Azure Function App with the `az functionapp create` command.

    ```bash
    # Create a serverless python function app in the resource group.
    echo "Creating $functionApp"
    az functionapp create --name $functionApp --storage-account $storage \
        --consumption-plan-location $location --resource-group $resourceGroup \
        --os-type Linux --runtime python --runtime-version $pythonVersion \
        --functions-version $functionsVersion
    ```

1. Create the user-assigned managed identity with the `az identity create` command.

    ```bash
    az identity create --resource-group $resourceGroup  --name $managedIdentity
    ```
