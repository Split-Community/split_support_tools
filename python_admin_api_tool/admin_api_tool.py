import os
import json
import re
import pprint
import pickle
from dotenv import load_dotenv
from splitapiclient.main import get_client
from splitapiclient.util.exceptions import HTTPNotFoundError

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
# Initialize the client connection

client = get_client({'apikey': API_KEY})

def get_workspaces():
    """
    Retrieve a dictionary of workspaces, where the keys are the workspace IDs
    and the values are the workspace names.

    Returns:
        dict: A dictionary of workspace IDs and names.
    """
    global cache_data

    if cache_data["workspaces"] is None:
        # If the workspaces are not in the cache, fetch them from the server
        workspace_dict = {ws.id: ws.name for ws in client.workspaces.list()}
        cache_data["workspaces"] = workspace_dict
        save_cache() # Save the updated cache
    else:
        # If the workspaces are in the cache, retrieve them from there
        workspace_dict = cache_data["workspaces"]

    return workspace_dict

def get_workspace_data():
    """
    Retrieve a dictionary of workspace data, where the keys are the workspace IDs
    and the values are dictionaries containing workspace information such as
    name and whether title and comments are required.

    Returns:
        dict: A dictionary of workspace data.
    """
    if cache_data["workspace_data"] is not None:
        # return cached data if available
        return cache_data["workspace_data"]
    else:
        # retrieve data from API if not cached
        workspace_data = {
            ws.id: {
                "Name": ws.name,
                "Requires Title And Comments": ws._requiresTitleAndComments,
            }
            for ws in client.workspaces.list()
        }
        # save to cache
        cache_data["workspace_data"] = workspace_data
        save_cache()
        return workspace_data

def get_environments_data():
    """
    Retrieve a dictionary containing information about all environments across all workspaces.

    Returns:
        dict: A dictionary with keys as workspace names and values as dictionaries containing information
        about all environments of the respective workspace.
    """
    global cache_data
    if cache_data['environments_data'] is not None:
        return cache_data['environments_data']
    
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
    
    # Update cache
    cache_data['environments_data'] = all_envs
    save_cache()
    
    return all_envs

def get_environments():
    """
    Retrieve a dictionary of environment data

    Returns:
        dict: A dictionary of environment name, id, and workspace.
    """
    if cache_data["environments"] is None:
        environments = {}
        for ws_id, ws_name in get_workspaces().items():
            for env in client.environments.list(ws_id):
                environments[env.id] = {
                    "Name": env.name,
                    "Workspace Name": ws_name
                }
        cache_data["environments"] = environments
        save_cache()  # Save the updated cache
    else:
        environments = cache_data["environments"]
    return environments

def get_segments(include_keys=True):
    """
    Get data for all segments in all environments across all workspaces.

    Args:
        include_keys (bool): Whether to include the segment keys or not. Defaults to True.

    Returns:
        A dictionary containing information on all segments, grouped by segment name and environment.
    """
    global cache_data

    # Check if segments data is already in the cache
    if cache_data.get('segments') is not None:
        return cache_data['segments']

    # If not, fetch the segments data
    segments_data = {}

    for workspace_id, workspace_name in get_workspaces().items():
        for env in client.environments.list(workspace_id):
            for segDef in client.segment_definitions.list(env.id, workspace_id):
                segment_info = {
                    "Segment Name": segDef.name,
                    "Environment": {
                        "ID": env.id,
                        "Name": env._name
                    },
                    "Workspace": {
                        "ID": workspace_id,
                        "Name": workspace_name
                    },
                    "Traffic Type": {
                        "ID": segDef._trafficType._id,
                        "Name": segDef._trafficType._name
                    },
                    "Creation Time": segDef._creationTime
                }

                if include_keys:
                    segment_info["Keys"] = client.segment_definitions.find(segDef.name, env.id, workspace_id).get_keys()

                segments_data[f"Segment: {segDef.name} in Environment: {env._name}"] = segment_info

    # Add the segments data to the cache
    cache_data['segments'] = segments_data

    return segments_data

def get_groups():
    """
    Get all user groups.

    Returns:
        dict: A dictionary where the keys are the group IDs and the values are the group names.
    """
    if cache_data["groups"] is not None:
        return cache_data["groups"]

    groups = {group._id: group._name for group in client.groups.list()}
    cache_data["groups"] = groups
    save_cache()

    return groups

def get_all_users():
    """
    Retrieves all active Split users and their associated group memberships.

    Returns:
        A dictionary where the keys are the user names and the values are dictionaries containing user information,
        including name, email, status, and a list of groups to which the user belongs.

    """
    if cache_data["users"]:
        return cache_data["users"]
    
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
    
    cache_data["users"] = users
    save_cache()
    return users

def get_groups_users():
    """
    Returns a dictionary containing information on all Split user groups, where the keys are the group names and the 
    values are a dictionary containing the group name and a list of users in that group.

    Returns:
        A dictionary containing information on all Split user groups.
    """
    groups_dict = get_groups()
    all_users = get_all_users()
    groups_data = {}
    for group_id, group_name in groups_dict.items():
        group_users = []
        for user_name, user_data in all_users.items():
            for group in user_data['Groups']:
                if group['ID'] == group_id:
                    group_users.append(user_name)
                    break
        groups_data[group_name] = {"Group": group_name, "Users": group_users}
    save_cache()
    return groups_data
    

def get_splits():
    """
    Get data for all splits across all workspaces.

    Returns:
        A dictionary containing information on all splits, grouped by split name.
    """
    global cache_data
    if cache_data["splits"]:
        #print("Retrieving data from cache...")
        return cache_data["splits"]
    else:
        #print("Retrieving data from Split")
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
        cache_data["splits"] = splits
        save_cache()
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
    cache_key = f"split_def:{environment_id}:{workspace_id}:{split_def.id}"
    if cache_data["splits_definitions"] is None:
        cache_data["splits_definitions"] = {}
    if cache_key in cache_data["splits_definitions"]:
        return cache_data["splits_definitions"][cache_key]
    
    workspaces = get_workspaces()
    data = {
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

    cache_data["splits_definitions"][cache_key] = data
    save_cache()
    return data

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
    cache_key = f"split_defs:{environment_id}:{workspace_id}"
    if cache_data["splits_definitions"].get(cache_key):
        return cache_data["splits_definitions"][cache_key]

    definitions = {}
    for split_def in client.split_definitions.list(environment_id, workspace_id):
        split_name = split_def.name
        if split_name not in definitions:
            definitions[split_name] = [get_split_definition(environment_id, workspace_id, split_def)]
        else:
            definitions[split_name].append(get_split_definition(environment_id, workspace_id, split_def))
    cache_data["splits_definitions"].setdefault(cache_key, definitions)
    save_cache()
    return definitions

def get_all_splits_definitions():
    """
    Get all Split definitions across all workspaces and environments.

    Returns:
        A dictionary containing information on all Split definitions, grouped by Split name.
    """
    if cache_data["all_splits_definitions"]:
        return cache_data["all_splits_definitions"]
    
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
    cache_data["all_splits_definitions"] = definitions
    save_cache()
    return definitions
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
    segments_data = get_segments(include_keys=False)
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
def list_all_workspaces():
    """
    List all workspaces with their corresponding ID and name.

    Returns:
        Output to stdout.
    """
    workspaces = get_workspaces()
    print("List of workspaces:")
    for id, name in workspaces.items():
        print(f"ID: {id}, Name: {name}")
        
def list_all_environments():
    """
    Displays a list of all environments, including their ID, name, and workspace name.
    
    Returns:
        Output to stdout.
    """
    print("List of all environments:")
    for environment_id, environment_data in get_environments().items():
        print("-------------------------------------------")
        print(f"Name: {environment_data['Name']}")
        print(f"ID: {environment_id}")
        print(f"Workspace Name: {environment_data['Workspace Name']}")

def list_all_groups():
    """
    List all user groups.
    
    Returns:
        Output to stdout.
    """
    groups = get_groups()
    print("List of all groups\n------")
    for group_id, group_name in groups.items():
        print(f"ID: {group_id}")
        print(f"Name: {group_name}\n")

def list_all_segments():
    """
    List all segments with their names, IDs, environment names, and workspace names.

    Returns:
        Output to stdout.
    
    """
    segments = get_segments(include_keys=False)
    print("List of all segments\n------")
    for segment, segment_data in segments.items():
        print(f"Segment Name: {segment_data['Segment Name']}")
        print(f"Environment Name: {segment_data['Environment']['Name']}")
        print(f"Workspace Name: {segment_data['Workspace']['Name']}\n")

def list_all_splits():
    """
    List all splits with their corresponding ID, name, workspace ID, and workspace name.

    Returns:
        Output to stdout.
    """
    splits = get_splits()
    print("List of all splits:")
    for split_name, split_data in splits.items():
        for data in split_data:
            print("-------------------------------------------")
            print(f"Name: {split_name}")
            print(f"ID: {data['ID']}")
            print(f"Workspace Name: {data['Workspace Name']}")
            print(f"Workspace ID: {data['Workspace ID']}")

def list_all_users():
    """
    Lists all active Split users and their associated group memberships.

    Returns:
        Output to stdout.
    """
    users = get_all_users()
    print("List of all users\n------")
    for user_name, user_data in users.items():
        print(f"Name: {user_name}")
        print(f"Email: {user_data['Email']}")
        groups = ", ".join([group["Name"] for group in user_data["Groups"]])
        print(f"Groups: {groups}\n")
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
CACHE_FILE = ".split_cache.pkl"

def load_cache():
    """
    Loads cached data from a file if it exists, and populates the cache with data for all splits and segments
    if they are not already in the cache. The cache is then saved to a file.
    """
    global cache_data
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            cache_data = pickle.load(f)
    else:
        cache_data = {
            "workspaces": None,
            "workspace_data": None,
            "environments": None,
            "environments_data": None,
            "groups": None,
            "segments": None,
            "splits": None,
            "splits_definitions": {},
            "users": None,
            "all_splits_definitions": None
        }

    # Populate the cache with all_splits_definitions if it's not already in the cache
    if not cache_data["all_splits_definitions"]:
        print(f"First run of the script will populate the Split Definitions cache data for faster loading. Please wait...")
        cache_data["all_splits_definitions"] = get_all_splits_definitions()

    # Populate the cache with segments if they're not already in the cache
    if not cache_data["segments"]:
        print(f"First run of the script will populate the Segment cache data for faster loading. Please wait...")
        cache_data["segments"] = get_segments()
    save_cache()

def save_cache():
    """
    Saves the cache to a file.
    """
    global cache_data
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache_data, f)

load_cache() # Load the cache at the start of the script

def quit_tool():
    """
    Saves the cache and exits the script.
    """
    save_cache() # Save the cache before quitting the script
    print("Goodbye!")
    exit()
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
formatted_text_cache = {}

def format_text(text):
    """
    Replace underscores in the text with spaces and format the text to title case.

    Args:
        text: A string to be formatted.

    Returns:
        A formatted string in title case.
    """
    if text not in formatted_text_cache:
        formatted_text_cache[text] = re.sub('_', ' ', text).title()
    return formatted_text_cache[text]

formatted_options_cache = {}

def display_options(options, menu_name):
    """
    Display a list of options as a formatted menu.

    Args:
        options: A dictionary containing the menu options.
        menu_name: A string containing the name of the menu to display.

    Returns:
        Output to stdout.
    """
    if menu_name not in formatted_options_cache:
        formatted_options_cache[menu_name] = [
            f"{key}. {format_text(func.__name__)}"
            for key, func in options.items()
        ]
    print("----------------------------------------")
    print(f"PYTHON ADMIN API TOOL - {menu_name}")
    print("----------------------------------------")
    print("\n".join(formatted_options_cache[menu_name]))

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

def list():
    options = {
        "1": list_all_workspaces,
        "2": list_all_environments,
        "3": list_all_groups,
        "4": list_all_segments,
        "5": list_all_splits,
        "6": list_all_users,
        "7": main_menu,
        "8": quit_tool,
    }
    get_choice(options, "List")

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
        "2": list,
        "3": export_all_data,
        "4": operations,
        "5": quit_tool
    }
    get_choice(options, "Main")

if __name__ == '__main__':
    main_menu()