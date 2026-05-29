import os
from dotenv import load_dotenv
from typing import Any
from pathlib import Path

from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool


def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    if "SSL_CERT_FILE" in os.environ:
        del os.environ["SSL_CERT_FILE"]

    load_dotenv()
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([project_endpoint, model_deployment, tenant_id, client_id, client_secret]):
        raise EnvironmentError(
            "Missing required environment variables. Ensure PROJECT_ENDPOINT, "
            "MODEL_DEPLOYMENT_NAME, AZURE_TENANT_ID, AZURE_CLIENT_ID, and "
            "AZURE_CLIENT_SECRET are set in your .env file."
        )

    script_dir = Path(__file__).parent
    file_path = script_dir / 'data.txt'

    with file_path.open('r') as file:
        data = file.read() + "\n"
        print(data)

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )

    with (
        credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        file = openai_client.files.create(
            file=open(file_path, "rb"), purpose="assistants"
        )
        print(f"Uploaded {file.filename}")

        code_interpreter = CodeInterpreterTool()

        agent = project_client.agents.create_version(
            agent_name="data-agent",
            definition=PromptAgentDefinition(
                model=model_deployment,
                instructions="You are an AI agent that analyzes the data in the file that has been uploaded. Use Python to calculate statistical metrics as necessary.",
                tools=[code_interpreter],
            ),
        )
        print(f"Using agent: {agent.name}")

        conversation = openai_client.conversations.create()

        while True:
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            if not user_prompt.strip():
                print("Please enter a prompt.")
                continue

            openai_client.conversations.items.create(
                conversation_id=conversation.id,
                items=[{"type": "message", "role": "user", "content": [
                    {"type": "input_file", "file_id": file.id},
                    {"type": "input_text", "text": user_prompt},
                ]}],
            )

            response = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
                input="",
            )

            if response.status == "failed":
                print(f"Response failed: {response.error}")
                continue

            print(f"Agent: {response.output_text}")

        print("\nConversation Log:\n")
        items = openai_client.conversations.items.list(conversation_id=conversation.id)
        for item in items:
            if item.type == "message":
                role = item.role.upper()
                content = item.content[0].text
                print(f"{role}: {content}\n")

        openai_client.conversations.delete(conversation_id=conversation.id)
        print("Conversation deleted")

        project_client.agents.delete(agent_name=agent.name)
        print("Agent deleted")


if __name__ == '__main__':
    main()
