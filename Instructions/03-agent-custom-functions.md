---
lab:
    title: 'Implement custom tools in an AI agent'
    description: 'TODO.'
---

# Implement custom tools in an AI agent

In this exercise you will explore using built-in tools in Azure AI Foundry to connect to knowledge sources and interpret code. Then, you'll develop a basic agent in Python or C# (C# coming soon).

This exercise should take approximately **30** minutes to complete.

## Before you start

To complete this exercise, you'll need:

* Azure Functions Core Tools. Most recent version 4.0.6x, or greater, recommended.
    * Windows [v4.x - Windows 64-bit](https://go.microsoft.com/fwlink/?linkid=2174087)
    * For installation on other operating systems visit [Azure Functions Core Tools on GitHub](https://github.com/Azure/azure-functions-core-tools/blob/v4.x/README.md)
* [Python](https://www.python.org/downloads/) installed on your machine. 
* An Azure subscription. If you don't already have one, you can [sign up for one](https://azure.microsoft.com/).
* [Visual Studio Code](https://code.visualstudio.com/Download) installed.

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
    - **Connect Azure AI Services or Azure OpenAI**: *Create a new AI Services resource with an appropriate name (for example, `my-ai-services`) or use an existing one*
    - **Connect Azure AI Search**: Skip connecting

    > \* Model quotas are constrained at the tenant level by regional quotas. In the event of a quota limit being reached later in the exercise, there's a possibility you may need to create another project in a different region.

1. Select **Next** and review your configuration. Then select **Create** and wait for the process to complete.
