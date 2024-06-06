# !/usr/bin/env python3

def list_backups(backup_path):
    """
    List directories in a specified backup path.
    Assumes that backups are stored in directories.
    """
    paths = []
    for entry in os.listdir(backup_path):
        full_path = os.path.join(backup_path, entry)
        if os.path.isdir(full_path):
            paths.append(full_path)
    return paths

def restore_project(CONFIG, MOD, args):
    """
    Restores the project from a backup.
    Choose a folder from "Backups" and restore the files in the Corepath with the files from backup.
    :param SCRIPT_PATH <str>: Core path of the project.
    :param CONFIG <dict>: Configuration dictionary.
    :param MOD <dict>: Module dictionary.
    """
    xlog = MOD["utils"]["log"]
    try:
        global os, shutil, questionary
        
        os = MOD["python"]["os"]
        shutil = MOD["python"]["shutil"]
        questionary = MOD["python"]["questionary"]

        xpaths = MOD["utils"]["xpaths"]
        
        reload = MOD["utils"]["reload"]
        
        LANG = CONFIG["lang"]
        SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]

        backup_path = xpaths.format_path("Backups", SCRIPT_PATH)
        available_backups = list_backups(backup_path)

        if not available_backups:
            xlog.log_info("No backups found.", LANG)
            return

        backup_to_restore = questionary.select("Choose a backup to restore:", choices=available_backups).ask()
        
        if not questionary.confirm("Are you sure you want to restore from this backup?").ask():
            xlog.log_info("Backup restoration canceled.")
            return
        
        # Perform the restoration
        target_path = SCRIPT_PATH
        xlog.log_info(f"Starting Restore of Project from path:\n\n[ {backup_to_restore} ]\n")
        for root, dirs, files in os.walk(backup_to_restore):
            relative_path = os.path.relpath(root, backup_to_restore)
            destination_dir = os.path.join(target_path, relative_path)
            os.makedirs(destination_dir, exist_ok=True)
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(destination_dir, file)
                shutil.copy2(src_file, dest_file)
        
        xlog.log_info("Backup restoration completed successfully. Restarting script...")
        reload.reload(CONFIG, MOD, args)
        
    except Exception as e:
        xlog.log_error(f"xRestore ERROR: {e}")