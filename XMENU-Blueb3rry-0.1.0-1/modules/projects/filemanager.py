def file_actions(CONFIG, MOD, source_path):
    global time, questionary, tools,default_hostpath
    """
    Interactive menu to perform actions on files and folders like renaming, deleting, copying, moving, and displaying information.
    :param MOD: object: Object for the project modules.
    :param source_path: Root-path for actions.
    :return: None or confirmation of completed actions.
    """
    
    questionary = MOD["python"]["questionary"]
    os = MOD["python"]["os"]
    time = MOD["python"]["time"]
    shutil = MOD["python"]["shutil"]
    xlog = MOD["utils"]["log"]
    tools = MOD["utils"]["tools"]
    xpaths = MOD["utils"]["xpaths"]

    LANG = CONFIG["lang"]
    
    NETW = CONFIG["hosts"]
    default_hostpath = tools.basic_menu(MOD, NETW.keys(), f"Select the host you are on (Enter to use Default: {CONFIG['core']['default_host']}):")
    if not default_hostpath:
        xlog.log_info("Using corepath of default host.")
        default_hostpath = CONFIG["core"]["default_host"]
    
    source_path = tools.basic_menu(MOD, NETW[f"{default_hostpath}"]["paths"]["as_runtime"], "Choose a Source Path:")
    if not source_path:
        xlog.log_error("File Manager Canvelled by user.")
        return
    
    runtime_path = source_path
    
    while True:
        try:
            tools.cls()
            xlog.log_header(LANG, MOD)
            xlog.log(f"\nFile & Folder Actions Menu.\n\nCurrent path: {runtime_path}\n", LANG, 2, "top")
            
            files = os.listdir(runtime_path)
            files.sort()
            files = [".."] + files + [">> Exit"]

            file = questionary.select("Select a File or Folder:", choices=files).ask()
            if file == ">> Exit" or file is None:
                return
            
            if file == "..":
                runtime_path = os.path.dirname(runtime_path.rstrip("/"))
                continue
            
            selected_path = os.path.join(runtime_path, file)

            if os.path.isdir(selected_path):
                action = questionary.select(
                    "Choose an action for this folder:",
                    choices=["Enter", "Rename", "Delete", "Copy", "Move", "Show Info", "Back"]
                ).ask()
                if action == "Enter":
                    runtime_path = selected_path
                    continue
            else:
                action = questionary.select(
                    "Choose an action for this file:",
                    choices=["Rename", "Delete", "Copy", "Move", "Show Info", "Back"]
                ).ask()

            if action in ["Rename", "Delete", "Copy", "Move", "Show Info"]:
                handle_action(MOD, CONFIG, selected_path, action, questionary, os, shutil, xpaths, xlog)
                
            elif action == "Back" or action == None:
                continue
        
        except Exception as e:
            xlog.log_fail(f"File Actions ERROR: {e}")

def handle_action(MOD, CONFIG, path, action, questionary, os, shutil, xpaths, xlog):
    """
    Handles specific actions for files and folders.
    """
    MEDIA = CONFIG["paths"]["media"]
    path_options = ["Enter own", "Choose interactive from corepath", "Choose interactive from current", "Use corepath", "Back"]
    
    if action == "Rename":
        xlog.log_info("Keep in mind to add the file-extension!")
        new_name = questionary.text("Enter new name:").ask()
        new_path = os.path.join(os.path.dirname(path), new_name)
        os.rename(path, new_path)
        xlog.log_info(f"Renaming: {path}\n    >> To: {new_path}")
        xlog.log_info(f"Renamed to {new_name}")

    elif action == "Delete":
        if questionary.confirm("Are you sure you want to delete this?").ask():
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            xlog.log_info(f"Delete: {path}")
            xlog.log_continue("Deleted successfully.")

    elif action == "Copy":
        path_opt = tools.basic_menu(MOD, path_options, "How to you want to enter the path?")
        if path_opt == "Enter own":
            destination = questionary.text("Enter the path:").ask()
        elif path_opt == "Choose interactive from corepath":
            destination = xpaths.get_path(CONFIG, MOD, MEDIA["core_paths"][default_hostpath], "single")
        elif path_opt == "Choose interactive from current":
            destination = xpaths.get_path(CONFIG, MOD, os.path.dirname(path.rstrip("/")), "single")
        elif path_opt == "Use corepath":
            destination = MEDIA["core_paths"][default_hostpath]
        else:
            xlog.log_info("Quitting")
            return
        xlog.log_info(f"Copying: {path}\n    >> To: {destination}")
        shutil.copy(path, destination)
        xlog.log_continue("Copied successfully.")

    elif action == "Move":
        path_opt = tools.basic_menu(MOD, path_options, "How to you want to enter the path?")
        if path_opt == "Enter own":
            destination = questionary.text("Enter the path:").ask()
        elif path_opt == "Choose interactive from corepath":
            destination = xpaths.get_path(CONFIG, MOD, MEDIA["core_paths"][default_hostpath], "single")
            print(destination)
        elif path_opt == "Choose interactive from current":
            destination = xpaths.get_path(CONFIG, MOD, os.path.dirname(path.rstrip("/")), "single")
        elif path_opt == "Use corepath":
            destination = MEDIA["core_paths"][default_hostpath]
        else:
            xlog.log_info("Quitting")
            return
        xlog.log_info(f"Moving: {path}\n    >> To: {destination}")
        shutil.move(path, destination)
        xlog.log_continue("Moved successfully.")

    elif action == "Show Info":
        file_info = os.stat(path)
        size = xpaths.get_size(path)
        xlog.log_info(
            f"File: {path}\nSize: {round(size / (1024 ** 3), 2)} GB\n"
            f"Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_info.st_mtime))}\n"
            f"Accessed: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_info.st_atime))}"
        )
        xlog.log_continue("Done showing this stuff...")


def change_host(CONFIG):
    """
    Allows the user to select a host from the configuration.
    """
    hosts = list(CONFIG["hosts"].keys())
    host = questionary.select("Select a host:", choices=hosts).ask()
    return host