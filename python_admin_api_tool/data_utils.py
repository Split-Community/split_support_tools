import os
import cache 
import cache_utils
import logging
from tqdm import tqdm
from dotenv import load_dotenv
from splitapiclient.main import get_client

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
# Initialize the client connection

client = get_client({'apikey': API_KEY})

logger = logging.getLogger(__name__)

def configure_logging(debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

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
    
def get_environments():
    """
    Retrieve a dictionary of environment data

    Returns:
        dict: A dictionary of environment name, id, and workspace.
    """
    if cache.cache_data["environments"] is None:
        environments = {}
        workspaces = get_workspaces()
        total_workspaces = len(workspaces)

        with tqdm(total=total_workspaces, desc="Fetching environments", ncols=100) as pbar:
            for ws_id, ws_name in workspaces.items():
                for env in client.environments.list(ws_id):
                    environments[env.id] = {
                        "name": env.name,
                        "workspace": ws_name
                    }
                pbar.update(1)

        cache.cache_data["environments"] = environments
        cache_utils.save_cache()
    else:
        environments = cache.cache_data["environments"]

    return environments

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
    for ws_id, ws_name in tqdm(workspaces.items(), desc="Fetching environments", ncols=100, leave=False):
        environments = client.environments.list(ws_id)
        envs_for_ws = {}
        for env in environments:
            env_dict = {
                'workspaceId': env._workspace_id,
                'WorkspaceName': ws_name,
                'creationTime': env._creationTime,
                'production': env._production,
                'dataExportPermissions': {},
                'environmentType': env._type,
                'name': env._name,
                'changePermissions': {},
                'id': env._id,
                'status': env._status
            }
            if env._dataExportPermissions:
                env_dict['dataExportPermissions'] = {
                    'areExportersRestricted': env._dataExportPermissions.get('areExportersRestricted'),
                    'exporters': env._dataExportPermissions.get('exporters', [])
                }
            if env._changePermissions:
                env_dict['changePermissions'] = {
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

def get_segments():
    """
    Get all segments in all environments across all workspaces.

    Returns:
        A dictionary containing all segments, grouped by workspace.
    """
    if cache.cache_data['segments'] is not None:
        return cache.cache_data['segments']

    segments_data = {}

    for workspace_id, workspace_name in tqdm(get_workspaces().items(), desc="Fetching segments", ncols=100, leave=False):
        if workspace_name not in segments_data:
            segments_data[workspace_name] = {}

        for segment in client.segments.list(workspace_id):
            segment_info = {
                "name": segment.name,
                "description": segment.description,
                "trafficType": {
                    "id": segment._trafficType.id,
                    "name": segment._trafficType.name
                },
                "tags": [{"name": tag_name} for tag_name in (segment._tags if segment._tags is not None else [])],
                "creationTime": segment._creationTime
            }
            segments_data[workspace_name][segment.name] = segment_info

    cache.cache_data['segments'] = segments_data
    return segments_data

def get_segment_definitions(environment_id, workspace_id, environment_name, workspace_name):
    if cache.cache_data["segments_definitions"] is None:
        cache.cache_data["segments_definitions"] = {}
        
    cache_key = f"{workspace_name}:{environment_id}"
    if cache.cache_data["segments_definitions"].get(workspace_name, {}).get(cache_key):
        return cache.cache_data["segments_definitions"][workspace_name][cache_key]

    definitions = {}
    for segDef in client.segment_definitions.list(environment_id, workspace_id):
        segment_info = {
            "name": segDef.name,
            "environment": {
                "id": environment_id,
                "name": environment_name
            },
            "workspace": {
                "id": workspace_id,
                "name": workspace_name
            },
            "trafficType": {
                "id": segDef._trafficType._id,
                "name": segDef._trafficType._name
            },
            "creationTime": segDef._creationTime
        }

        segment_info["keys"] = client.segment_definitions.find(segDef.name, environment_id, workspace_id).get_keys()

        definitions[f"{segDef.name}.{environment_id}.{workspace_id}"] = segment_info

    cache.cache_data["segments_definitions"].setdefault(workspace_name, {}).setdefault(cache_key, definitions)
    cache_utils.save_cache()
    return definitions

def get_all_segments_definitions():
    if cache.cache_data["all_segments_definitions"]:
        return cache.cache_data["all_segments_definitions"]

    workspaces = get_workspaces()
    definitions = {}

    total_environments = sum(len(client.environments.list(workspace_id)) for workspace_id in workspaces)

    with tqdm(total=total_environments, desc="Fetching segment definitions", ncols=100) as pbar:
        for workspace_id, workspace_name in workspaces.items():
            for env in client.environments.list(workspace_id):
                segment_definitions = get_segment_definitions(env.id, workspace_id, env.name, workspace_name)
                for segment_key, segment_definition in segment_definitions.items():
                    definitions[segment_key] = segment_definition
                pbar.update(1)

    cache.cache_data["all_segments_definitions"] = definitions
    cache_utils.save_cache()
    return definitions

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
    statuses = ["ACTIVE", "DEACTIVATED", "PENDING"]
    for status in tqdm(statuses, desc="Fetching users", ncols=100, leave=False):
        for user in client.users.list(status):
            user_data = {
                "Type": user._type,
                "Name": user._name,
                "Email": user.email,
                "Status": user._status,
                "ID" : user._id,
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
    if cache.cache_data["splits"]:
        return cache.cache_data["splits"]
    else:
        workspaces = get_workspaces()
        splits = {}
        for workspace_id, workspace_name in tqdm(workspaces.items(), desc="Fetching splits", ncols=100, leave=False):
            for split in client.splits.list(workspace_id):
                split_data = split.to_dict()
                split_data["rolloutStatus"] = split._rolloutStatus
                split_data["trafficType"] = split._trafficType.to_dict()
                split_data["tags"] = split._tags
                split_data["owners"] = split._owners
                split_data["workspace_id"] = workspace_id
                split_data["workspace_name"] = workspace_name
                if split.name not in splits:
                    splits[split.name] = [split_data]
                else:
                    splits[split.name].append(split_data)
        cache.cache_data["splits"] = splits
        cache_utils.save_cache()
        return splits

def get_split_definitions(environment_id, workspace_id, workspace_name):
    """
    Get data for all Split definitions in a specific environment and workspace.

    Args:
        environment_id (str): ID of the environment to retrieve Split definitions from.
        workspace_id (str): ID of the workspace to retrieve Split definitions from.

    Returns:
        A dictionary containing information on all Split definitions, grouped by Split definition name.
        Each Split definition contains data on the definition's treatments, rules, and other attributes.

    """
    cache_key = f"{workspace_name}:{environment_id}"
    #if cache.cache_data["splits_definitions"].get(workspace_name, {}).get(cache_key):
        #return cache.cache_data["splits_definitions"][workspace_name][cache_key]
    if cache.cache_data["splits_definitions"].get(cache_key):
        return cache.cache_data["splits_definitions"][cache_key]

    definitions = {}
    for split_def in client.split_definitions.list(environment_id, workspace_id):
        split_name = split_def.name
        data = split_def.to_dict()
        data["workspace"] = workspace_name
        data["rules"] = [rule.export_dict() for rule in split_def._rules]
        data["defaultRule"] = [def_rule.export_dict() for def_rule in split_def._default_rule]
        data["treatments"] = [treatment.export_dict() for treatment in split_def._treatments]
        data["killed"] = split_def._killed
        data["defaultTreatment"] = split_def._default_treatment
        data["baselineTreatment"] = split_def._baseline_treatment
        data["trafficAllocation"] = split_def._traffic_allocation
        data["environment"] = {"id": split_def._environment.id, "name": split_def._environment.name}
        data["trafficType"] = split_def._trafficType.to_dict()
        data["creationTime"] = split_def._creationTime
        data["lastUpdateTime"] = split_def._lastUpdateTime

        definitions[f"{split_name}.{environment_id}.{workspace_id}"] = data
    #cache.cache_data["splits_definitions"].setdefault(cache_key, definitions)
    cache.cache_data["splits_definitions"][cache_key] = definitions
    cache_utils.save_cache()
    return definitions

def get_all_splits_definitions():
    if cache.cache_data["all_splits_definitions"]:
        return cache.cache_data["all_splits_definitions"]

    workspaces = get_workspaces()
    definitions = {}

    total_environments = sum(len(client.environments.list(workspace_id)) for workspace_id in workspaces)

    with tqdm(total=total_environments, desc="Fetching feature flags definitions", ncols=100) as pbar:
        for workspace_id, workspace_name in workspaces.items():
            for env in client.environments.list(workspace_id):
                split_definitions = get_split_definitions(env.id, workspace_id, workspace_name).values()
                for split_definition in split_definitions:
                    split_key = f"{split_definition['name']}.{env.id}.{workspace_id}"
                    definitions[split_key] = split_definition
                pbar.update(1)

    cache.cache_data["all_splits_definitions"] = definitions
    cache_utils.save_cache()
    return definitions

def get_all_splits_definitions_bk():
    """
    Get all Split definitions across all workspaces and environments.

    Returns:
        A dictionary containing information on all Split definitions, grouped by Split name.
    """
    if cache.cache_data["all_splits_definitions"]:
        return cache.cache_data["all_splits_definitions"]

    workspaces = get_workspaces()
    definitions = {}

    #total_workspaces = len(workspaces)
    total_environments = sum(len(client.environments.list(workspace_id)) for workspace_id in workspaces)

    with tqdm(total=total_environments, desc="Fetching split definitions", ncols=100) as pbar:
        for workspace_id, workspace_name in workspaces.items():
            for env in client.environments.list(workspace_id):
                #split_definitions = get_split_definitions(env.id, workspace_id, workspace_name)
                split_definitions = get_split_definitions(env.id, workspace_id, workspace_name).values()
                for split_key, split_definition in split_definitions:
                    definitions[split_key] = split_definition
                pbar.update(1)

    cache.cache_data["all_splits_definitions"] = definitions
    cache_utils.save_cache()
    return definitions