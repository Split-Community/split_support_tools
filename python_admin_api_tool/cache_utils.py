import os
import pickle
import cache
CACHE_FILE = ".split_cache.pkl"

def load_cache(get_all_splits_definitions, get_segments):
    """
    Loads cached data from a file if it exists, and populates the cache with data for all splits and segments
    if they are not already in the cache. The cache is then saved to a file.
    """

    if os.path.exists(CACHE_FILE):
        print(f"cached file exists")
        try:
            with open(CACHE_FILE, "rb") as f:
                loaded_data = pickle.load(f)
            cache.cache_data.update(loaded_data)
        except (EOFError, pickle.UnpicklingError) as e:
            print(f"Failed to load cache file '{CACHE_FILE}': {e}")

    # Populate the cache with all_splits_definitions if it's not already in the cache
    if not cache.cache_data["all_splits_definitions"]:
        print(f"Caching split definition on the first script run or update.")
        print(f"Please wait...")
        cache.cache_data["all_splits_definitions"] = get_all_splits_definitions()
   
    # Populate the cache with segments if they're not already in the cache
    if not cache.cache_data["segments"]:
        print(f"Caching segments on the first script run or update.")
        print(f"Please wait...")
        cache.cache_data["segments"] = get_segments()
    save_cache()

def update_cache(get_all_splits_definitions, get_segments):
    """
    Updates the cache with the latest data for all splits and segments and saves it to a file.
    """
    try:
        os.remove(CACHE_FILE)
        #print(f"Cache file '{CACHE_FILE}' removed.")
        print(f"Cache removed.")
    except OSError as e:
        #print(e)
        pass
    cache.cache_data = cache.default_cache_data()
    # Load the cache with fresh data
    print(f"Fetching latest data.")
    load_cache(get_all_splits_definitions, get_segments)
    print(f"Cache updated with latest data.")

def save_cache():
    """
    Saves the cache to a file.
    """
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache.cache_data, f)

def quit_tool():
    """
    Saves the cache and exits the script.
    """
    save_cache()
    print("Goodbye!")
    exit()