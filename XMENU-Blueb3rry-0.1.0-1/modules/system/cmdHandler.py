# !/usr/bin/env python3

def find_command(CMD, command):
    """
    Find the command in the command configuration.
    :param CMD: Object: Object of Command Infos.
    :param command: string: Input of user, check against 'Aliases'.
    """
    for cmd_name, cmd_info in CMD.items():
        if command.lower() in cmd_info["aliases"]:
            return cmd_info
    return None


def cmdHandler(CONFIG, MOD, command, args=[]):
    """
    Handles incoming commands.
    :param str 'SCRIPT_PATH': Core path of script.
    :param dict 'CONFIG': Config dict.
    :param dict 'MOD': Module dict.
    :param str 'command': Command to handle.
    :param list 'args': Arguments of command.
    """
    exit_keys = CONFIG["core"]["runtime"]["exit_keys"]

    # ModuleCores
    utils = MOD["utils"]
    psys = MOD["system"]
    # ============================
    xlog = utils["log"]
    # ============================

    if command in exit_keys:
        xlog.log_end(CONFIG["lang"])
        exit()

    cmd_config = CONFIG["cmd"]
    cmd_info = find_command(cmd_config, command)

    try:
        if cmd_info:
            if cmd_info["is_project"]:
                # ============================
                # Command to run other modules like projects
                if cmd_info["title"] == "Run":
                    psys[cmd_info["sub_modulepack"]].run_command(
                        CONFIG, MOD, args
                    )
                    return
                    
            # ============================
            # Commands without arguments
            else:
                getattr(MOD[f"{cmd_info['core_modulepack']}"][f"{cmd_info['sub_modulepack']}"], cmd_info['function_call'])(CONFIG, MOD, args)
                return
                
            xlog.log_info(f"Command '{command}' is a project and needs 'run'.\n     >> Check 'help run' for more info")
        else:
            if command != "":
                xlog.log_info(f"Command '{command}' not found.")
        return
            
    except Exception as e:
        xlog.log_error(f"cmdHandler ERROR: {e}")