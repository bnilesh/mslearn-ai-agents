import os
from dotenv import load_dotenv
from typing import Any
from pathlib import Path


# Add references


def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    PROJECT_CONNECTION_STRING= os.getenv("PROJECT_CONNECTION")
    MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT")

    # Load data to be analyzed
    script_dir = Path(__file__).parent  # Get the directory of the script
    file_path = script_dir / 'data.txt'

    with file_path.open('r') as file:
        data = file.read()
        print(data)

    # Connect to the Azure AI Foundry project



    # Define an agent that uses the CodeInterpreter tool

    
        # Loop until the user types 'quit'
        while True:
            # Get input text
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            if len(user_prompt) == 0:
                print("Please enter a prompt.")
                continue

            # Send a prompt to the agent


            # Check the run status for failures

    
            # Get messages from the thread

    
            # Save any generated files


        # Delete the agent when done

    


if __name__ == '__main__': 
    main()