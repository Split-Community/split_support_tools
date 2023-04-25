import data_utils
import menu_utils
import export_utils
import pprint
import os
import logging
from dotenv import load_dotenv
from splitapiclient.main import get_client

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
# Initialize the client connection

client = get_client({'apikey': API_KEY})

logger = logging.getLogger(__name__)

def configure_logging(debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

def search_workspaces_or_groups():
    """
    Search for a workspace or Split group by name, and print information on the one found.
    
    Returns:
        output to stdout
    """
    while True:
        print("-------------------------------------------\n")
        ws_or_gr_name = input("Enter the workspace or group name to search or 1 to go back to previous menu: ")
        if ws_or_gr_name == "1":
            menu_utils.search()
            break
        else:
            ws = client.workspaces.find(ws_or_gr_name)
            if ws:
                print(f"The workspace is found:")
                print("-------------------------------------------\n")
                pprint.pprint(ws.to_dict())
                print("-------------------------------------------\n")
            else:
                gr = client.groups.find(ws_or_gr_name)
                if not gr:
                    print(f"The workspace or group you entered does not exist. Please double check the name and try again")
                else:
                    groups_data = data_utils.get_groups_users()
                    user_list = groups_data.get(ws_or_gr_name, {}).get('Users', [])
                    print("-------------------------------------------\n")
                    print(f"The group id is {gr._id} and name is {gr._name}")
                    print(f"The users in this group are:")
                    pprint.pprint(user_list)
                    print("-------------------------------------------\n")

def search_environments():
    """
    Search for environments with the given name across all workspaces and return their information. Optionally, 
    display all Split definitions in each environment.

    Returns:
        Output to stdout
    """
    while True:
        print("-------------------------------------------\n")
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
                print("-------------------------------------------\n")
                print(f"Environment(s) found with name: {env_name}")
                print(f"Showing all environments of the same name across all workspaces:")
                for env in found_envs:
                    print("-------------------------------------------")
                    pprint.pprint(env)
                print("-------------------------------------------\n")
            else:
                print(f"Environment not found with name {env_name}")

def search_users():
    """
    Search for a specific user by email address and display information on their status, 
    groups, and other details.

    Returns:
        Output to stdout
    """
    while True:
        print("-------------------------------------------\n")
        email = input("Enter the email of the user or 1 to go back to previous menu: ")
        if email == "1":
            menu_utils.search()
            break
        else:
            user = client.users.find(email)
            if user:
                print("-------------------------------------------\n")
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
                print("-------------------------------------------\n")
            else:
                print(f"User not found with email {email}")

def get_segment_definitions_by_name(segment_name):
    all_definitions = data_utils.get_all_segments_definitions()
    definitions = {}

    for key in all_definitions.keys():
        if key.startswith(segment_name):
            segment_name, environment_id, workspace_id = key.split('.')
            if segment_name not in definitions:
                definitions[segment_name] = []
            definitions[segment_name].append(all_definitions[key])

    return definitions

def search_segments():
    """
    Searches for a specific segment by name and displays information on its attributes such as its name, ID, 
    workspace, environment, etc. Optionally, the user can choose to display the 
    segment definition for the searched segment in a specific workspace and environment.

    Returns:
        Output to stdout.
    """
    segments = data_utils.get_segments()
    while True:
        print("-------------------------------------------\n")
        segment_name = input("Enter the segment name to search or 1 to go back to previous menu: ")
        if segment_name == "1":
            menu_utils.search()
            break

        found_segments = []
        for workspace_name, workspace_segments in segments.items():
            if segment_name in workspace_segments:
                found_segments.append((workspace_name, workspace_segments[segment_name]))

        if found_segments:
            print("Segments found:")
            for workspace_name, segment_data in found_segments:
                print("-------------------------------------------")
                print(f"Workspace: {workspace_name}")
                pprint.pprint(segment_data)
            print("-------------------------------------------\n")
            segment_definitions = data_utils.get_all_segments_definitions()

            while True:
                print("-------------------------------------------\n")
                see_segment_definitions = input("Do you want to see the segment definitions for this segment? (yes/no): ")
                if see_segment_definitions.lower() == "yes" or see_segment_definitions.lower() == "y":
                    
                    workspaces = {definition_data["workspace"]["name"]: definition_data["workspace"]["id"] for definition_key, definition_data in segment_definitions.items() if definition_data['name'] == segment_name}
                    if not workspaces:
                        print("No workspaces containing the segment found.")
                        break
                    print("Workspaces containing the segment:")
                    print("-------------------------------------------\n")
                    for index, workspace_name in enumerate(workspaces, 1):
                        print(f"{index}. {workspace_name}")
                    print("-------------------------------------------\n")

                    chosen_workspace = int(input("Choose a workspace by entering its number: "))
                    chosen_workspace_name = list(workspaces)[chosen_workspace-1]

                    environments = {definition_data["environment"]["name"]: definition_data["environment"]["id"] for definition_key, definition_data in segment_definitions.items() if definition_data['name'] == segment_name and definition_data["workspace"]["name"] == chosen_workspace_name}
                    if not environments:
                        print("No environments containing the segment's definitions found.")
                        break
                    
                    print("Environments in the chosen workspace containing the segment's definitions:")
                    print("-------------------------------------------\n")
                    for index, environment_name in enumerate(environments, 1):
                        print(f"{index}. {environment_name}")
                    print("-------------------------------------------\n")

                    chosen_environment = int(input("Choose an environment by entering its number: "))
                    chosen_environment_name = list(environments)[chosen_environment-1]
                    chosen_workspace_id = workspaces[chosen_workspace_name]
                    chosen_environment_id = environments[chosen_environment_name]

                    for definition_key, definition_data in segment_definitions.items():
                        if definition_data['name'] == segment_name and definition_data["workspace"]["name"] == chosen_workspace_name and definition_data["environment"]["name"] == chosen_environment_name:
                            print("-------------------------------------------")
                            print(f"Segment definition for Segment {segment_name} in environment {chosen_environment_name} and workspace {chosen_workspace_name}:")
                            pprint.pprint(definition_data)
                            #export_option = input("Do you want to export this segment definition? (yes/no): ")
                            #if export_option.lower() == "yes" or export_option.lower() == "y":
                            #    export_utils.export_specific_segment_definition(definition_data)
                            print("-------------------------------------------\n")
                            export_keys_option = input("Do you want to export keys under this segment? (yes/no): ")
                            if export_keys_option.lower() == "yes" or export_keys_option.lower() == "y":
                                file_name = f"{segment_name}.{chosen_environment_name}.{chosen_workspace_name}"
                                segDef = client.segment_definitions.find(segment_name, chosen_environment_id, chosen_workspace_id)
                                segDef.export_keys_to_csv(f"{file_name}.csv")
                                print(f"The keys have been exported to {file_name}")
                            break
                else:
                    break
        else:
            print("Segment not found")

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
    definitions = {}
    
    for key in all_definitions.keys():
        if key.startswith(split_name):
            #split_name, environment_id, workspace_id = key.split('.')
            split_name, environment_id, workspace_id = key.rsplit('.', 2)
            if split_name not in definitions:
                definitions[split_name] = []
            definitions[split_name].append(all_definitions[key])
    
    return definitions

def search_splits():
    """
    Searches for a specific Split by name and displays information on its attributes such as its name, ID, 
    workspace, environment, treatments, rules, etc. Optionally, the user can choose to display the 
    Split definition for the searched Split in a specific workspace and environment.

    Returns:
        Output to stdout.
    """
    splits = data_utils.get_splits()
    while True:
        print("-------------------------------------------\n")
        split_name = input("Enter the split name to search or 1 to go back to previous menu: ")
        if split_name == "1":
            menu_utils.search()
            break
        elif split_name in splits:
            print("Splits found:")
            for split_data in splits[split_name]:
                print("-------------------------------------------")
                pprint.pprint(split_data)
            print("-------------------------------------------\n")
            split_definitions = get_split_definitions_by_name(split_name)
            workspaces = {definition_data["workspace"] for definition_data in split_definitions[split_name]}
            exported = False
            while not exported:
                see_split_definitions = input("Do you want to see the split definitions for this split? (yes/no): ")
                if see_split_definitions.lower() == "yes" or see_split_definitions.lower() == "y":
                    print("Workspaces containing the split:")
                    print("-------------------------------------------\n")
                    for index, workspace_name in enumerate(workspaces, 1):
                        print(f"{index}. {workspace_name}")
                    print("-------------------------------------------\n")

                    chosen_workspace = int(input("Choose a workspace by entering its number: "))
                    chosen_workspace_name = list(workspaces)[chosen_workspace-1]

                    environments = {definition_data["environment"]["name"] for definition_data in split_definitions[split_name] if definition_data["workspace"] == chosen_workspace_name}
                    print("Environments in the chosen workspace containing the split's definitions:")
                    print("-------------------------------------------\n")
                    for index, environment_name in enumerate(environments, 1):
                        print(f"{index}. {environment_name}")
                    print("-------------------------------------------\n")
                    chosen_environment = int(input("Choose an environment by entering its number: "))
                    chosen_environment_name = list(environments)[chosen_environment-1]

                    for definition_data in split_definitions[split_name]:
                        if definition_data["workspace"] == chosen_workspace_name and definition_data["environment"]["name"] == chosen_environment_name:
                            print("-------------------------------------------")
                            print(f"Split definition for Split {split_name} in environment {chosen_environment_name} and workspace {chosen_workspace_name}:")
                            pprint.pprint(definition_data)
                            print("-------------------------------------------\n")
                            export_option = input("Do you want to export this split definition? (yes/no): ")
                            if export_option.lower() == "yes" or export_option.lower() == "y":
                                export_utils.export_specific_split_definition(definition_data)

                            export_treatments_option = input("Do you want to export keys under treatments to json? (yes/no): ")
                            if export_treatments_option.lower() == "yes" or export_treatments_option.lower() == "y":
                                file_name = f"{split_name}.{chosen_environment_name}.{chosen_workspace_name}_treatments.json"
                                export_utils.export_treatment_keys_to_json(definition_data["treatments"], file_name)
                            
                            export_treatments_option = input("Do you want to export keys under treatments to csv? (yes/no): ")
                            if export_treatments_option.lower() == "yes" or export_treatments_option.lower() == "y":
                                file_name = f"{split_name}.{chosen_environment_name}.{chosen_workspace_name}_treatments.csv"
                                export_utils.export_treatment_keys_to_csv(definition_data["treatments"], file_name)

                            export_matchers_option = input("Do you want to export the Targeting rules to json? (yes/no): ")
                            if export_matchers_option.lower() == "yes" or export_matchers_option.lower() == "y":
                                file_name = f"{split_name}.{chosen_environment_name}.{chosen_workspace_name}_matchers.json"
                                export_utils.export_matcher_type_and_strings_to_json(definition_data["rules"], file_name)
                            
                            export_matchers_option = input("Do you want to export the Targeting rules to csv? (yes/no): ")
                            if export_matchers_option.lower() == "yes" or export_matchers_option.lower() == "y":
                                file_name = f"{split_name}.{chosen_environment_name}.{chosen_workspace_name}_matchers.csv"
                                export_utils.export_matcher_type_and_strings_to_csv(definition_data["rules"], file_name)
                    exported = True
                    break    
                else:
                    break
        else:
            print("Split not found")
