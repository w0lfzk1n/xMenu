# !/usr/bin/env python3

def dev(CONFIG, MOD, args=[]):
    global xlog
    """
    Dev command
    """

    # Module imports
    # >> Python libraries
    pymod = MOD["python"]
    # >> modules/system scripts
    system = MOD["system"]
    # >> modules/utils scripts
    utils = MOD["utils"]
    # >> modules/projects scripts
    projects = MOD["projects"]

    os = pymod["os"]
    questionary = pymod["questionary"]
    # Module-Tools to use
    xpaths = utils["xpaths"]
    xjson = utils["xjson"]
    xlog = utils["log"]
    tools = utils["tools"]
    config = system["config"]

    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
    HOSTS = CONFIG["hosts"]
    LANG = CONFIG["lang"]


    # This file will be used for showcasing the creation of modules for this project
    
    xlog.log_continue("This file has not been edited. The 'modules/projects/dev.py' will be used for showcasing the creation of modules and usage of the things supplied by this project.")