import os
import json
import re
import pprint
from dotenv import load_dotenv
from splitapiclient.main import get_client
from splitapiclient.util.exceptions import HTTPNotFoundError

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
# Initialize the client connection

client = get_client({'apikey': API_KEY})

def quit_tool():
    print("Goodbye!")
    exit()

def get_workspaces():
    """
    Retrieve a dictionary of workspaces, where the keys are the workspace IDs
    and the values are the workspace names.

    Returns:
        dict: A dictionary of workspace IDs and names.
    """
    return {ws.id: ws.name for ws in client.workspaces.list()}

def get_workspace_data():
    """
    Retrieve a dictionary of workspace data, where the keys are the workspace IDs
    and the values are dictionaries containing workspace information such as
    name and whether title and comments are required.

    Returns:
        dict: A dictionary of workspace data.
    """
    return {
        ws.id: {
            "Name": ws.name,
            "Requires Title And Comments": ws._requiresTitleAndComments,
        }
        for ws in client.workspaces.list()
    }

def get_environments_data():
    """Returns a dictionary containing information about all environments across all workspaces.

    Returns:
    dict: A dictionary with keys as workspace names and values as dictionaries containing information 7
    about all environments of the respective workspace.
    """
    all_envs = {}
    workspaces = get_workspaces()
    for ws_id, ws_name in workspaces.items():
        environments = client.environments.list(ws_id)
        envs_for_ws = {}
        for env in environments:
            env_dict = {
                'Workspace ID': ws_id,
                'Workspace Name': ws_name,
                'Creation Time': env._creationTime,
                'Production': env._production,
                'Data Export Permissions': {},
                'Environment Type': env._type,
                'Name': env._name,
                'Change Permissions': {},
                'ID': env._id,
                'Org Id': env._orgId,
                'status': env._status
            }
            if env._dataExportPermissions:
                env_dict['Data Export Permissions'] = {
                    'areExportersRestricted': env._dataExportPermissions.get('areExportersRestricted'),
                    'exporters': env._dataExportPermissions.get('exporters', [])
                }
            if env._changePermissions:
                env_dict['Change Permissions'] = {
                    'areApproversRestricted': env._changePermissions.get('areApproversRestricted'),
                    'allowKills': env._changePermissions.get('allowKills'),
                    'areEditorsRestricted': env._changePermissions.get('areEditorsRestricted'),
                    'areApprovalsRequired': env._changePermissions.get('areApprovalsRequired'),
                    'approvers': env._changePermissions.get('approvers', []),
                    'editors': env._changePermissions.get('editors', [])
                }
            envs_for_ws[env._name] = env_dict
        all_envs["Workspace: " + ws_name] = envs_for_ws
    return all_envs

def get_environments():
    """
    Returns a dictionary of all environment IDs and names across all workspaces.
    """
    return {env.id: env.name for ws_id, _ in get_workspaces().items() for env in client.environments.list(ws_id)}

def get_segments():
    """
    Get data for all segments in all environments across all workspaces.

    Returns:
        A dictionary containing information on all segments, grouped by segment name and environment.
    """
    segments_data = {}

    for workspace_id, workspace_name in get_workspaces().items():
        ws = client.workspaces.find(workspace_name)

        for env in client.environments.list(ws.id):
            for segDef in client.segment_definitions.list(env.id, ws.id):
                segments_data["Segment: " + segDef.name + " in " + "Environment: " + env._name] = {
                    "Segment Name": segDef.name,
                    "Environment": {
                        "ID": env.id,
                        "Name": env._name
                    },
                    "Workspace" :
                    {
                        "ID" : ws.id,
                        "Name" : workspace_name
                    },
                    "Traffic Type": {
                        "ID": segDef._trafficType._id,
                        "Name": segDef._trafficType._name
                    },
                    "Creation Time": segDef._creationTime,
                    "Keys": client.segment_definitions.find(segDef.name, env.id, ws.id).get_keys()
                }

    return segments_data

def get_groups():
    """
    Get all user groups.

    Returns:
        dict: A dictionary where the keys are the group IDs and the values are the group names.
    """
    return {group._id: group._name for group in client.groups.list()}

def get_all_users():
    """
    Retrieves all active Split users and their associated group memberships.

    Returns:
        A dictionary where the keys are the user names and the values are dictionaries containing user information,
        including name, email, status, and a list of groups to which the user belongs.

    """
    groups_dict = get_groups()
    users = {}

    for user in client.users.list("ACTIVE"):
        user_data = {
            "Type": user._type,
            "Name": user._name,
            "Email": user.email,
            "Status": user._status,
            "Groups": [
                {
                    "type": group["type"],
                    "ID": group["id"],
                    "Name": groups_dict[group["id"]]
                }
                for group in user._groups
            ]
        }
        users[user._name] = user_data
    return users

def get_splits():
    """
    Get data for all splits across all workspaces.

    Returns:
        A dictionary containing information on all splits, grouped by split name.
    """
    workspaces = get_workspaces()
    splits = {}
    for workspace_id, workspace_name in workspaces.items():
        for split in client.splits.list(workspace_id):
            split_data = {
                "Workspace Name": workspace_name,
                "Workspace ID": workspace_id,
                "ID": split.id,
                "Name": split.name,
                "Description": split.description,
                "Traffic Type ID": split._trafficType._id,
                "Traffic Type Name": split._trafficType.name,
                "Creation Time": split._creationTime,
                "Rollout Status ID": split._rolloutStatus['id'],
                "Rollout Status Name": split._rolloutStatus['name'],
                "Rollout Status Timestamp": split._rolloutStatusTimestamp,
                "Tags": split._tags,
                "Owners": split._owners,
            }
            if split.name not in splits:
                splits[split.name] = [split_data]
            else:
                splits[split.name].append(split_data)
    return splits

def get_split_definition(environment_id, workspace_id, split_def):
    """
    Return a dictionary containing detailed information about a split definition.

    Args:
        environment_id (str): The ID of the environment.
        workspace_id (str): The ID of the workspace.
        split_def: The split definition object.

    Returns:
        A dictionary containing detailed information about the split definition, including its name,
        environment, traffic type, treatments, rules, default rules, and other metadata.

    """
    workspaces = get_workspaces()
    return {
        "Workspace Name" :workspaces[workspace_id],
        "Name": split_def.name,
        "environment": {
            "ID" : split_def._environment.id,
            "Name" : split_def._environment.name
        },
        "trafficType": {
            "ID": split_def._trafficType.id,
            "Name": split_def._trafficType.name
        },
        "killed": split_def._killed,
        "treatments": [{"Name": t._name, "configurations": t._configurations,
                        "description": t._description, 
                        "keys": t._keys, "segments": t._segments} 
                        for t in split_def._treatments],
        "defaultTreatment": split_def._default_treatment,
        "baselineTreatment": split_def._baseline_treatment,
        "trafficAllocation": split_def._traffic_allocation,
        "rules": [{
            "condition": {
                "combiner": rule._condition["combiner"],
                "matchers": [{
                    "negate": matcher.get('negate', False),
                    "type": matcher.get('type', False),
                    "attribute": matcher.get('attribute', False),
                    "string": matcher.get('string', False),
                    "bool": matcher.get('bool', False),
                    "strings": matcher.get('strings', False),
                    "number": matcher.get('number', False),
                    "date": matcher.get('date', False),
                    "between": matcher.get('between', False),
                    "depends": matcher.get('depends', False),
                } for matcher in rule._condition["matchers"]]
            },
            "buckets": [{
                "treatment": bucket.get('treatment', False),
                "size": bucket.get('size', False)
            } for bucket in rule._buckets]
        } for rule in split_def._rules],
        "defaultRule": [{
            "treatment": default_rule._treatment,
            "size": default_rule._size
        } for default_rule in split_def._default_rule],
        "creationTime": split_def._creationTime,
        "lastUpdateTime": split_def._lastUpdateTime
    }

def get_split_definitions(environment_id, workspace_id):
    """
    Get data for all Split definitions in a specific environment and workspace.

    Args:
        environment_id (str): ID of the environment to retrieve Split definitions from.
        workspace_id (str): ID of the workspace to retrieve Split definitions from.

    Returns:
        A dictionary containing information on all Split definitions, grouped by Split definition name.
        Each Split definition contains data on the definition's treatments, rules, and other attributes.

    """
    definitions = {}
    for split_def in client.split_definitions.list(environment_id, workspace_id):
        split_name = split_def.name
        if split_name not in definitions:
            definitions[split_name] = [get_split_definition(environment_id, workspace_id, split_def)]
        else:
            definitions[split_name].append(get_split_definition(environment_id, workspace_id, split_def))
    return definitions

def get_all_splits_definitions():
    """
    Get all Split definitions across all workspaces and environments.

    Returns:
        A dictionary containing information on all Split definitions, grouped by Split name.
    """
    workspaces = get_workspaces()
    environments = get_environments()
    definitions = {}
    for workspace_id, workspace_name in workspaces.items():
        for environment_id, environment_name in environments.items():
            workspace_definitions = get_split_definitions(environment_id, workspace_id)
            for split_name, split_definitions in workspace_definitions.items():
                if split_name not in definitions:
                    definitions[split_name] = split_definitions
                else:
                    definitions[split_name].extend(split_definitions)
    return definitions

def get_groups_users():
    """
    Returns a dictionary containing information on all Split user groups, where the keys are the group names and the 
    values are a dictionary containing the group name and a list of users in that group.

    Returns:
        A dictionary containing information on all Split user groups.
    """
    status = "ACTIVE"
    groups_dict = get_groups()
    users = client.users.list(status)
    users_data = {}
    for user in users:
        for group in user._groups:
            if groups_dict[group["id"]] in users_data:
                users_data[groups_dict[group["id"]]].append(user._name)
            else:
                users_data[groups_dict[group["id"]]] = [user._name]
    groups_data = {group: {"Group": group, "Users": users} for group, users in users_data.items()}
    return groups_data

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
def search_workspaces_or_groups():
    """
    Search for a workspace or Split group by name, and print information on the one found.
    
    Returns:
        output to stdout
    """
    while True:
        ws_or_gr_name = input("Enter the workspace or group name to search or 1 to go back to previous menu: ")
        if ws_or_gr_name == "1":
            search()
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
                    groups_data = get_groups_users()
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
            search()
            break
        else:
            found_envs = []
            all_envs = get_environments_data()
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
                if see_split_definitions.lower() == "yes":
                    for env in found_envs:
                        definitions = get_split_definitions(env["ID"], env["Workspace ID"])
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
    segments_data = get_segments()
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
            search()
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
                user_groups = get_groups()
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
    all_definitions = get_all_splits_definitions()
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
    splits = get_splits()
    while True:
        split_name = input("Enter the split name to search or 1 to go back to previous menu: ")
        if split_name == "1":
            search()
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
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

def export_data_to_json(data_type, data_getter, file_name_format):
    data = data_getter()
    with open(data_type + "_data" + ".json", "w") as file:
        file.write(json.dumps(data, indent=4))

def export_data(data_type, data_getter, file_name_format=None):
    """
    Exports data to a JSON file with the given filename and displays a success message.

    Args:
        data_type (str): The type of data being exported.
        data_getter (function): A function that returns the data to be exported.
        file_name_format (str): A string with placeholders for formatting the filename, such as "{date}".

    Returns:
        None
    """
    print("Exporting data, please wait...")
    export_data_to_json(data_type, data_getter, file_name_format)
    print(f"{data_type} data exported successfully!")

def export_splits():
    """
    Export all Split data as a JSON file with the name "splits_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("splits", get_splits, "{0}_splits")

def export_users():
    """
    Export all user data as a JSON file with the name "users_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("users", get_all_users, "{0}_users")

def export_workspaces():
    """
    Export all workspace data as a JSON file with the name "workspaces_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("workspaces", get_workspace_data, "{0}_workspaces")

def export_segments():
    """
    Export all segment data as a JSON file with the name "segments_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("segments", get_segments, "{0}_segments")

def export_groups():
    """
    Export all group data as a JSON file with the name "groups_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("groups", get_groups_users, "{0}_groups")

def export_environments():
    """
    Export all environment data as a JSON file with the name "environments_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("environments", get_environments_data, "{0}_environments")

def export_split_definitions():
    """
    Export all Split definition data as a JSON file with the name "split_definitions_data.json" to the current working 
    directory.

    Returns:
        Output to stdout
    """
    export_data("split_definitions", get_all_splits_definitions, "{0}_split_definitions")

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
def delete_splits():
    """
    Deletes a specific Split by name within a given workspace.

    Returns:
        Output to stdout.
    """
    while True:
        workspace_name = input("Enter the workspace name or 1 to go back to prevous menu: ")
        if workspace_name == "1":
            operations()
            break
        ws = client.workspaces.find(workspace_name)
        if ws:
            while True:
                split_name = input("Enter the Split name to delete or 1 to go back to previous menu: ")
                if split_name == "1":
                    break
                else:
                    confirm = input(f"Are you sure you want to delete the split '{split_name}' in workspace '{workspace_name}'? (yes/no): ")
                    if confirm.lower() == "yes":
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

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

def format_text(text):
    """
    Replace underscores in the text with spaces and format the text to title case.

    Args:
        text: A string to be formatted.

    Returns:
        A formatted string in title case.
    """
    text = re.sub('_', ' ', text)
    return text.title()

def display_options(options, menu_name):
    """
    Display a list of options as a formatted menu.

    Args:
        options: A dictionary containing the menu options.
        menu_name: A string containing the name of the menu to display.

    Returns:
        Output to stdout.
    """
    formatted_options = [
        f"{key}. {format_text(func.__name__)}"
        for key, func in options.items()
    ]
    print("----------------------------------------")
    print(f"PYTHON ADMIN API TOOL - {menu_name}")
    print("----------------------------------------")
    print("\n".join(formatted_options))

def get_choice(options, menu_name):
    """
    Displays the options of the given menu and prompts the user to enter a choice. 
    If the choice is valid, the corresponding function is called. If the choice is 
    invalid, an error message is displayed and the prompt is repeated.

    Args:
        options (dict): A dictionary containing the menu options where keys are the option numbers 
            and values are the functions to execute when the option is chosen.
        menu_name (str): The name of the menu to be displayed.

    Returns:
        Output to stdout.
    """

    while True:
        display_options(options, menu_name)
        choice = input(f"Enter your choice (1-{len(options)}): ")
        try:
            options[choice]()
        except (KeyError, ValueError, IndexError):
            print("Invalid choice, try again")
        except KeyboardInterrupt:
            print("\nExiting...")
            quit_tool()

def search():
    options = {
        "1": search_workspaces_or_groups,
        "2": search_environments,
        "3": search_users,
        "4": search_splits,
        "5": search_segments,
        "6": main_menu,
        "7": quit_tool,
    }
    get_choice(options, "Search")

def export_all_data():
    options = {
        "1": export_groups,
        "2": export_segments,
        "3": export_splits,
        "4": export_split_definitions,
        "5": export_users,
        "6": export_workspaces,
        "7": export_environments,
        "8": main_menu,
        "9": quit_tool
    }
    get_choice(options, "Export")

def operations():
    options = {
        "1": delete_splits,
        "2": main_menu,
        "3": quit_tool
    }
    get_choice(options, "Operations")

def main_menu():
    options = {
        "1": search,
        "2": export_all_data,
        "3": operations,
        "4": quit_tool
    }
    get_choice(options, "Main")

if __name__ == '__main__':
    main_menu()