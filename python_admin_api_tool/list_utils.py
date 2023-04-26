import data_utils
import logging

logger = logging.getLogger(__name__)

def configure_logging(debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

def list_all_workspaces():
    
    """
    List all workspaces with their corresponding ID and name.

    Returns:
        Output to stdout.
    """
    workspaces = data_utils.get_workspaces()
    print("")
    print("List of workspaces:")
    print("-------------------------------------------")
    for id, name in workspaces.items():
        print(f"ID: {id}, Name: {name}")
        print("-------------------------------------------\n")

def list_all_environments():
    """
    Displays a list of all environments, including their ID, name, and workspace name.
    
    Returns:
        Output to stdout.
    """
    print("")
    print("List of all environments:")
    #print("-------------------------------------------")
    for environment_id, environment_data in data_utils.get_environments().items():
        print("-------------------------------------------")
        print(f"Name: {environment_data['name']}")
        print(f"ID: {environment_id}")
        print(f"Workspace Name: {environment_data['workspace']}")
    print("-------------------------------------------\n")

def list_all_groups():
    """
    List all user groups and their users.
    
    Returns:
        Output to stdout.
    """
    groups_data = data_utils.get_groups_users()
    print("")
    print("List of all groups\n")
    print("-------------------------------------------")
    for group_name, group_info in groups_data.items():
        print(f"Group: {group_info['Group']}")
        print("Users:")
        for user in group_info['Users']:
            print(f"  - {user}")
        print("------------------------------------------- \n")

def list_all_segments():
    """
    List all segments with their names, IDs, environment names, and workspace names.

    Returns:
        Output to stdout.
    
    """
    segments_definitions = data_utils.get_all_segments_definitions()
    print("")
    print("List of all segments\n")
    print("-------------------------------------------")
    for segment_key, segment_data in segments_definitions.items():
        print(f"Segment Name: {segment_data['name']}")
        print(f"Environment Name: {segment_data['environment']['name']}")
        print(f"Workspace Name: {segment_data['workspace']['name']}")
        print(f"keys in this Segment: {segment_data['keys']}")
        print("-------------------------------------------\n")

def list_all_feature_flags():
    """
    List all fflags with their corresponding ID, name, workspace ID, and workspace name.

    Returns:
        Output to stdout.
    """
    splits = data_utils.get_splits()
    print("")
    print("List of all feature flags:")
    for split_name, split_data in splits.items():
        for data in split_data:
            print("-------------------------------------------")
            print(f"Name: {split_name}")
            #print(f"ID: {data['id']}")
            print(f"Workspace Name: {data['workspace_name']}")
            print(f"Workspace ID: {data['workspace_id']}")
            print("------------------------------------------- \n")

def list_all_users():
    """
    Lists all active Split users and their associated group memberships.

    Returns:
        Output to stdout.
    """
    users = data_utils.get_all_users()
    print("List of all users\n------")
    for user_name, user_data in users.items():
        print(f"Name: {user_name}")
        print(f"Email: {user_data['Email']}")
        print(f"Status: {user_data['Status']}")
        groups = ", ".join([group["Name"] for group in user_data["Groups"]])
        print(f"Groups: {groups}")
        print("------------------------------------------- \n")