import os
import json
import csv
import readline
import re
import pprint
from collections import OrderedDict
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
    return [
        {
            "ID": ws.id,
            "Name": ws.name,
            "Requires Title And Comments": ws._requiresTitleAndComments,
        }
        for ws in client.workspaces.list()
    ]

def get_all_environments():
    """
    Fetches all environments in all workspaces and returns a list of environment dictionaries.
    """
    all_envs = []
    workspaces = get_workspaces()
    for ws_id, ws_name in workspaces.items():
        environments = client.environments.list(ws_id)
        for env in environments:
            env_dict = {
                'Workspace ID': ws_id,
                'Workspace Name': ws_name,
                'Creation Time': env._creationTime,
                'Production': env._production,
                'Data Export Permissions': env._dataExportPermissions,
                'Environment Type': env._type,  # Replace with the correct value
                'Name': env._name,
                'Change Permissions': env._changePermissions,
                'Type': 'environment',
                'ID': env._id,
                'Org ID': env._orgId,
                'Status': env._status,
            }
            all_envs.append(env_dict)
    return all_envs


def get_environments():
    return {env.id: env.name for ws_id, _ in get_workspaces().items() for env in client.environments.list(ws_id)}

def get_segments():
    segments_data = {}

    for workspace_id, workspace_name in get_workspaces().items():
        ws = client.workspaces.find(workspace_name)

        for env in client.environments.list(ws.id):
            for segDef in client.segment_definitions.list(env.id, ws.id):
                keys = segDef.get_keys()
                segments_data[segDef._name] = {
                    "Name": segDef._name,
                    "Environment": {
                        "id": env.id,
                        "name": env._name
                    },
                    "Traffic Type": {
                        "id": segDef._trafficType._id,
                        "name": segDef._trafficType._name
                    },
                    "Creation Time": segDef._creationTime,
                    "Keys": keys
                }

    return segments_data

def get_groups():
    return {group._id: group._name for group in client.groups.list()}

def get_all_users():    
    groups_dict = get_groups()
    return [
        {
            "ID": user.id,
            "Type": user._type,
            "Name": user._name,
            "Email": user.email,
            "Status": user._status,
            "Groups": [
                {
                    "type": group["type"],
                    "id": group["id"],
                    "name": groups_dict[group["id"]]
                }
                for group in user._groups
            ]
        }
        for user in client.users.list("ACTIVE")
    ]

def get_splits():
    workspaces = get_workspaces()
    splits = []
    for workspace_id, workspace_name in workspaces.items():
        for split in client.splits.list(workspace_id):
            split_data = {
                "Workspace": workspace_name,
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
            splits.append(split_data)
    return splits


def get_split_definitions(environment_id, workspace_id):
    definitions = []
    workspace_name = get_workspaces()[workspace_id]
    environment_name = get_environments()[environment_id]

    for split_def in client.split_definitions.list(environment_id, workspace_id):
        definition_data = split_def.to_dict()
        definition_data["Environment"] = {
            "ID": environment_id,
            "Name": environment_name
        }
        definition_data["Workspace"] = {
            "ID": workspace_id,
            "Name": workspace_name
        }
        definitions.append(definition_data)
    return definitions


def get_all_splits_definitions():
    workspaces = get_workspaces()
    environments = get_environments()
    definitions = []

    for workspace_id, workspace_name in workspaces.items():
        for environment_id, environment_name in environments.items():
            for split_def in client.split_definitions.list(environment_id, workspace_id):
                definition_data = split_def.to_dict()
                definition_data["Environment"] = {
                    "ID": environment_id,
                    "Name": environment_name
                }
                definition_data["Workspace"] = {
                    "ID": workspace_id,
                    "Name": workspace_name
                }
                definitions.append(definition_data)
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
    groups_data = [OrderedDict([("Group", group), ("Users", users)]) for group, users in users_data.items()]
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
                print(f"The workspace id is {ws.id} and name is {ws.name}")
            else:
                gr = client.groups.find(ws_or_gr_name)
                if not gr:
                    print(f"The workspace or group you entered does not exist. Please double check the name and try again")
                else:
                    groups_data = get_groups_users()
                    user_list = []
                    for group in groups_data:
                        if group['Group'] == ws_or_gr_name:
                            user_list = group['Users']

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
            all_envs = get_all_environments()
            for env in all_envs:
                if env['Name'] == env_name:
                    found_envs.append(env)
            if found_envs:
                print(f"Environment found with name: {env_name}")
                pprint.pprint(found_envs)

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
    segments_data = get_segments()

    if segment_name in segments_data:
        segment = segments_data[segment_name]
        print(f"Segment found with name: {segment_name}")
        print(f"Environment ID: {segment['Environment']['id']}")
        print(f"Environment Name: {segment['Environment']['name']}")
        print(f"Traffic Type ID: {segment['Traffic Type']['id']}")
        print(f"Traffic Type Name: {segment['Traffic Type']['name']}")
        print(f"Creation Time: {segment['Creation Time']}")
        print(f"Keys: {', '.join(segment['Keys'])}")
    else:
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


def search_splits_by_name(splits_data, split_name):
    for split in splits_data:
        if split['Name'] == split_name:
            split_data = {
                "workspace": split['Workspace'],
                "split_data": split
            }
            return split_data
    return None

def search_splits():
    splits = get_splits()
    while True:
        split_name = input("Enter the split name to search or 1 to go back to main Menu: ")
        if split_name == "1":
            search()
            break
        split_data = search_splits_by_name(splits, split_name)
        if split_data:
            print("Split found:")
            pprint.pprint(split_data)
        else:
            print("Split not found")

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

def export_data_to_json(data_type, data_getter, file_name_format):
    data = data_getter()
    with open(f"{data_type}.json", "w") as file:
        file.write(json.dumps(data, indent=4))

def export_data_to_csv(data_type, data_getter, file_extension, file_name_format):
    data = data_getter()
    if type(data) == dict:
        for name, d in data.items():
            with open(name + ".csv", "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=file_extension)
                writer.writeheader()
                if type(d) == dict:
                    if "objects" in d:
                        for item in d["objects"]:
                            writer.writerow(item)
                    else:
                        writer.writerow(d)
                else:
                    for item in d:
                        writer.writerow(item)
    elif type(data) == list:
        with open(data_type + ".csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=file_extension)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
    else:
        raise ValueError("Data type not supported")

def export_data(data_type, data_getter, file_extension=None, file_name_format=None):
    options = {
        "json": export_data_to_json,
        "csv": export_data_to_csv
    }
    choice = input("Enter the format you want the output in (json/csv): ")
    if choice not in options:
        print("Invalid choice")
        return
    if choice == "csv":
        options[choice](data_type, data_getter, file_extension, file_name_format)
    else:
        options[choice](data_type, data_getter, file_name_format)
    print(f"{data_type} data exported successfully!")


def export_splits():
    split_data = get_splits()
    export_data("splits", split_data, ["Workspace", "ID", "Name", "Description", "Traffic Type ID", "Traffic Type Name", "Creation Time", "Rollout Status ID", "Rollout Status Name", "Rollout Status Timestamp", "Tags", "Owners"], "{0}_splits")

def export_users():
    users = get_all_users()
    export_data("users", users, ["ID", "Type", "Name", "Email", "Status", "Groups"], "users",)

def export_workspaces():
    workspace_data = get_workspace_data()
    export_data("workspaces", workspace_data, ["ID", "Name", "Requires Title And Comments"], "{0}_workspaces")

def export_segments():
    export_data("segments", get_segments, ["Name", "Environment ID", "Environment Name", "Traffic Type ID", "Traffic Type Name", "Creation Time", "Keys"], "{0}_segments")

def export_groups():
    export_data("groups", get_groups_users, ["Group", "Users"], "{0}_groups")

def export_environments():
    export_data("environments", get_all_environments, [
        "Workspace ID", "Workspace Name", "Creation Time", "Production",
        "Data Export Permissions", "Environment Type", "Name", "Change Permissions",
        "Type", "ID", "Org ID", "Status"
    ], "environments")

def export_split_definitions():
    export_data("split_definitions", get_all_splits_definitions, [
        "Split Name", "Environment ID", "Environment Name", "creationTime", "killed", "name", "defaultTreatment", "lastTrafficReceivedAt", "rules", "defaultRule", "trafficType", "treatments", "trafficAllocation", "Environment", "Workspace", "lastUpdateTime", "environment", "baselineTreatment"
    ], "{0}_split_definitions")



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

#Method to display the menu
#New option can be added by adding new key to the options dictionary
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