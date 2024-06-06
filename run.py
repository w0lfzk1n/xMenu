# !/usr/bin/env python

try:
    import os
    from modules.utils import xpaths
    from modules.utils import xjson
    from modules.system import import_utils
except ImportError as e:
    missing_module = str(e).split(" ")
    print(f"The following required modules are missing:\n{missing_module}\n\nAborting script...\nPlease make sure to install them before running the script again.")
    exit(1)

# Preparing Config files
SCRIPT_PATH = xpaths.format_path(os.path.dirname(os.path.realpath(__file__)))
config = xjson.load_config_json(SCRIPT_PATH)
config["core"]["cpaths"]["project_path"] = SCRIPT_PATH
CONFIG = config

LANG = CONFIG["lang"]
CMD = CONFIG["cmd"]
MOD = import_utils.import_modules(SCRIPT_PATH, CONFIG)

# ModuleCores
pymod = MOD["python"]
utils = MOD["utils"]
psys = MOD["system"]
projects = MOD["projects"]
# ============================
# Imported Modules
xlog = utils["log"]
tools = utils["tools"]

getattr(utils['tools'], "clear_console")(CONFIG, MOD)

def main():
    while True:
        try:
            command = xlog.log_input("Command")
            args = command.split(" ")
            command = args[0]
            args = args[1:]
            psys["cmdHandler"].cmdHandler(CONFIG, MOD, command, args)
        except KeyboardInterrupt:
            xlog.log_end(LANG)
            break
        except Exception as e:
            xlog.log_error(f"RUN-Error: {e}")
            continue

if __name__ == "__main__":
    main()