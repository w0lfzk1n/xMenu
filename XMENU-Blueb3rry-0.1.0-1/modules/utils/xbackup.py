# !/usr/bin/env python3

def backup_project(CONFIG, MOD, args):
    """
    Copies project folder to backup folder.
    Name of backup folder is "X01-0_Backup" or "X01-1_Backup" and so on.
    :param SCRIPT_PATH <str>: Core path of the project.
    :param CONFIG <dict>: Configuration dictionary.
    :param MOD <dict>: Module dictionary.
    :param backup_version <str>: Name of the backup version 'X01'.
    """
    try:
        os = MOD["python"]["os"]
        shutil = MOD["python"]["shutil"]
        
        xpaths = MOD["utils"]["xpaths"]
        xlog = MOD["utils"]["log"]
        
        LANG = CONFIG["lang"]
        SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
        version = LANG["version"]
        
        subversion = 0
        if not args:
            backup_version = f"XMENU-{version}"
        else:
            backup_version = args[0]

        project_name = xpaths.format_path(os.path.basename(SCRIPT_PATH))
        backup_path = xpaths.format_path("Backups", SCRIPT_PATH)

        xlog.log(f"--===>> INITATED BACKUP", LANG, 1, "top")
        xlog.log_info(f"-=> Working_path: {SCRIPT_PATH}")
        xlog.log_info(f"-=> Backup_path: {backup_path}\n")
        xlog.log_info(f"Backing up project: {project_name}")

        if not os.path.exists(backup_path):
            try:
                os.mkdir(backup_path)
                xlog.log_success(f"Created Main-Backup folder: {backup_path}")
            except OSError as e:
                xlog.log_error(f"Could not create Main-Backup folder: {e}")
                return

        while os.path.exists(
            xpaths.format_path(f"{backup_version}-{subversion}", backup_path)
        ):
            subversion += 1
        backup_version = f"{backup_version}-{subversion}"
        backup_path = xpaths.format_path(backup_version, backup_path)

        xlog.log_info(f"New Backupname: {backup_version}")
        xlog.log_info(f"Copying project folder to backup folder.")
        try:
            shutil.copytree(
                SCRIPT_PATH, backup_path, ignore=shutil.ignore_patterns("0data", "__pycache__", "Backups", "AppData", "Old Files", "venv", "Downloads", "WIN_venv", "UNIX_venv")
            )
        except shutil.Error as e:
            xlog.log_error(f"Could not copy project folder to backup folder: {e}")
            return

        xlog.log_info(f"Backup completed.")
        xlog.log_bar(LANG, 1)
        
    except Exception as e:
        xlog.log_error(f"xBackup ERROR: {e}")