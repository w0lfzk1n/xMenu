# !/usr/bin/env python3

import time
from modules.utils.tools import xdatenow

nolog = "No message for log has been supplied!"

def log_info(msg=nolog):
    """Prints a message with the INFO prefix"""
    print(f"{xdatenow()} |>> INFO: {msg}")

def log_continue(msg=nolog):
    """Prints the message and forces the user to press any key to continue"""
    print(f"\n{xdatenow()} |>> INFO: {msg}")
    input("Press ANY Key to continue. . .")

def log_error(msg):
    """Prints a message with the ERROR prefix and forces the user to press any key to continue"""
    print(f"{xdatenow()} |>> ERROR: {msg}")
    input("Press ANY Key to continue. . .")


def log_warning(msg, LANG):
    """
    Prints a message with the WARNING prefix
    :param str 'msg': The message to print.
    :param dict 'LANG': The language dict.
    """
    print(
        f"{LANG['bar3']}\n{xdatenow()} |>> WARNING: {msg}\n{LANG['bar3']}"
    )


def log_debug(msg, LANG):
    """
    Prints a message with the DEBUG prefix
    :param str 'msg': The message to print.
    :param dict 'LANG': The language dict.
    """
    print(
        f"{LANG['bar3']}\n{xdatenow()} |>> DEBUG: {msg}\n{LANG['bar3']}"
    )


def log_success(msg):
    """Prints a message with the SUCCESS prefix"""
    print(f"{xdatenow()} |-- SUCCESS: {msg}")


def log_fail(msg):
    """Prints a message with the FAIL prefix"""
    print(f"{xdatenow()} |-- FAIL: {msg}")


def log_input(msg):
    """Prints a message with the INPUT prefix"""
    return input(f"\n{xdatenow()} |-- {msg} : ")


def log(msg, LANG, barType=None, position=None):
    """
    Prints a message with a bar ontop or below.
    :param msg: The message to print
    :param barType: The type of bar to print. Default: None
    :options: [1, 2, 3]
    :param position: The position of the bar. Default: None
    :options: ['top', 'bottom']
    """
    try:
        if barType is None:
            print(f"{xdatenow()} | {msg}")
            return
        else:
            bar_patterns = [LANG[f"bar{i}"] for i in range(1, 6)]

            if barType in range(1, 6):
                pattern = bar_patterns[barType - 1]
                if position == "top":
                    print(f"{pattern}\n{msg}")
                elif position == "bottom":
                    print(f"{msg}\n{pattern}")
                else:
                    print(f"{pattern}\n{msg}\n{pattern}")
            else:
                print(msg)
    except KeyError as e:
        log_error(f"[log-raw] KeyError: {e}")
    except ValueError as e:
        log_error(f"[log-raw] ValueError: {e}")
    except Exception as e:
        log_error(f"[log-raw] Unknown Error: {e}")


def log_bar(LANG, barType=None):
    """
    Prints a bar
    :param LANG: dict - The object for language strings.
    :param barType: int - The type of bar to print.
    """
    bar_patterns = [LANG[f"bar{i}"] for i in range(1, 6)]
    if barType in range(1, 6):
        pattern = bar_patterns[barType - 1]
        print(f"{pattern}")


def log_header(LANG, MOD):
    """Prints the header"""
    lng_header = LANG["header2"]
    version = LANG["version"]
    title = LANG["title"]
    note = LANG["note"]
    len_sysd, len_utils, len_submods, len_projects = (
        len(MOD["python"]),
        len(MOD["utils"]),
        len(MOD["system"]),
        len(MOD["projects"]),
    )
    header_txt = f"""{lng_header}
          >> Version: [ {version} ]
{title}

Dev_Note:
"{note}"

Imported Modules:\n[Python: {len_sysd} | System: {len_submods} | Util: {len_utils} | Projects: {len_projects}]
"""
    
    
    len_txt = f">> Version: [ {version} ]\nImported Modules:\nPY: {len_sysd} | UTILS: {len_utils} | SYSTEM: {len_submods} | PROJECTS: {len_projects}"
    print(header_txt)


def log_helppage(CONFIG, MOD, args=[]):
    """
    Prints the main help page.
    Or for a specific command.
    :param CONFIG: object: Config object.
    :param MOD: object: Modules object.
    :param args: array: Array of arguments, for specific helppage.
    """
    LANG = CONFIG["lang"]
    CMDS = CONFIG["cmd"]

    # ModuleCores
    psys = MOD["system"]
    utils = MOD["utils"]
    # ============================
    # Imported Modules
    cmd_finder = psys["cmdHandler"]

    lng_helppage = "Helppage for the available commands. Use 'help <command>' for more info.\n"
    try:
        for cmd in CMDS:
            cmd_info = cmd_finder.find_command(CMDS, cmd)
            if not cmd_info:
                log(f"Problem detected with helppage for command:  {cmd}\n\nThere seems to be a command in the 'cmd' config, where the aliases don't include the command-key (name of the object).\nPlease fix it manually!\nReview the template for 'cmd' in 'configs/defaults.json'", LANG, 3)
                exit(1)
            lng_helppage += f"\n## {cmd_info['title']}\n - Usage: {cmd_info['usage']}\n - Alias: {cmd_info['aliases']}\n{cmd_info['content']}\n\n"
        if args:
            process_cmd = cmd_finder.find_command(CMDS, args[0])
            if process_cmd:
                log_json_data(process_cmd, LANG)
            else:
                log_error(f"Helppage for Command '{args[0]}' not found.")
        else:
            log(lng_helppage, LANG, 2)
        return
    except KeyError as e:
        log_error(f"[log-help] KeyError: {e}")
    except ValueError as e:
        log_error(f"[log-help] ValueError: {e}")
    except Exception as e:
        log_error(f"[log-help] Unknown Error: {e}")


def log_end(LANG):
    """Prints the end"""
    print("\n")
    log_bar(LANG, 1)
    log_info(LANG["end"])
    log_bar(LANG, 1)


def log_json_data(data, LANG, indent=0):
    """
    Prints the data of a json file.
    :param data: The data to print.
    :param LANG: The language dict.
    :param indent: The number of spaces for indentation.
    """
    try:
        if indent == 0:
            log_bar(LANG, 2)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    print(f"{' ' * (indent - 1)}{key}:")
                    log_json_data(value, LANG, indent + 2)
                else:
                    print(f"{' ' * indent}{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    log_json_data(item, LANG, indent + 2)
                else:
                    print(f"{' ' * indent}{item}")
        if indent == 0:
            log_bar(LANG, 2)
    except KeyError as e:
        log_error(f"[log-jsondat] KeyError: {e}")
    except ValueError as e:
        log_error(f"[log-jsondat] ValueError: {e}")
    except Exception as e:
        log_error(f"[log-jsondat] Unknown Error: {e}")