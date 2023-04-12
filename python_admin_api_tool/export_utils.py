import json
import data_utils

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
    export_data("splits", data_utils.get_splits, "{0}_splits")

def export_users():
    """
    Export all user data as a JSON file with the name "users_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("users", data_utils.get_all_users, "{0}_users")

def export_workspaces():
    """
    Export all workspace data as a JSON file with the name "workspaces_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("workspaces", data_utils.get_workspace_data, "{0}_workspaces")

def export_segments():
    """
    Export all segment data as a JSON file with the name "segments_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("segments", data_utils.get_segments, "{0}_segments")

def export_groups():
    """
    Export all group data as a JSON file with the name "groups_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("groups", data_utils.get_groups_users, "{0}_groups")

def export_environments():
    """
    Export all environment data as a JSON file with the name "environments_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("environments", data_utils.get_environments_data, "{0}_environments")

def export_split_definitions():
    """
    Export all Split definition data as a JSON file with the name "split_definitions_data.json" to the current working 
    directory.

    Returns:
        Output to stdout
    """
    export_data("split_definitions", data_utils.get_all_splits_definitions, "{0}_split_definitions")
