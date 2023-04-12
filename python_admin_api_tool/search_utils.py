import data_utils
import menu_utils
import pprint
import os
from dotenv import load_dotenv
from splitapiclient.main import get_client

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
# Initialize the client connection

client = get_client({'apikey': API_KEY})

def search_workspaces_or_groups():
    """
    Search for a workspace or Split group by name, and print information on the one found.
    
    Returns:
        output to stdout
    """
    while True:
        ws_or_gr_name = input("Enter the workspace or group name to search or 1 to go back to previous menu: ")
        if ws_or_gr_name == "1":
            menu_utils.search()
            break
        else:
            ws = client.workspaces.find(ws_or_gr_name)
            if ws:
                print(f"The workspace is found:")
                pprint.pprint(ws.to_dict())
            else:
                gr = client.groups.find(ws_or_gr_name)
                if not gr:
                    print(f"The workspace or group you entered does not exist. Please double check the name and try again")
                else:
                    groups_data = data_utils.get_groups_users()
                    user_list = groups_data.get(ws_or_gr_name, {}).get('Users', [])
                    print(f"The group id is {gr._id} and name is {gr._name}")
                    print(f"The users in this group are:")
                    pprint.pprint(user_list)

def search_environments():
    """
    Search for environments with the given name across all workspaces and return their information. Optionally, 
    display all Split definitions in each environment.

    Returns:
        Output to stdout
    """
    while True:
        env_name = input("Enter the environment name to search or 1 to go back to previous menu: ")
        if env_name == "1":
            menu_utils.search()
            break
        else:
            found_envs = []
            all_envs = data_utils.get_environments_data()
            for ws_id, ws_envs in all_envs.items():
                for ename, env in ws_envs.items():
                    if ename == env_name:
                        found_envs.append(env)
            if found_envs:
                print(f"Environment(s) found with name: {env_name}")
                print(f"Showing all environments of the same name across all workspaces:")
                for env in found_envs:
                    print("-------------------------------------------")
                    pprint.pprint(env)

                see_split_definitions = input("Do you want to see all the split definitions in this environment? (yes/no): ")
                if see_split_definitions.lower() == "yes" or see_split_definitions.lower() == "y":
                    for env in found_envs:
                        definitions = data_utils.get_split_definitions(env["ID"], env["Workspace ID"])
                        print(f"Split definitions for environment {env_name} in workspace {env['Workspace Name']}:")
                        pprint.pprint(definitions)
            else:
                print(f"Environment not found with name {env_name}")

def search_segments():
    """
    Searches for a segment with a given name across all environments and workspaces.
    Prints information on all matching segments.

    Returns:
        Output to stdout
    """
    segment_name = input("Enter the name of the segment: ")
    print("Showing segments of the same name across all environments and workspaces. This will take sometime, please wait...")
    segments_data = data_utils.get_segments(include_keys=True)
    found = False
    for key, segment in segments_data.items():
        if segment_name == segment['Segment Name']:
            found = True
            print("-------------------------------------------")
            pprint.pprint(key)
            print("-------------------------------------------")
            print("Segment definition : ")
            pprint.pprint(segment)

    if not found:
        print(f"Segment not found with name {segment_name}")

def search_users():
    """
    Search for a specific user by email address and display information on their status, 
    groups, and other details.

    Returns:
        Output to stdout
    """
    while True:
        email = input("Enter the email of the user or 1 to go back to previous menu: ")
        if email == "1":
            menu_utils.search()
            break
        else:
            user = client.users.find(email)
            if user:
                print(f"User found with email {email}")
                print(f"ID: {user.id}")
                print(f"Name: {user._name}")
                print(f"Email: {user.email}")
                print(f"Status: {user._status}")
                print(f"Type: {user._type}")
                groupnames = []
                user_groups = data_utils.get_groups()
                for group in user._groups:
                    if group["id"] in user_groups:
                        groupnames.append(user_groups[group["id"]])
                print(f"The user {user._name} is in groups:")
                pprint.pprint(groupnames)
            else:
                print(f"User not found with email {email}")

def get_split_definitions_by_name(split_name):
    """
    Returns a dictionary containing information on all Split definitions for a given split name,
    where the keys are the split names and the values are a list of split definitions.

    Args:
        split_name (str): The name of the Split definition to retrieve.

    Returns:
        A dictionary containing information on all Split definitions for the given split name.
    """
    all_definitions = data_utils.get_all_splits_definitions()
    definitions = {split_name: []}

    if split_name in all_definitions:
        definitions[split_name] = all_definitions[split_name]

    return definitions

def search_splits():
    """
    Searches for a specific Split by name and displays information on its attributes such as its name, ID, 
    workspace, environment, treatments, rules, etc. Optionally, the user can choose to display all the 
    Split definitions for the searched Split across all workspaces and environments.

    Returns:
        Output to stdout.
    """
    splits = data_utils.get_splits()
    while True:
        split_name = input("Enter the split name to search or 1 to go back to previous menu: ")
        if split_name == "1":
            menu_utils.search()
            break
        elif split_name in splits:
            print("Splits found:")
            for split_data in splits[split_name]:
                print("-------------------------------------------")
                pprint.pprint(split_data)
            see_split_definitions = input("Do you want to see the split definitions for this split? (yes/no): ")
            print("Showing all the Split definitions of the same Split name across all workspaces and environments")
            if see_split_definitions.lower() == "yes" or see_split_definitions.lower() == "y":
                print(f"This will take sometime, please wait...")
                split_definitions = get_split_definitions_by_name(split_name)
                for definition_data in split_definitions[split_name]:
                    print("-------------------------------------------")
                    environment_name = definition_data["environment"]["Name"]
                    workspace_name = definition_data["Workspace Name"]
                    print(f"Split definition for Split {split_name} in environment {environment_name} and workspace {workspace_name}:")
                    pprint.pprint(definition_data)
        else:
            print("Split not found")