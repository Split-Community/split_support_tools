import menu_utils
import data_utils
import os
import cache
import logging
import pprint
from dotenv import load_dotenv
from splitapiclient.main import get_client
from splitapiclient.util.exceptions import HTTPNotFoundError

logger = logging.getLogger(__name__)

def configure_logging(debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
# Initialize the client connection

client = get_client({'apikey': API_KEY})

def delete_groups():
    """
    Deletes a selected group and updates the cache.

    Returns: None
    """
    groups_data = data_utils.get_groups()
    while True:
        # Print available groups
        print("")
        print("Available groups:")
        print("-------------------------------------------\n")
        for idx, (group_id, group_name) in enumerate(groups_data.items(), start=1):
            print(f"{idx}. {group_name}")
        print("-------------------------------------------\n")
        group_idx_input = input("Select the group to delete (0 to go back to previous menu): ")
        if group_idx_input == "0":
            menu_utils.operations()
            break

        group_idx = int(group_idx_input) - 1
        group_id, group_name = list(groups_data.items())[group_idx]

        # Confirm deletion
        print("-------------------------------------------\n")
        confirm = input(f"Are you sure you want to delete '{group_name}'? (yes/no): ")
        if confirm.lower() in ["yes", "y"]:
            try:
                deleted = client.groups.delete_group(group_id)
            except Exception as e:
                deleted = False
                print(f"Error: {str(e)}")
            if deleted:
                print(f"'{group_name}' has been deleted.")
                print(f"Refreshing cache")
                cache.cache_data["groups"] = None
                groups_data = data_utils.get_groups()
            else:
                print(f"Failed to delete '{group_name}'.")
        else:
            print("Deletion cancelled")

def delete_segments():
    """
    Deletes a selected segment from a chosen workspace and updates the cache.

    Returns: None
    """
    segments_data = data_utils.get_segments()

    while True:
        # Print available workspaces
        print("")
        print("Available workspaces:")
        print("-------------------------------------------\n")
        for idx, workspace_name in enumerate(segments_data.keys(), start=1):
            print(f"{idx}. {workspace_name}")
        print("-------------------------------------------\n")
        ws_idx_input = input("Select the workspace from the list (0 to go back to the previous menu): ")
        if ws_idx_input == "0":
            menu_utils.operations()
            break

        ws_idx = int(ws_idx_input) - 1
        ws_name = list(segments_data.keys())[ws_idx]

        while True:
            # Print available segments for the selected workspace
            print("")
            print("Available segments for the selected workspace:")
            print("-------------------------------------------\n")
            segments = list(segments_data[ws_name].keys())
            for idx, segment_name in enumerate(segments, start=1):
                print(f"{idx}. {segment_name}")
            print("-------------------------------------------\n")
            segment_idx_input = input("Select the segment to delete (0 to go back to the previous menu): ")
            if segment_idx_input == "0":
                break

            segment_idx = int(segment_idx_input) - 1
            segment_name = segments[segment_idx]

            # Confirm deletion
            confirm = input(f"Are you sure you want to delete '{segment_name}'? (yes/no): ")
            if confirm.lower() in ["yes", "y"]:
                ws = client.workspaces.find(ws_name)
                deleted = ws.delete_segment(segment_name)
                if deleted:
                    print(f"'{segment_name}' has been deleted.")
                    print(f"Refreshing cache")
                    cache.cache_data["segments"] = None
                    segments_data = data_utils.get_segments()
                else:
                    print(f"Failed to delete '{segment_name}'.")
            else:
                print("Deletion cancelled")

def delete_feature_flags():
    """
    Deletes a selected feature flag from a chosen workspace and updates the cache.

    Returns: None
    """
    workspaces = data_utils.get_workspaces()
    all_splits = data_utils.get_splits()

    while True:
        # Print available workspaces
        print("")
        print("Available workspaces:")
        print("-------------------------------------------\n")
        for idx, (ws_id, ws_name) in enumerate(workspaces.items(), start=1):
            print(f"{idx}. {ws_name}")
        print("-------------------------------------------\n")

        ws_idx_input = input("Select the workspace from the list (0 to go back to the previous menu): ")
        if ws_idx_input == "0":
            menu_utils.operations()
            break

        ws_idx = int(ws_idx_input) - 1
        ws_id, ws_name = list(workspaces.items())[ws_idx]

        while True:
            print("")
            print("Available feature flags for the selected workspace:")
            print("-------------------------------------------\n")
            splits = [
                split_name.split(".")[0]
                for split_name, split_data_list in all_splits.items()
                for split_data in split_data_list
                if split_data["workspace_name"] == ws_name
            ]
            splits = list(set(splits))
            splits.sort()
            for idx, split_name in enumerate(splits, start=1):
                print(f"{idx}. {split_name}")
            print("-------------------------------------------\n")

            split_idx_input = input("Select the feature flag to delete from the (0 to go back to the previous menu): ")
            if split_idx_input == "0":
                break

            split_idx = int(split_idx_input) - 1
            split_name = splits[split_idx]

            # Confirm deletion
            confirm = input(f"Are you sure you want to delete '{split_name}'? (yes/no): ")
            if confirm.lower() in ["yes", "y"]:
                ws = client.workspaces.find(ws_name)
                deleted = ws.delete_split(split_name)
                if deleted:
                    print(f"'{split_name}' has been deleted.")
                    print(f"Refreshing cache")
                    cache.cache_data["splits"] = None
                    all_splits = data_utils.get_splits()
                else:
                    print(f"Failed to delete '{split_name}'.")
            else:
                print("Deletion cancelled")

def delete_environments():
    environments_data = data_utils.get_environments_data()
    workspaces = [name for name in environments_data.keys()]
    workspaces.sort()

    print("Workspaces:")
    for i, ws_name in enumerate(workspaces, start=1):
        print(f"{i}. {ws_name}")

    ws_choice = int(input("Select the workspace containing the environment to delete: ")) - 1
    selected_ws_name = workspaces[ws_choice]
    selected_ws_envs = environments_data[selected_ws_name]
    
    env_names = [env['name'] for env in selected_ws_envs.values()]
    env_names.sort()

    print("Environments:")
    for i, env_name in enumerate(env_names, start=1):
        print(f"{i}. {env_name}")

    env_choice = int(input("Select the environment to delete: ")) - 1
    selected_env_name = env_names[env_choice]
    selected_env = selected_ws_envs[selected_env_name]

    env_name = selected_env['name']
    ws_id = selected_env['workspaceId']

    confirm = input(f"Are you sure you want to delete the environment '{selected_env_name}'? (yes/no): ")

    if confirm.lower() in ["yes", "y"]:
        try:
            deleted = client.environments.delete(env_name, ws_id)
        except HTTPNotFoundError as e:
            deleted = False
            error_message = e
            print(f"Error: {error_message}")
        except Exception as e:
            deleted = False
            print(f"Error: {str(e)}")

        if deleted:
            print(f"Environment '{selected_env_name}' deleted successfully.")
            # Update cache after successful deletion
            cache.cache_data["environments"] = None
            cache.cache_data["environments_data"] = None
        else:
            print(f"Failed to delete environment '{selected_env_name}'.")

def copy_feature_flag_definitions():
    """
    Copy definitions from one feature flag to another

    Returns: None
    """
    workspaces = data_utils.get_workspaces()
    environments = data_utils.get_environments()
    #cache.cache_data["all_splits_definitions"] = None
    all_splits_definitions = data_utils.get_all_splits_definitions()
    exit = False
    try: 
        while not exit:
            # Workspace selection loop
            while True:
                # Print available workspaces
                print("")
                print("Available workspaces:")
                print("")
                print("-------------------------------------------\n")
                for idx, (ws_id, ws_name) in enumerate(workspaces.items(), start=1):
                    print(f"{idx}. {ws_name}")
                print("-------------------------------------------\n")
                source_ws_idx = int(input("Select the source workspace (0 to go back to the previous menu): ")) - 1

                if source_ws_idx == -1:
                    menu_utils.operations()
                    exit = True
                    break
                source_ws_id, source_ws_name = list(workspaces.items())[source_ws_idx]
                updated = False
                while not updated:
                # Print available environments for the source workspace
                    print("")
                    print("Available environments for the source workspace:")
                    print("-------------------------------------------\n")
                    source_env_options = {env_id: env_data for env_id, env_data in environments.items() if env_data["workspace"] == source_ws_name}
                    for idx, (env_id, env_data) in enumerate(source_env_options.items(), start=1):
                        print(f"{idx}. {env_data['name']}")
                    print("-------------------------------------------\n")
                    source_env_idx = int(input("Select the source environment by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                    if source_env_idx == -1:
                        break
                    source_env_id, source_env_data = list(source_env_options.items())[source_env_idx]
                    source_environment_name = source_env_data["name"]
                    
                    while not updated:
                        # Get split names for the source workspace and environment
                        source_splits = [
                            split_key.split(".")[0]  # Modify this line
                            for split_key, split_definition in all_splits_definitions.items()
                            if split_definition["workspace"] == source_ws_name and split_definition["environment"]["name"] == source_environment_name
                        ]
                        print("")
                        print("Available feature flags for the source workspace and environment:")
                        print("-------------------------------------------\n")
                        for idx, split_name in enumerate(source_splits, start=1):
                            print(f"{idx}. {split_name}")
                        print("-------------------------------------------\n")
                        # Get source split name
                        source_split_idx = int(input("Select the source feature flag by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                        if source_split_idx == -1:
                            break
                        source_split_name = source_splits[source_split_idx]
                        
                        # Search for the source split definition
                        source_split_def = None
                        for split_key, split_definition in all_splits_definitions.items():
                            split_name, _, _ = split_key.split(".")
                            if (split_name == source_split_name and
                                    split_definition["workspace"] == source_ws_name and
                                    split_definition["environment"]["name"] == source_environment_name):
                                source_split_def = split_definition
                                break
                        if not source_split_def:
                            print("Source feature flag definition not found.")
                            break
                        else:
                            print("This is the definition of the chosen Split: ")
                            pprint.pprint(source_split_def)
                            continue_input = input("is this the definition you want? (yes/no) : ").lower()
                            if continue_input not in ["yes", "y"]:
                                break

                        while not updated:
                            # Print workspace options for target
                            print("")
                            print("Select the target workspace: ")
                            print("-------------------------------------------\n")
                            for idx, (ws_id, ws_name) in enumerate(workspaces.items(), start=1):
                                print(f"{idx}. {ws_name}")
                            print("-------------------------------------------\n")
                            # Get target workspace
                            try:
                                target_ws_idx = int(input("Select the target workspace by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                            except ValueError:
                                print("Invalid input. Please enter a number.")
                                continue

                            if target_ws_idx == -1:
                                break
                            elif 0 <= target_ws_idx < len(workspaces):
                                target_ws_id, target_ws_name = list(workspaces.items())[target_ws_idx]
                            else:
                                print("Invalid number. Please enter a number from the list.")
                                break

                            target_ws_id, target_ws_name = list(workspaces.items())[target_ws_idx]
                        
                            while not updated:
                                # Print available environments for the target workspace
                                print("")
                                print("Available environments for the target workspace:")
                                print("-------------------------------------------\n")
                                target_env_options = {env_id: env_data for env_id, env_data in environments.items() if env_data["workspace"] == target_ws_name}
                                for idx, (env_id, env_data) in enumerate(target_env_options.items(), start=1):
                                    print(f"{idx}. {env_data['name']}")
                                print("-------------------------------------------\n")
                                # Get target environment
                                target_env_idx = int(input("Select the target environment by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                                if target_env_idx == -1 or updated:
                                    break
                                target_env_id, target_env_data = list(target_env_options.items())[target_env_idx]
                                target_environment_name = target_env_data["name"]
                            # Create a new split definition dictionary with only the necessary keys
                                split_definition = {
                                "treatments": list(source_split_def["treatments"]),
                                "defaultTreatment": source_split_def["defaultTreatment"],
                                "rules": source_split_def["rules"],
                                "defaultRule": source_split_def["defaultRule"],
                                "trafficAllocation" : source_split_def["trafficAllocation"]
                                }
                                target_splits = [
                                        split_key.split(".")[0]  # Modify this line
                                        for split_key, split_definition in all_splits_definitions.items()
                                        if split_definition["workspace"] == target_ws_name and split_definition["environment"]["name"] == target_environment_name
                                    ]
                                
                                while not updated:
                                    if not target_splits:
                                        print("")
                                        print(f"there is no feature flag definition for this environment. Before copying please make sure to create a feature flag definition first. \n")
                                        break
                                    print("")
                                    print("Available feature flag for the target workspace and environment: \n")
                                    print("-------------------------------------------\n")
                                    for idx, split_name in enumerate(target_splits, start=1):
                                        print(f"{idx}. {split_name}")
                                    print("-------------------------------------------\n")
                                    # Get target split name
                                    target_split_idx = int(input("Select the target feature flag by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                                    if target_split_idx == -1 or updated:
                                        break
                                    target_split_name = target_splits[target_split_idx]
                                    #dest_workspace = client.workspaces.find(target_ws_name)

                                    target_split_def = client.split_definitions.find(target_split_name, target_env_id, target_ws_id)
                                    update_check = target_split_def.update_definition(split_definition)
                                    if update_check:
                                        print("")
                                        print(f"Copied definition from feature flag {source_split_name} in Workspace {source_ws_name}, Environment: {source_environment_name} to feature flag {target_split_name} in Workspace: {target_ws_name}, Environment: {target_environment_name} \n")
                                    else:
                                        print(f"Copying feature flag definition unsuccessful, enable debug logging (--debug) for more info \n")
                                    updated = True
                                    break
    except Exception as e:
        print(f"An error occurred: {e}")

def copy_segment_definitions():
    """
    Copy segment keys from a segment to another segment.

    Returns: None
    """
    workspaces = data_utils.get_workspaces()
    environments = data_utils.get_environments()
    all_segments_definitions = data_utils.get_all_segments_definitions()
    updated = False
    exit = False
    try: 
        while not exit:
            # Workspace selection loop
            while True:
                # Print available workspaces
                print("")
                print("Available workspaces:")
                print("-------------------------------------------\n")
                for idx, (ws_id, ws_name) in enumerate(workspaces.items(), start=1):
                    print(f"{idx}. {ws_name}")
                print("-------------------------------------------\n")
                source_ws_idx = int(input("Select the source workspace by entering the corresponding number (0 to quit): ")) - 1
                if source_ws_idx == -1:
                    exit = True
                    menu_utils.operations
                    break
                source_ws_id, source_ws_name = list(workspaces.items())[source_ws_idx]
        
                updated = False
                while not updated:
                    # Print available environments for the source workspace
                    print("")
                    print("Available environments for the source workspace:")
                    print("-------------------------------------------\n")
                    source_env_options = {env_id: env_data for env_id, env_data in environments.items() if env_data["workspace"] == source_ws_name}
                    for idx, (env_id, env_data) in enumerate(source_env_options.items(), start=1):
                        print(f"{idx}. {env_data['name']}")
                    print("-------------------------------------------\n")
                    source_env_idx = int(input("Select the source environment by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                    if source_env_idx == -1:
                        break
                    source_env_id, source_env_data = list(source_env_options.items())[source_env_idx]
                    source_environment_name = source_env_data["name"]

                    while not updated:
                    # Get segment names for the source workspace and environment
                        source_segments = [
                            segment_key.split(".")[0]
                            for segment_key, segment_definition in all_segments_definitions.items()
                            if segment_definition["workspace"]["id"] == source_ws_id and segment_definition["environment"]["id"] == source_env_id
                        ]
                        print("")
                        print("Available segments for the source workspace and environment:")
                        print("-------------------------------------------\n")
                        for idx, segment_name in enumerate(source_segments, start=1):
                            print(f"{idx}. {segment_name}")
                        print("-------------------------------------------\n")

                        # Get source segment name
                        source_segment_idx = int(input("Select the source segment by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                        if source_segment_idx == -1:
                            break
                        source_segment_name = source_segments[source_segment_idx]
                        source_segment_key = f"{source_segment_name}.{source_env_id}.{source_ws_id}"
                        selected_segment_definition = all_segments_definitions[source_segment_key]
                        segment_keys = selected_segment_definition["keys"]

                        print("")
                        print(f"Keys for the selected source segment '{source_segment_name}':")
                        for idx, key in enumerate(segment_keys, start=1):
                            print(f"{idx}. {key}")
                        
                        continue_input = input("is this the definition you want? (yes/no) : ").lower()
                        if continue_input not in ["yes", "y"]:
                            break
                        while not updated:
                            # Print workspace options for target
                            print("")
                            print("Select the target workspace: ")
                            print("-------------------------------------------\n")
                            for idx, (ws_id, ws_name) in enumerate(workspaces.items(), start=1):
                                print(f"{idx}. {ws_name}")
                            print("-------------------------------------------\n")
                            # Get target workspace
                            target_ws_idx = int(input("Select the target workspace by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                            target_ws_id, target_ws_name = list(workspaces.items())[target_ws_idx]
                            
                            if target_ws_idx == -1:
                                break
                            while not updated:
                                # Print available environments for the target workspace
                                print("")
                                print("Available environments for the target workspace:")
                                print("-------------------------------------------\n")
                                target_env_options = {env_id: env_data for env_id, env_data in environments.items() if env_data["workspace"] == target_ws_name}
                                for idx, (env_id, env_data) in enumerate(target_env_options.items(), start=1):
                                    print(f"{idx}. {env_data['name']}")
                                print("-------------------------------------------\n")
                                # Get target environment
                                target_env_idx = int(input("Select the target environment by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                                target_env_id, target_env_data = list(target_env_options.items())[target_env_idx]
                                target_environment_name = target_env_data["name"]

                                if target_env_idx == -1:
                                    break
                                while not updated:
                                    # Get segment names for the target workspace and environment
                                    target_segments = [
                                        segment_key.split(".")[0]
                                        for segment_key, segment_definition in all_segments_definitions.items()
                                        if segment_definition["workspace"]["name"] == target_ws_name and segment_definition["environment"]["name"] == target_environment_name
                                    ]
                                    if not target_segments:
                                        print("There is no segment definition for this environment, please choose again or create a segment definition first.")
                                        break
                                    print("")
                                    print("Available segments for the target workspace and environment:")
                                    print("-------------------------------------------\n")
                                    for idx, segment_name in enumerate(target_segments, start=1):
                                        print(f"{idx}. {segment_name}")
                                    print("-------------------------------------------\n")

                                    # Get target segment name
                                    target_segment_idx = int(input("Select the target segment by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                                    target_segment_name = target_segments[target_segment_idx]
                                    if target_segment_idx == -1:
                                        break
                                    # Copy segment definitions
                                    target_segment_def = client.segment_definitions.find(target_segment_name, target_env_id, target_ws_id)

                                    keys = client.segment_definitions.find(source_segment_name, source_env_id, source_ws_id).get_keys()
                                    update_check = target_segment_def.import_keys_from_json("false", {"keys": keys, "comment": "copy keys from segment"})

                                    if update_check:
                                        print("")
                                        print(f"Segment keys copied from Segment {source_segment_name} in workspace: {source_ws_name} - environemnt: {source_environment_name} to Segment {target_segment_name} in workspace : '{target_ws_name}' - environment : {target_environment_name}' \n")
                                        updated = True
                                        break
    except Exception as e:
        print(f"An error occurred: {e}")

def export_segments_keys():
    """
    Export the keys for a chosen segment.

    Returns: None
    """
    workspaces = data_utils.get_workspaces()
    environments = data_utils.get_environments()
    all_segments_definitions = data_utils.get_all_segments_definitions()
    exit = False
    try: 
        while not exit:
            # Workspace selection loop
            while True:
                # Print available workspaces
                print("")
                print("Available workspaces:")
                print("-------------------------------------------\n")
                for idx, (ws_id, ws_name) in enumerate(workspaces.items(), start=1):
                    print(f"{idx}. {ws_name}")
                print("-------------------------------------------\n")

                source_ws_idx = int(input("Select the source workspace by entering the corresponding number (0 to quit): ")) - 1
                if source_ws_idx == -1:
                    exit = True
                    menu_utils.operations
                    break
                source_ws_id, source_ws_name = list(workspaces.items())[source_ws_idx]
                updated = False    
                # Environment selection loop
                while not updated:
                    # Print available environments for the source workspace
                    print("")
                    print("Available environments for the source workspace:")
                    print("-------------------------------------------\n")
                    source_env_options = {env_id: env_data for env_id, env_data in environments.items() if env_data["workspace"] == source_ws_name}
                    for idx, (env_id, env_data) in enumerate(source_env_options.items(), start=1):
                        print(f"{idx}. {env_data['name']}")
                    print("-------------------------------------------\n")

                    source_env_idx = int(input("Select the source environment by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                    if source_env_idx == -1:
                        break
                    source_env_id, source_env_data = list(source_env_options.items())[source_env_idx]
                    source_environment_name = source_env_data["name"]

                    while not updated:
                    # Get segment names for the source workspace and environment
                        source_segments = [
                            segment_key.split(".")[0]
                            for segment_key, segment_definition in all_segments_definitions.items()
                            if segment_definition["workspace"]["id"] == source_ws_id and segment_definition["environment"]["id"] == source_env_id
                        ]

                        print("")
                        print("Available segments for the source workspace and environment:")
                        print("-------------------------------------------\n")
                        for idx, segment_name in enumerate(source_segments, start=1):
                            print(f"{idx}. {segment_name}")
                        print("-------------------------------------------\n")

                        # Get source segment name
                        source_segment_idx = int(input("Select the Segment by entering the corresponding number (0 to go back to the previous menu): ")) - 1
                        if source_segment_idx == -1:
                            break

                        source_segment_name = source_segments[source_segment_idx]
                        source_segment_key = f"{source_segment_name}.{source_env_id}.{source_ws_id}"
                        selected_segment_definition = all_segments_definitions[source_segment_key]
                        segment_keys = selected_segment_definition["keys"]

                        print("")
                        print(f"Keys for the selected source segment '{source_segment_name}':")
                        print("-------------------------------------------\n")
                        for idx, key in enumerate(segment_keys, start=1):
                            print(f"{idx}. {key}")
                        print("-------------------------------------------\n")
                        #export_keys_option = input("Do you want to export keys under this segment? (yes/no): ")
                        #if export_keys_option.lower() == "yes" or export_keys_option.lower() == "y":
                        file_name = f"segment-{source_segment_name}.{source_environment_name}.{source_ws_name}"
                        segDef = client.segment_definitions.find(segment_name, source_env_id, source_ws_id)
                        segDef.export_keys_to_csv(f"{file_name}_keys.csv")
                        print(f"keys are exported to {file_name}_keys.csv")
                        updated = True
                        break
    except Exception as e:
        print(f"An error occurred: {e}")
