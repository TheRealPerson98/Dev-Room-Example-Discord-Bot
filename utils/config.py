import json
import os

def load_config(filename="config.json"):
    """ Load configuration from a JSON file inside the 'config' folder. """
    # Construct the path to the file within the 'config' folder, which is one level up from 'utils'
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', filename)

    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        raise Exception(f"Configuration file {filename} not found in 'config' directory.")
    except json.JSONDecodeError:
        raise Exception(f"Error decoding {filename}. Please check its validity.")
