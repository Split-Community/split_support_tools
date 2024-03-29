## Overview

This Python tool utilizes Split's [Python PyPi library for Split REST Admin API](https://help.split.io/hc/en-us/articles/4412331052685-Python-PyPi-library-for-Split-REST-Admin-API)

With the Python Admin API command-line interface, (CLI), you can:
   - Search for workspaces, environments, groups, users, feature flags, and segments.
   - List all workspaces, environments, groups, users, feature flags, and segments.
   - Export detailed definitions to JSON and optionally convert to CSV
   - Copy (clone) feature flags and segments
   - Delete groups, segments, and feature flags.

## Setting up

1. If you don’t have Python 3 installed, [install it from here](https://www.python.org/downloads/)
- Please note that on MacOS, the python command is `python3`
- You can run the following command to create the alias for python
```
echo "alias python=python3\nalias pip=pip3" >> ~/.zprofile

source ~/.zprofile
```
- Now your `python` command on MacOS will run python3.

2. Clone this repository and go into it

```bash
git clone git@github.com:Split-Community/split_support_tools.git

cd split_support_tools/python_admin_api_tool/
```

3. Create a new virtual environment

```bash
python -m venv venv

source venv/bin/activate
```

4. Install the requirements

```bash
pip install -r requirements.txt
```

5. Make a copy of the example environment variables file

```bash
cp env_sample .env
```

6. Add your [Admin API key](https://help.split.io/hc/en-us/articles/360019916211-API-keys#adding-admin-api-keys) to the newly created `.env` file
- Note that it's recommended to use an API key that is scoped across all environments and workspaces
- If the environment/workspace has access restrictions, you might encounter an error.

7. Run the tool

```bash
python admin_api_tool.py
```
or on MacOS

```bash
python3 admin_api_tool.py
```

## Caching
- To reduce API calls and improve response time, the script caches feature flag definitions and segments definitions on the first run if there is no cache data. Other data will be cached on the first use.

#### Note: If you make changes to your feature flags, it's recommended that you update the cache using the Update Cache option.

## Usage:
The menu is straightforward with the options. There are 5 choices: 
- Search
- List
- Export
- Operations
- Update Cache.

## Search
- The Search options are:

```
1. Search Workspaces Or Groups
   - This searches for the name of the workspaces or the groups in your org.

2. Search Environments
   - This searches for all the environments of the same name across all workspaces.

3. Search Users
   - Requires the email of the users being searched. Will show information of the user and which group they are in.

4. Search Feature Flags
   - This searches for all feature flags of the same name across all workspaces and environments.
   - When a feature flag is found, the user can choose to export the following:
      * This feature flag's definition from a specific environment to json
      * The treatment keys to csv/json
      * The list of the targeting rules to csv/json

5. Search Segments
   - This searches for all segments of the same name across all workspaces and environments, and will also display all the keys of the segments.
   - When a segment is found, the user can choose to export the following:
      * The segment keys to csv
```

## List
- The List options are self-explanatory. Note that these do not show the full details (such as feature flag definitions or segment keys), please use the Export functions to get the full data.

```
1. List all workspaces
   - List all workspaces in the org.

2. List all environments
   - List all environments across all workspaces.

3. List all groups
   - List all the groups and the list of users.

4. List all segments
   - List all the segments and keys of each for all environments and workspaces.

5. List all feature flags
   - List all the feature flags across all workspaces, will not show feature flag definitions (use the export option for the definitions).

6. List all users
   - List all users and their statuses.
```

## Export
- The Export options are straightforward. By default, all exports are json format. 

Also refer to the Additional tool (JSON to CSV converter) for more information.

```
1. Export environments
   - This exports all environments across all workspaces.

2. Export groups
   - This exports all groups and the users in each group.

3. Export segments definitions
   - This exports all segments definitions across all workspaces and environments.

4. Export segments keys
   - This lets the user choose the workspace, environment, the segment, and export all the keys.

5. Export feature flag definitions
   - This exports all feature flag definitions across all workspaces and environments.

6. Export feature flag
   - This exports all feature flags (not the definitions) across all workspaces and environments.

7. Export users
   - This exports all the users and their statuses, as well as group memberships.

8. Export workspaces
   - This exports all workspaces in your org.
```

## Operations
- The Operations mutates or changes your feature flags/segments/workspaces/environments. More options will be added over time.

```
1. Copy segment definitions
   - This allows for copying the keys of one segment to another segment. Users can choose from available lists of workspaces, environments, and segments to copy.

2. Copy feature flag definitions
   - This allows for copying the definitions of one feature flag to another. Users can choose from available lists of workspaces, environments, and feature flags to copy.

3. Delete groups
   - This forcefully deletes the group in the workspace you specified, regardless of the definitions. Note that this is not reversible!

4. Delete segments
   - This forcefully deletes the segment in the workspace you specified, regardless of the definitions. Note that this is not reversible!

5. Delete feature flags
   - This forcefully deletes the feature flag in the workspace you specified, regardless of the definitions. Note that this is not reversible!
```

## Update Cache

It's recommended to run this option after you have made changes to the feature flags or segments to ensure the latest data.


## DEBUG Logging:
If you run into issues, you can run the script with debug logging enabled for better troubleshooting:

```bash
python admin_api_tool.py --debug
```

## Additional tool (JSON to CSV converter)
You can use the provided `convert_json_csv.py` to convert your json files to csv. Simply run

```
python convert_json_csv.py
```
In the same directory of your json files.

## Additional notes
The admin tool does not work properly for workspaces that require approval or have access restrictions.

When that happens, you either have to manually do the edit, or you have to make sure the API key you are using has proper access and temporarily disable the approval so the tool can work.