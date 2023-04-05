## Overview

This is a simple python tool utilizing the Split's [Python PyPi library for Split REST Admin API](https://help.split.io/hc/en-us/articles/4412331052685-Python-PyPi-library-for-Split-REST-Admin-API)

## Setup

1. If you don’t have Python 3 installed, [install it from here](https://www.python.org/downloads/)
   - Please note that on MacOS, the python commmand is `python3`

2. Clone this repository

   ```bash
   git clone --depth 1 --filter=tree:0 git@github.com:Split-Community/split_support_tools.git --branch main --single-branch python_admin_api_tool
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

6. Make a copy of the example environment variables file

   ```bash
   cp env_sample .env
   ```

7. Add your [Admin API key](https://help.split.io/hc/en-us/articles/360019916211-API-keys#adding-admin-api-keys) to the newly created `.env` file
   - Note that it's recommend to use an API keys that is scoped across all environments and workspaces
   - If the the environment/workspace has access restrictions, you might encounter an error.

8. Run the tool

   ```bash
   python admin_api_tool.py
   
   or python3 admin_api_tool.py on MacOS
   ```

## Caching
- To reduce API calls and improve response time, the script caches all data on the first run. This may take up to 30-40 seconds. This is needed only on the first run or when updating the cache.

- If you make changes to your Splits, it's recommended that you update the cache using the "Update Cache" option.

## Usage:
- The menu is straight forward with the options. There are 5 choices: Search, List, Export,Operations, and Update Cache.

- The Search options are:

```
1. Search Workspaces Or Groups
   - This will search for the name of the workspaces or the groups in your org.

2. Search Environments
   - This will search for all the environments of the same name across all workspaces. You will also have the option to see all the splits' definitions under this environment's name.

3. Search Users
   - Requires the email of the users being searched. Will show information of the user and which group they are in.

4. Search Splits
   - This will search for all splits of the same name across all workspaces and environments. Also a sub-option to show all the definitions of the Split.

5. Search Segments
   - This will search for all segments of the same name across all workspaces and environments, and will also display all the keys of the segments.

```

- The List options are self-explanatory. Note that these do not show the full details (such as Split's definitions or segment keys), please use the Export functions to get the full data.

```
1. List All Workspaces
   - List all workspaces in the org.

2. List All Environments
   - List all environments across all workspaces.

3. List All Groups
   - List all the groups, will not show list of users.

4. List All Segments
   - List all the segments for all environments and workspaces, will not show the segment keys.

5. List All Splits
   - List all the splits across all workspaces, will not show split's definitions.

6. List All Users
   - List all active users.
```

- Similarly, the Export options are straightforward. By default, all exports are json format. Please also see Additional tool for info.

```
1. Export Groups
   - This will export all groups and the users in each group.

2. Export Segments
   - This will export all segments across all workspaces and environments as well as the corresponding keys.

3. Export Splits
   - This will export all Splits (not the definitions) across all workspaces and environments.

4. Export Split Definitions
   - This will export all Splits definitions across all workspaces and environments.

5. Export Users
   - This will export all ACTIVE users (cannot export inactive users).

6. Export Workspaces
   - This will export all workspaces in your org.

7. Export Environments
   - This will export all environments across all workspaces.

```

- The Operations are options that will mutate or change your splits/workspaces/environments. More options will be added over time

```
1. Delete Splits
   - This will forcefully delete the Split in the workspace you specified, regardless of the definitions. Note that this is not reversable!
```

- The Update Cache option is as the name implies.

## Additional tool
You can use the provided `convert_json_csv.py` to convert your json files to csv. Simply run

```
python convert_json_csv.py
```

In the same directory of your json files.

