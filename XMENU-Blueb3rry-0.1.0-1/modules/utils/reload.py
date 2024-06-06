# !/usr/bin/env python3

def reload(CONFIG, MOD, args):
    """
    Reloads the code, when changes are made in the code.
    Restarts the console. No stopping the script.
    """
    os = MOD["python"]["os"]
    sys = MOD["python"]["sys"]
    xlog = MOD["utils"]["log"]
    
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
    LANG = CONFIG["lang"]
    
    xlog.log("Restarting script... Hold on...", LANG, 2, "bottom")
    
    cmd = [sys.executable, os.path.join(SCRIPT_PATH, 'run.py')] + args
    
    try:
        os.execvp(cmd[0], cmd)
        xlog.log_info("Failed to replace process!")
    except OSError as e:
        xlog.log_info(f"Script restart failed! Error: {e}")
    return