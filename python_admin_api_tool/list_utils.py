import data_utils

def list_all_workspaces():
    """
    List all workspaces with their corresponding ID and name.

    Returns:
        Output to stdout.
    """
    workspaces = data_utils.get_workspaces()
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
    for environment_id, environment_data in data_utils.get_environments().items():
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
    groups = data_utils.get_groups()
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
    segments = data_utils.get_segments(include_keys=False)
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
    splits = data_utils.get_splits()
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
    users = data_utils.get_all_users()
    print("List of all users\n------")
    for user_name, user_data in users.items():
        print(f"Name: {user_name}")
        print(f"Email: {user_data['Email']}")
        groups = ", ".join([group["Name"] for group in user_data["Groups"]])
        print(f"Groups: {groups}\n")