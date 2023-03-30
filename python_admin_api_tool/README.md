## Overview

This is a simple python tool utilizing the Split's [Python PyPi library for Split REST Admin API](https://help.split.io/hc/en-us/articles/4412331052685-Python-PyPi-library-for-Split-REST-Admin-API)

## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/)

2. Clone this repository


3. Create a new virtual environment

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

4. Install the requirements

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file

   ```bash
   $ cp .env.example .env
   ```

7. Add your [Admin API key](https://help.split.io/hc/en-us/articles/360019916211-API-keys#adding-admin-api-keys) to the newly created `.env` file

8. Run the tool

   ```bash
   $ python python_admin_tool.py
   ```


## Usage:

- The menu is straight forward with the options. There are 2 choices: Search and Export

- The Search options are:

```
1. Search Workspaces Or Groups
   - This will search for the name of the workspaces or the groups in your org.

2. Search Environments
   - This will search for the environments of the same name across all workspaces.

3. Search Users
   - Requires the email of the users being searched. Will show information of the user and which group they are in.

4. Search Splits
   - This will search for all splits of the same name across all workspaces and environments. Also a sub-option to show all the definitions of the Split.

5. Search Segments
   - This will search for all segments of the same name across all workspaces and environments, and will also display all the keys of the segments.

```
- Similarly, the export options are straightforward. By default, all exports are json format. Please also see Additional tool for info.

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

## additional tool
You can use the provided `convert_json_csv.py` to convert your json files to csv. Simply run

```
python convert_json_csv.py
```

In the same directoy of your json files.

