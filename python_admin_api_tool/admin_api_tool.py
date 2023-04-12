import cache_utils
import menu_utils
import data_utils

if __name__ == '__main__':
    cache_utils.load_cache(data_utils.get_all_splits_definitions, data_utils.get_segments)
    menu_utils.main_menu()   