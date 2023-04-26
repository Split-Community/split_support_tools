## Overview


This is a simple Python tool utilizing Split's [Python PyPi library for Split REST Admin API](https://help.split.io/hc/en-us/articles/4412331052685-Python-PyPi-library-for-Split-REST-Admin-API)


## Setup


1. If you don’t have Python 3 installed, [install it from here](https://www.python.org/downloads/)
- Please note that on MacOS, the python command is `python3`
- You can run the following command to create the alias for python
```
echo "alias python=python3\nalias pip=pip3" >> ~/.zprofile


source ~/.zprofile
```
- Now your `python` command on the mac will run python3.


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


6. Make a copy of the example environment variables file


```bash
cp env_sample .env
```


7. Add your [Admin API key](https://help.split.io/hc/en-us/articles/360019916211-API-keys#adding-admin-api-keys) to the newly created `.env` file
- Note that it's recommend to use an API keys that is scoped across all environments and workspaces
- If the environment/workspace has access restrictions, you might encounter an error.


8. Run the tool


```bash
python admin_api_tool.py
```
or on MacOS


```bash
python3 admin_api_tool.py
```


## Caching
- To reduce API calls and improve response time, the script caches split definitions and segments definitions on the first run if there is no cache data, other data will be cached on the first use.


- If you make changes to your Splits, it's recommended that you update the cache using the "Update Cache" option.


## Usage:
- The menu is straight forward with the options. There are 5 choices: Search, List, Export, Operations, and Update Cache.

- The Search options are:

```
1. Search Workspaces Or Groups
   - This will search for the name of the workspaces or the groups in your org.


2. Search Environments
   - This will search for all the environments of the same name across all workspaces. You will also have the option to see all the splits' definitions under this environment's name.


3. Search Users
   - Requires the email of the users being searched. Will show information of the user and which group they are in.


4. Search Splits
   - This will search for all splits of the same name across all workspaces and environments.
   - When a split is found, the user can choose to export the following:
      * This split's definition from a specific environment to json
      * The treatment keys to csv
      * The list of the targeting rules csv


5. Search Segments
   - This will search for all segments of the same name across all workspaces and environments, and will also display all the keys of the segments.
- When a segment is found, the user can choose to export the following:
* The segment keys to csv
```

- The List options are self-explanatory. Note that these do not show the full details (such as Split's definitions or segment keys), please use the Export functions to get the full data.


```
1. List All Workspaces
   - List all workspaces in the org.

2. List All Environments
   - List all environments across all workspaces.

3. List All Groups
   - List all the groups and the list of users.

4. List All Segments
   - List all the segments and keys of each for all environments and workspaces.

5. List All Splits
   - List all the splits across all workspaces, will not show split's definitions (use the export option for the definitions).

6. List All Users
   - List all users and their statuses.
```


- Similarly, the Export options are straightforward. By default, all exports are json format. Please also see Additional tool for info.


```
1. Export Environments
   - This will export all environments across all workspaces.

2. Export Groups
   - This will export all groups and the users in each group.

3. Export Segments Definitions
   - This will export all segments definitions across all workspaces and environments.

4. Export Segments Keys
   - This will let the user choose the workspace, environment, the segment, and export all the keys.

5. Export Split Definitions
   - This will export all Splits definitions across all workspaces and environments.

6. Export Splits
   - This will export all Splits (not the definitions) across all workspaces and environments.

7. Export Users
   - This will export all the users and their statuses, as well as group memberships.

8. Export Workspaces
   - This will export all workspaces in your org.
```

- The Operations are options that will mutate or change your splits/segments/workspaces/environments. More options will be added over time.


```
1. Copy Segment Definitions
   - This allows for copying the keys of one segment to another segment. Users can choose from available lists of workspaces, environments, and segments to copy.

2. Copy Split Definitions
   - This allows for copying the definitions of one split to another split. Users can choose from available lists of workspaces, environments, and splits to copy.

3. Delete Groups
   - This will forcefully delete the group in the workspace you specified, regardless of the definitions. Note that this is not reversible!

4. Delete Segments
   - This will forcefully delete the segment in the workspace you specified, regardless of the definitions. Note that this is not reversible!

5. Delete Splits
   - This will forcefully delete the Split in the workspace you specified, regardless of the definitions. Note that this is not reversible!

6. Main Menu

7. Quit Tool
```

- The Update Cache option


```
It's recommended to run this option after you have made changes to the splits to ensure the latest data.
```


## DEBUG Logging:
If you run into issues, you can run the script with debug logging enabled for better troubleshooting:


```bash
python admin_api_tool.py --debug
```



## Additional tool
You can use the provided `convert_json_csv.py` to convert your json files to csv. Simply run


```
python convert_json_csv.py
```


In the same directory of your json files.



## Additional notes:
The admin tool will not work properly for workspaces that require approval or have access restrictions.


When that happens, you either have to manually do the edit, or you have to make sure the API key you are using has proper access and temporarily disables the approval so the tool can work.