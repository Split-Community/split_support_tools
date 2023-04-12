import menu_utils
import os
from dotenv import load_dotenv
from splitapiclient.main import get_client
from splitapiclient.util.exceptions import HTTPNotFoundError

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
# Initialize the client connection

client = get_client({'apikey': API_KEY})

def delete_splits():
    """
    Deletes a specific Split by name within a given workspace.

    Returns:
        Output to stdout.
    """
    while True:
        workspace_name = input("Enter the workspace name or 1 to go back to prevous menu: ")
        if workspace_name == "1":
            menu_utils.operations()
            break
        ws = client.workspaces.find(workspace_name)
        if ws:
            while True:
                split_name = input("Enter the Split name to delete or 1 to go back to previous menu: ")
                if split_name == "1":
                    break
                else:
                    confirm = input(f"Are you sure you want to delete the split '{split_name}' in workspace '{workspace_name}'? (yes/no): ")
                    if confirm.lower() == "yes" or confirm.lower() == "y":
                        try:
                            deleted = ws.delete_split(split_name)
                            if deleted:
                                print(f"The split '{split_name}' has been deleted from workspace '{workspace_name}'")
                            else:
                                print(f"Failed to delete the split '{split_name}' from workspace '{workspace_name}'")
                        except HTTPNotFoundError:
                            print(f"The split '{split_name}' was not found in workspace '{workspace_name}'")
                    else:
                        print("Deletion cancelled")
        else:
            print("Workspace not found")