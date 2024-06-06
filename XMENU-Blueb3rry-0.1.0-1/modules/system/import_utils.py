# !/usr/bin/env python3

import os
import importlib.util
from modules.utils import log as xlog
from modules.utils import xpaths

def import_modules(SCRIPT_PATH, CONFIG, debug=True):
    """
    Import all needed modules for entire project.
    :param SCRIPT_PATH <str>: Core Path to project.
    :param CONFIG <dict>: Configuration dictionary.
    :param debug <bool>: Debug mode.
    return <dict>: Dictionary of imported modules.
    {
        "python": {
            "module": <module>
        },
        "utils": {
            "module": <module>
        },
        "system": {
            "module": <module>
        },
        "projects": {
            "module": <module>
        }
    }
    """
    LANG = CONFIG["lang"]
    py_sysmodules = CONFIG["core"]["coredata"]["py_sys_modules"]
    path_to_scripts = xpaths.format_path(f'{SCRIPT_PATH}/{CONFIG["core"]["cpaths"]["module_path"]}')

    utils_to_import = {"python": py_sysmodules, "utils": [], "system": [], "projects": []}

    for project_module in ["utils", "system", "projects"]:
        for util in os.listdir(
            xpaths.format_path(
                os.path.join(path_to_scripts, project_module), SCRIPT_PATH
            )
        ):
            if util.endswith(".py") and util != "__init__.py":
                utils_to_import[project_module].append(util)

    if debug:
        xlog.log_info(
            f"DEBUG: Prepared {len(utils_to_import['python'])} Python | {len(utils_to_import['utils'])} UTILS | {len(utils_to_import['system'])} SUBMODS | {len(utils_to_import['projects'])} Projects to import.."
        )
        xlog.log(f"DEBUG: Importing Python modules...", LANG, 1, "both")

    util_import = {"sys_error": {}, "misc_error": {}}
    util_export = {"python": {}, "utils": {}, "system": {}, "projects": {}}

    for sys_module in py_sysmodules:
        try:
            if isinstance(sys_module, dict):
                from_list = sys_module["from"]
                if isinstance(from_list, str):
                    from_list = [from_list]
                for from_module in from_list:
                    module = __import__(from_module, fromlist=sys_module["namelist"])
                    for sub_module in sys_module["namelist"]:
                        util_export["python"][f"{from_module}.{sub_module}"] = getattr(
                            module, sub_module
                        )
                        if debug:
                            xlog.log_info(
                                f"-=| |=- Imported {from_module}.{sub_module}"
                            )
            else:
                module = __import__(sys_module)
                util_export["python"][sys_module] = module
                if debug:
                    xlog.log_info(f"-=| |=- Imported {sys_module}")
        except ImportError as e:
            if 'Crypto' in str(e):
                module = 'pycryptodome'
            elif 'PIL' in str(e):
                module = 'pillow'
            else:
                module = sys_module if isinstance(sys_module, str) else sys_module['from'][0]
            util_import["sys_error"][module] = e

    if util_import["sys_error"]:
        xlog.log(f"Missing Modules:\n{util_import['sys_error']}", LANG, 1, "top")
        ask_install = xlog.log_input("Some system modules could not be imported. Do you want to try to install them? (Yes/No/Skip)")

        if ask_install.lower() in ["y", "yes", "ys", "ya", "ja", "j"]:
            os.system(f"pip3 install -r configs/requirements/requirements.txt")

        elif ask_install.lower() in ["no", "n", "", None]:
            xlog.log_error("Some modules could not be imported. Exiting..")
            exit(1)

        elif ask_install.lower() in ["skip", "s", "sk"]:
            xlog.log_error(
                "Some modules could not be imported. You might encounter mayor issues.."
            )
            xlog.log_input("Press ENTER to continue...")
            pass

    for project_module in ["utils", "system", "projects"]:
        if debug:
            xlog.log(f" Importing CustomModules from '{project_module}'...", LANG, 1, "both")
        module_path = os.path.join(path_to_scripts, project_module)
        for file in os.listdir(module_path):
            if file.endswith(".py") and file != "__init__.py":
                module_name = file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(
                        module_name, os.path.join(module_path, file)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    util_export[project_module][module_name] = module
                    if debug:
                        xlog.log_info(f"-=| |=- Imported {module_name}")
                except Exception as e:
                    util_import["misc_error"][module_name] = e

    for util in util_import["sys_error"]:
        xlog.log_bar(LANG, 1)
        xlog.log_info(f"Error importing sys_module: {util}")
        xlog.log_info(f"ImportError: {util_import['sys_error'][util]}")

    for util in util_import["misc_error"]:
        xlog.log_bar(LANG, 1)
        xlog.log_info(f"Error importing misc_module: {util}")
        xlog.log_info(f"ImportError: {util_import['misc_error'][util]}")

    if debug or (util_import["sys_error"] or util_import["misc_error"]):
        xlog.log_input("Press ENTER to continue. . .")

    return util_export