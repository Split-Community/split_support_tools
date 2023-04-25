import argparse
import cache_utils
import menu_utils
import data_utils

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin Tool")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    cache_utils.configure_logging(args.debug)
    menu_utils.configure_logging(args.debug)
    data_utils.configure_logging(args.debug)

    cache_utils.load_cache(data_utils.get_all_splits_definitions, data_utils.get_all_segments_definitions)
    menu_utils.main_menu()