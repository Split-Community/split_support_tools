import logging
logger = logging.getLogger(__name__)

def configure_logging(debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)


import cache_utils, export_utils, list_utils, ops_utils, search_utils, re
from data_utils import get_all_splits_definitions, get_all_segments_definitions

formatted_text_cache = {}
formatted_options_cache = {}

def update_cache():
    cache_utils.update_cache(get_all_splits_definitions, get_all_segments_definitions)

def format_text(text):
    """
    Replace underscores in the text with spaces and format the text to title case.

    Args:
        text: A string to be formatted.

    Returns:
        A formatted string in title case.
    """
    if text not in formatted_text_cache:
        formatted_text_cache[text] = re.sub('_', ' ', text).title()
    return formatted_text_cache[text]

def display_options(options, menu_name):
    """
    Display a list of options as a formatted menu.

    Args:
        options: A dictionary containing the menu options.
        menu_name: A string containing the name of the menu to display.

    Returns:
        Output to stdout.
    """
    if menu_name not in formatted_options_cache:
        formatted_options_cache[menu_name] = [
            f"{key}. {format_text(func.__name__)}"
            for key, func in options.items()
        ]
    
    print("-------------------------------------------")
    print(f"PYTHON ADMIN API TOOL - {menu_name}")
    print("-------------------------------------------")
    print("\n".join(formatted_options_cache[menu_name]))

def get_choice(options, menu_name):
    """
    Displays the options of the given menu and prompts the user to enter a choice. 
    If the choice is valid, the corresponding function is called. If the choice is 
    invalid, an error message is displayed and the prompt is repeated.

    Args:
        options (dict): A dictionary containing the menu options where keys are the option numbers 
            and values are the functions to execute when the option is chosen.
        menu_name (str): The name of the menu to be displayed.

    Returns:
        Output to stdout.
    """

    while True:
        display_options(options, menu_name)
        choice = input(f"Enter your choice (1-{len(options)}): ")
        try:
            options[choice]()
        except (KeyError, ValueError, IndexError):
            print("Invalid choice, try again")
        except KeyboardInterrupt:
            print("\nExiting...")
            cache_utils.quit_tool()

def search():
    ops_list = [
    search_utils.search_workspaces_or_groups,
    search_utils.search_environments,
    search_utils.search_users,
    search_utils.search_feature_flags,
    search_utils.search_segments,
    main_menu,
    cache_utils.quit_tool,
]
    sorted_ops_list = sorted(ops_list, key=lambda func: func.__name__)
    options = {str(idx+1): func for idx, func in enumerate(sorted_ops_list)}
    get_choice(options, "Search")

def list():
    ops_list = [
    list_utils.list_all_workspaces,
    list_utils.list_all_environments,
    list_utils.list_all_groups,
    list_utils.list_all_segments,
    list_utils.list_all_feature_flags,
    list_utils.list_all_users,
    main_menu,
    cache_utils.quit_tool,
]
    sorted_ops_list = sorted(ops_list, key=lambda func: func.__name__)
    options = {str(idx+1): func for idx, func in enumerate(sorted_ops_list)}
    get_choice(options, "List")

def export_all_data():
    ops_list = [
    export_utils.export_groups,
    export_utils.export_segments_definitions,
    ops_utils.export_segments_keys,
    export_utils.export_feature_flags,
    export_utils.export_feature_flags_definitions,
    export_utils.export_users,
    export_utils.export_workspaces,
    export_utils.export_environments,
    main_menu,
    cache_utils.quit_tool,
]
    sorted_ops_list = sorted(ops_list, key=lambda func: func.__name__)
    options = {str(idx+1): func for idx, func in enumerate(sorted_ops_list)}
    get_choice(options, "Export")

def operations():
    ops_list = [
        ops_utils.delete_groups,
        ops_utils.delete_feature_flags,
        ops_utils.delete_segments,
        ops_utils.copy_feature_flag_definitions,
        ops_utils.copy_segment_definitions,
        main_menu,
        cache_utils.quit_tool
    ]
    
    sorted_ops_list = sorted(ops_list, key=lambda func: func.__name__)
    options = {str(idx+1): func for idx, func in enumerate(sorted_ops_list)}
    get_choice(options, "Operations")


def main_menu():
    ops_list = [
        search, 
        list, 
        export_all_data,
        operations,
        update_cache,
        cache_utils.quit_tool
    ]
    #sorted_ops_list = sorted(ops_list, key=lambda func: func.__name__)
    options = {str(idx+1): func for idx, func in enumerate(ops_list)}
    get_choice(options, "Main")