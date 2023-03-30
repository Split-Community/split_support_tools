import os
import json
import re
import pprint
from dotenv import load_dotenv
from splitapiclient.main import get_client

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
# Initialize the client connection

client = get_client({'apikey': API_KEY})

def get_workspaces():
    return {ws.id: ws.name for ws in client.workspaces.list()}

def get_workspace_data():
    return {
        ws.id: {
            "Name": ws.name,
            "Requires Title And Comments": ws._requiresTitleAndComments,
        }
        for ws in client.workspaces.list()
    }

def get_environments_data():
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
    return {env.id: env.name for ws_id, _ in get_workspaces().items() for env in client.environments.list(ws_id)}

def get_segments():
    segments_data = {}

    for workspace_id, workspace_name in get_workspaces().items():
        ws = client.workspaces.find(workspace_name)

        for env in client.environments.list(ws.id):
            for segDef in client.segment_definitions.list(env.id, ws.id):
                segments_data["Segment: " + segDef.name + " " + "in" + " " + "Environment: " + env._name] = {
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
    return {group._id: group._name for group in client.groups.list()}

def get_all_users():
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
        users[user._name] = user_data  # Use user's ID as the key
    return users

def get_splits():
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
    definitions = {}
    for split_def in client.split_definitions.list(environment_id, workspace_id):
        split_name = split_def.name
        if split_name not in definitions:
            definitions[split_name] = [get_split_definition(environment_id, workspace_id, split_def)]
        else:
            definitions[split_name].append(get_split_definition(environment_id, workspace_id, split_def))
    return definitions

def get_all_splits_definitions():
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


def quit_tool():
    print("Goodbye!")
    exit()
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
def search_workspaces_or_groups():
    while True:
        ws_or_gr_name = input("Enter the workspace or group name to search or 1 to go back to main Menu: ")
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
    while True:
        env_name = input("Enter the environment name to search or 1 to go back to main Menu: ")
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
                    print("-------------------")
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
    segment_name = input("Enter the name of the segment: ")
    print("Showing segments of the same name across all workspaces. This will take sometime, please wait...")
    segments_data = get_segments()
    found = False
    
    for key, segment in segments_data.items():
        if segment_name == segment['Name']:
            found = True
            print("-------------------------------------------")
            pprint.pprint(key)
            print("-------------------------------------------")
            print("Segment definition : ")
            pprint.pprint(segment)

    if not found:
        print(f"Segment not found with name {segment_name}")

def search_users():
    email = input("Enter the email of the user: ")
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
    all_definitions = get_all_splits_definitions()
    definitions = {split_name: []}

    if split_name in all_definitions:
        definitions[split_name] = all_definitions[split_name]

    return definitions

def search_splits():
    splits = get_splits()
    while True:
        split_name = input("Enter the split name to search or 1 to go back to main Menu: ")
        if split_name == "1":
            search()
            break
        elif split_name in splits:
            print("Splits found:")
            for split_data in splits[split_name]:
                print("-------------------------------------------")
                pprint.pprint(split_data)
            see_split_definitions = input("Do you want to see the split definitions for this split? (yes/no): ")
            print("This will show ")
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
    print("Exporting data, please wait...")
    export_data_to_json(data_type, data_getter, file_name_format)
    print(f"{data_type} data exported successfully!")

def export_splits():
    export_data("splits", get_splits, "{0}_splits")

def export_users():
    export_data("users", get_all_users, "{0}_users")

def export_workspaces():
    export_data("workspaces", get_workspace_data, "{0}_workspaces")

def export_segments():
    export_data("segments", get_segments, "{0}_segments")

def export_groups():
    export_data("groups", get_groups_users, "{0}_groups")

def export_environments():
    export_data("environments", get_environments_data, "{0}_environments")

def export_split_definitions():
    export_data("split_definitions", get_all_splits_definitions, "{0}_split_definitions")

def format_text(text):
    text = re.sub('_', ' ', text)
    return text.title()

def display_options(options):
    print("----------------------------------------")
    print("PYTHON ADMIN API TOOL")
    print("----------------------------------------")
    for key, value in options.items():
        print(f"{key}. {format_text(value)}")

def search():
    options = {
        "1": "search_workspaces_or_groups",
        "2": "search_environments",
        "3": "search_users",
        "4": "search_splits",
        "5": "search_segments",
        "6": "main_menu",
        "7": "quit_tool",
    }
    while True:
        display_options(options)
        choice = input(f"Enter your choice (1-{len(options)}): ")
        if choice in options:
            globals()[options[choice]]()
        elif choice == str(len(options)+1):
            return
        elif choice == str(len(options)+2):
            quit_tool()
        else:
            print("Invalid choice, try again")

def export_all_data():
    options = {
        "1": "export_groups",
        "2": "export_segments",
        "3": "export_splits",
        "4": "export_split_definitions",
        "5": "export_users",
        "6": "export_workspaces",
        "7": "export_environments",
        "8": "main_menu",
        "9": "quit_tool"
    }
    while True:
        display_options(options)
        choice = input(f"Enter your choice (1-{len(options)}): ")
        if choice in options:
            globals()[options[choice]]()
        elif choice == str(len(options)+1):
            return
        elif choice == str(len(options)+2):
            quit_tool()
        else:
            print("Invalid choice, try again")

def main_menu():
    options = {
        "1": "search",
        "2": "export_all_data",
        "3": "quit_tool"
    }

    while True:
        display_options(options)
        choice = input(f"Enter your choice (1-{len(options)}): ")
        if choice in options:
            globals()[options[choice]]()
        else:
            print("Invalid choice, try again")

if __name__ == '__main__':
    main_menu()