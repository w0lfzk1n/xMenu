# !/usr/bin/env python3

def run_command(CONFIG, MOD, args=[]):
    """
    Runs a command.
    """

    import os
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]

    CMDS = CONFIG["cmd"]

    # ModuleCores
    psys = MOD["system"]
    utils = MOD["utils"]
    # ============================
    # Imported Modules
    xlog = utils["log"]
    cmd_finder = psys["cmdHandler"]

    if not args:
        xlog.log_error("No arguments given. Check 'help run' for more info.")
        return

    process_cmd = cmd_finder.find_command(CMDS, args[0])

    if process_cmd != None and process_cmd["is_project"]:
        # ============================
        # PROJECTS
        # Exeptional scripts that require a external script to run
        if process_cmd["title"] == "Cyberdrop-dl":
            # If system is not windows, dont run script
            if os.name != "nt":
                os.system(f"bash {SCRIPT_PATH}/modules/projects/cyberDrop/run.sh")
            else:
                os.system(f"{SCRIPT_PATH}/modules/projects/cyberDrop/run.bat")

        # ============================
        # If not in this list, its a integrated script
        else:
            getattr(MOD[f"{process_cmd['core_modulepack']}"][f"{process_cmd['sub_modulepack']}"], process_cmd['function_call'])(CONFIG, MOD, args)

        # ============================
        # If the found command should not be exec with 'run', redirect to normal handler without 'run'.
    elif process_cmd and not process_cmd["is_project"]:
        getattr(MOD['system']['cmdHandler'], 'cmdHandler')(CONFIG, MOD, args[0], args=[])

    else:
        xlog.log_info(f"RunCommand '{args[0]}' not found.")
    # ============================
    return
