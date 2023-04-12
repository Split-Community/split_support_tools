import os
import cache 
import cache_utils
from dotenv import load_dotenv
from splitapiclient.main import get_client

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
    if cache.cache_data["workspaces"] is None:
        workspace_dict = {ws.id: ws.name for ws in client.workspaces.list()}
        cache.cache_data["workspaces"] = workspace_dict
        cache_utils.save_cache()
    else:
        workspace_dict = cache.cache_data["workspaces"]

    return workspace_dict

def get_workspace_data():
    """
    Retrieve a dictionary of workspace data, where the keys are the workspace IDs
    and the values are dictionaries containing workspace information such as
    name and whether title and comments are required.

    Returns:
        dict: A dictionary of workspace data.
    """
    if cache.cache_data["workspace_data"] is not None:
        return cache.cache_data["workspace_data"]
    else:
        workspace_data = {
            ws.id: {
                "Name": ws.name,
                "Requires Title And Comments": ws._requiresTitleAndComments,
            }
            for ws in client.workspaces.list()
        }
        cache.cache_data["workspace_data"] = workspace_data
        cache_utils.save_cache()
        return workspace_data

def get_environments_data():
    """
    Retrieve a dictionary containing information about all environments across all workspaces.

    Returns:
        dict: A dictionary with keys as workspace names and values as dictionaries containing information
        about all environments of the respective workspace.
    """

    if cache.cache_data['environments_data'] is not None:
        return cache.cache_data['environments_data']
    
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
    
    cache.cache_data['environments_data'] = all_envs
    cache_utils.save_cache()
    return all_envs

def get_environments():
    """
    Retrieve a dictionary of environment data

    Returns:
        dict: A dictionary of environment name, id, and workspace.
    """
    if cache.cache_data["environments"] is None:
        environments = {}
        for ws_id, ws_name in get_workspaces().items():
            for env in client.environments.list(ws_id):
                environments[env.id] = {
                    "Name": env.name,
                    "Workspace Name": ws_name
                }
        cache.cache_data["environments"] = environments
        cache_utils.save_cache() 
    else:
        environments = cache.cache_data["environments"]
    return environments

def get_segments(include_keys=True):
    """
    Get data for all segments in all environments across all workspaces.

    Args:
        include_keys (bool): Whether to include the segment keys or not. Defaults to True.

    Returns:
        A dictionary containing information on all segments, grouped by segment name and environment.
    """

    if cache.cache_data['segments'] is not None:
        return cache.cache_data['segments']

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

    cache.cache_data['segments'] = segments_data

    return segments_data

def get_groups():
    """
    Get all user groups.

    Returns:
        dict: A dictionary where the keys are the group IDs and the values are the group names.
    """
    if cache.cache_data["groups"] is not None:
        return cache.cache_data["groups"]

    groups = {group._id: group._name for group in client.groups.list()}
    cache.cache_data["groups"] = groups
    cache_utils.save_cache()

    return groups

def get_all_users():
    """
    Retrieves all active Split users and their associated group memberships.

    Returns:
        A dictionary where the keys are the user names and the values are dictionaries containing user information,
        including name, email, status, and a list of groups to which the user belongs.

    """
    if cache.cache_data["users"]:
        return cache.cache_data["users"]
    
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
    
    cache.cache_data["users"] = users
    cache_utils.save_cache()
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
    cache_utils.save_cache()
    return groups_data
    
def get_splits():
    """
    Get data for all splits across all workspaces.

    Returns:
        A dictionary containing information on all splits, grouped by split name.
    """
    #global cache.cache_data
    if cache.cache_data["splits"]:
        return cache.cache_data["splits"]
    else:
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
        cache.cache_data["splits"] = splits
        cache_utils.save_cache()
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
    if cache.cache_data["splits_definitions"] is None:
        cache.cache_data["splits_definitions"] = {}
    if cache_key in cache.cache_data["splits_definitions"]:
        return cache.cache_data["splits_definitions"][cache_key]
    
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

    cache.cache_data["splits_definitions"][cache_key] = data
    cache_utils.save_cache()
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
    if cache.cache_data["splits_definitions"].get(cache_key):
        return cache.cache_data["splits_definitions"][cache_key]

    definitions = {}
    for split_def in client.split_definitions.list(environment_id, workspace_id):
        split_name = split_def.name
        if split_name not in definitions:
            definitions[split_name] = [get_split_definition(environment_id, workspace_id, split_def)]
        else:
            definitions[split_name].append(get_split_definition(environment_id, workspace_id, split_def))
    cache.cache_data["splits_definitions"].setdefault(cache_key, definitions)
    cache_utils.save_cache()
    return definitions

def get_all_splits_definitions():
    #global cache.cache_data
    """
    Get all Split definitions across all workspaces and environments.

    Returns:
        A dictionary containing information on all Split definitions, grouped by Split name.
    """
    if cache.cache_data["all_splits_definitions"]:
        return cache.cache_data["all_splits_definitions"]
    
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
    cache.cache_data["all_splits_definitions"] = definitions
    cache_utils.save_cache()
    return definitions