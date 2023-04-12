import cache_utils, export_utils, list_utils, ops_utils, search_utils, re
from data_utils import get_all_splits_definitions, get_segments


formatted_text_cache = {}
formatted_options_cache = {}

def update_cache():
    cache_utils.update_cache(get_all_splits_definitions, get_segments)

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
    print("----------------------------------------")
    print(f"PYTHON ADMIN API TOOL - {menu_name}")
    print("----------------------------------------")
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
    options = {
        "1": search_utils.search_workspaces_or_groups,
        "2": search_utils.search_environments,
        "3": search_utils.search_users,
        "4": search_utils.search_splits,
        "5": search_utils.search_segments,
        "6": main_menu,
        "7": cache_utils.quit_tool,
    }
    get_choice(options, "Search")

def list():
    options = {
        "1": list_utils.list_all_workspaces,
        "2": list_utils.list_all_environments,
        "3": list_utils.list_all_groups,
        "4": list_utils.list_all_segments,
        "5": list_utils.list_all_splits,
        "6": list_utils.list_all_users,
        "7": main_menu,
        "8": cache_utils.quit_tool,
    }
    get_choice(options, "List")

def export_all_data():
    options = {
        "1": export_utils.export_groups,
        "2": export_utils.export_segments,
        "3": export_utils.export_splits,
        "4": export_utils.export_split_definitions,
        "5": export_utils.export_users,
        "6": export_utils.export_workspaces,
        "7": export_utils.export_environments,
        "8": main_menu,
        "9": cache_utils.quit_tool
    }
    get_choice(options, "Export")

def operations():
    options = {
        "1": ops_utils.delete_splits,
        "2": main_menu,
        "3": cache_utils.quit_tool
    }
    get_choice(options, "Operations")

def main_menu():
    options = {
        "1": search,
        "2": list,
        "3": export_all_data,
        "4": operations,
        "5": update_cache,
        "6": cache_utils.quit_tool
    }
    get_choice(options, "Main")