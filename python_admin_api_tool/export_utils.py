import json
import data_utils
import csv
import logging

logger = logging.getLogger(__name__)

def configure_logging(debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

def export_treatment_keys_to_json(treatments, file_name):
    keys = []
    for treatment in treatments:
        if "keys" in treatment and treatment["keys"]:
            keys = [key for key in treatment["keys"]]
            break
    if keys:
        with open(file_name, "w") as file:
            file.write(json.dumps(keys, indent=4))
        print(f"Feature Flag's treatment keys exported successfully!")
    else:
        print(f"Keys are empty, no export")
        return

def export_treatment_keys_to_csv(treatments, file_name):
    """
    Exports treatment keys to CSV file.
    Returns:
        None
    """
    keys = []
    for treatment in treatments:
        if "keys" in treatment and treatment["keys"]:
            keys = [key for key in treatment["keys"]]
            break
    if keys:
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["keys"])
            for key in keys:
                writer.writerow([key])
        print(f"Split treatment rules exported to csv successfully!")
    else:
        print(f"Keys are empty, no export")
        return

def export_matcher_type_and_strings_to_json_bk(rules, file_name):
    if not rules:
        print("Rules are empty, no export.")
        return
    type_and_strings = []
    for rule in rules:
        for matcher in rule["condition"]["matchers"]:
            if "strings" in matcher:
                type_and_strings.append({"type": matcher["type"], "strings": matcher["strings"]})
            elif "string" in matcher:
                type_and_strings.append({"type": matcher["type"], "strings": [matcher["string"]]})
    with open(file_name, "w") as file:
        file.write(json.dumps(type_and_strings, indent=4))
        print(f"Feature Flag's treatment rules exported to json successfully!")

def export_matcher_type_and_strings_to_json(rules, file_name):
    if not rules:
        print("Rules are empty, no export.")
        return
    type_and_strings = []
    for rule in rules:
        for matcher in rule["condition"]["matchers"]:
            matcher_info = {"type": matcher["type"]}
            if "strings" in matcher:
                matcher_info["strings"] = matcher["strings"]
            elif "string" in matcher:
                matcher_info["strings"] = [matcher["string"]]
            elif "set" in matcher:
                matcher_info["set"] = [matcher["set"]]
            elif "depends" in matcher:
                matcher_info["depends"] = matcher["depends"]
            # Add other matcher types here
            type_and_strings.append(matcher_info)

    with open(file_name, "w") as file:
        file.write(json.dumps(type_and_strings, indent=4))
        print(f"Feature Flag's treatment rules exported to json successfully!")


def export_matcher_type_and_strings_to_csv(rules, file_name):
    """
    Exports treatment rules to CSV file.

    Returns:
        None
    """
    if not rules:
        print("Rules are empty, no export.")
        return
    type_and_strings = []
    for rule in rules:
        if "condition" not in rule:
            continue
        for matcher in rule["condition"]["matchers"]:
            matcher_info = {"type": matcher["type"]}
            if "strings" in matcher:
                matcher_info["strings"] = matcher["strings"]
            elif "string" in matcher:
                matcher_info["strings"] = [matcher["string"]]
            elif "depends" in matcher:
                matcher_info["depends"] = matcher["depends"]
            # Add other matcher types here
            type_and_strings.append(matcher_info)

    # Find the max number of rows
    max_rows = max([len(strings) for type_and_string in type_and_strings if "strings" in type_and_string for strings in type_and_string["strings"]])

    with open(file_name, "w", newline='') as file:
        csv_writer = csv.writer(file)
        # Write header
        headers = [f"{type_and_string['type']}_{idx}" for idx, type_and_string in enumerate(type_and_strings)]
        csv_writer.writerow(headers)
        for row_idx in range(max_rows):
            row = []
            for type_and_string in type_and_strings:
                if "strings" in type_and_string:
                    strings = type_and_string["strings"]
                    row.append(strings[row_idx] if row_idx < len(strings) else '')
                else:
                    row.append('')
            csv_writer.writerow(row)
    print(f"Split treatment rules exported to csv successfully!")

def export_split_definition_to_json(split_data, file_name):
    with open(file_name, "w") as file:
        file.write(json.dumps(split_data, indent=4))

def export_specific_split_definition(split_data):
    """
    Exports a specific split definition to a JSON file.

    Args:
        split_data (dict): The split definition data to be exported.

    Returns:
        None
    """
    split_name = split_data["name"]
    environment_name = split_data["environment"]["name"]
    workspace_name = split_data["workspace"]
    file_name = f"{split_name}.{environment_name}.{workspace_name}.json"

    print("Exporting feature flag definition, please wait...")
    export_split_definition_to_json(split_data, file_name)
    print(f"Feature flag definition for {split_name} in environment {environment_name} and workspace {workspace_name} exported successfully!")


def export_data_to_json(data_type, data_getter):
    data = data_getter()
    with open(data_type + "_data" + ".json", "w") as file:
        file.write(json.dumps(data, indent=4))


def export_data(data_type, data_getter):
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
    export_data_to_json(data_type, data_getter)
    print(f"{data_type} data exported successfully!")

def export_feature_flags():
    """
    Export all Split data as a JSON file with the name "{}_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("feature_flags", data_utils.get_splits)

def export_users():
    """
    Export all user data as a JSON file with the name "users_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("users", data_utils.get_all_users)

def export_workspaces():
    """
    Export all workspace data as a JSON file with the name "workspaces_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("workspaces", data_utils.get_workspace_data)

def export_segments_definitions():
    """
    Export all segment data as a JSON file with the name "segments_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("segments_definitions", data_utils.get_all_segments_definitions)

def export_groups():
    """
    Export all group data as a JSON file with the name "groups_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("groups", data_utils.get_groups_users)

def export_environments():
    """
    Export all environment data as a JSON file with the name "environments_data.json" to the current working directory.

    Returns:
        Output to stdout
    """
    export_data("environments", data_utils.get_environments_data)

def export_feature_flags_definitions():
    """
    Export all Split definition data as a JSON file with the name "split_definitions_data.json" to the current working 
    directory.

    Returns:
        Output to stdout
    """
    export_data("flag_definitions", data_utils.get_all_splits_definitions)