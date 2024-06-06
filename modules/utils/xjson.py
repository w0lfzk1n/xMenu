# !/usr/bin/env python3
import json
import os
from modules.utils import xpaths
import modules.utils.log as xlog

def load_json(file_path, debug=True):
    """
    Loads JSON-File from path.
    :type file_path: str
    :param file_path: Path to JSON-File.
    :return: JSON-File as dict or None if error.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            if debug:
                xlog.log_success(f"Loaded JSON-File: {os.path.basename(file_path)}")
            return data
    except FileNotFoundError:
        xlog.log_error(f"[load-JSON] File not found: {file_path}")
    except json.JSONDecodeError:
        xlog.log_error(f"[load-JSON] File is not valid: {file_path}")
    except Exception as e:
        xlog.log_error(f"[load-JSON] Unexpected error loading File: {e}")
    return None


def save_json(SCRIPT_PATH, file_path, content={}):
    """
    Saves the content to a json file.
    :param str SCRIPT_PATH: Core path of script.
    :param str file + _path: Path to json file.
    :param dict content: Content to write.
    """
    full_path = os.path.join(SCRIPT_PATH, file_path)
    try:
        with open(full_path, "w") as file:
            json.dump(content, file, indent=4)
            #xlog.log_success(f"JSON file saved successfully at: {full_path}")
    except IOError as e:
        xlog.log_error(f"[save-JSON] Failed to write to file: {full_path}\n{e}")
    except Exception as e:
        xlog.log_error(f"[save-JSON] Unexpected error while saving JSON file: {e}")


def load_config_json(SCRIPT_PATH):
    """
    Returns config.json as dict.
    """
    core = load_json(xpaths.format_path("configs/core.json", SCRIPT_PATH))
    conf_paths = core["core"]["cpaths"]["configs"]
    for key in conf_paths:
        if key == "core":
            continue
        core[f"{key}"] = load_json(xpaths.format_path(conf_paths[key], SCRIPT_PATH))
    return core


def save_config_json(SCRIPT_PATH, CONFIG):
    """
    Saves config.json.
    Ignoring lang and cmdlist
    """
    config = CONFIG.copy()
    conf_paths = config["core"]["cpaths"]["configs"]
    config["core"]["cpaths"]["project_path"] = ""
    for key in conf_paths:
        if "core" in key:
            save_json(SCRIPT_PATH, conf_paths[key], {"core": config[key]})
        elif "defaults" in key:
            continue
        else:
            save_json(SCRIPT_PATH, conf_paths[key], config[key])
    xlog.log_success("Saved all configs")


def list_json(CONFIG, MOD, args=["all"]):
    """
    This Command lists the data of a specific attribut or all of the core_json object in the System.
    :param CONFIG <dict>: Configuration dictionary.
    :param MOD <dict>: Module dictionary.
    :param args <list>: Arguments of command.
    Usage: listjson <op:Attribute>
    Example: listjson paths
    """
    LANG = CONFIG["lang"]
    CONFIG["mod"] = MOD
    CONFIG["wordlist"] = []
    try:
        if len(args) < 1:
            json_attribute = "all"
        else:
            json_attribute = args[0]

        if json_attribute == "all":
            xlog.log_json_data(CONFIG, LANG)
        else:
            if json_attribute in CONFIG:
                xlog.log_json_data(CONFIG[json_attribute], LANG)
            else:
                xlog.log_error(f"Attribute '{json_attribute}' not found in CONFIG!")

    except Exception as e:
        xlog.log_error(f"xJSON ERROR: {e}")
