# !/usr/bin/env python3
import os

def format_path(path, base_path=None):
    """
    Formats path to use "/" instead of "\.".
    :param path: Path to format.
    :param base_path: Optional base path to combine with path.
    :return: Formatted path.
    """
    if base_path and base_path != "":
        return os.path.join(base_path, path).replace("\\", "/")
    else:
        return path.replace("\\", "/")

def get_path(CONFIG, MOD, source_path, mode="single"):
    """
    Interactive Menu for selecting a folder, using a root path.
    Also allows to Enter the folder, rather then select one.
    :param MOD: object: Object for the project modules.
    :param source_path: Root-path for selection.
    :return: Formatted path as string or *None* on Exit.
    """
    
    questionary = MOD["python"]["questionary"]
    xpaths = MOD["utils"]["xpaths"]
    xlog = MOD["utils"]["log"]
    tools = MOD["utils"]["tools"]
    
    if not check_path_exists(source_path):
        xlog.log_error(f"Given path not valid: {source_path}")
        return None
    
    LANG = CONFIG["lang"]
    
    runtime_path = source_path 
    selected_paths = []
    
    while True:
        try:
            tools.cls()
            xlog.log_header(LANG, MOD)
            xlog.log(f"\nFolder & File Selector.\n\nCurrent path: {runtime_path}\nSelected Paths: {len(selected_paths)}\n", LANG, 2, "top")

            files = os.listdir(runtime_path)

            if runtime_path != source_path:
                files = [".."] + files

            files_with_indicators = [
                (
                    f"[v] {file}/ (Folder)" if os.path.join(runtime_path, file) in selected_paths
                    else f"{file}/ (Folder)"
                )
                if os.path.isdir(os.path.join(runtime_path, file))
                else f"[v] {file}"
                if os.path.join(runtime_path, file) in selected_paths
                else file
                for file in files
            ]
            files_with_indicators.sort()
            files_with_indicators.append(">> Confirm Multi-Select")
            files_with_indicators.append(">> Exit")
            
            file = questionary.select(
                "Select a File or Folder:", choices=files_with_indicators
            ).ask()
            if file is None or file == "":
                return None

            file = file.replace("/ (Folder)", "").replace("[v] ", "") if file not in ["Exit", ".."] else file

            if file == ">> Exit" or file == None or file == "":
                return None
            if file == ">> Confirm Multi-Select":
                return [xpaths.format_path(path) for path in selected_paths]

            if file == "..":
                runtime_path = os.path.dirname(runtime_path.rstrip("/"))
                continue

            selected_path = os.path.join(runtime_path, file)

            if os.path.isdir(selected_path):
                action = questionary.select(
                    "Do you want to select this folder or enter it?",
                    choices=["Enter", "Select"],
                ).ask()
                
                if action == "Select":
                    if mode == "multi":
                        # Toggle path selection
                        if selected_path in selected_paths:
                            selected_paths.remove(selected_path)
                        else:
                            selected_paths.append(selected_path)
                    elif mode == "single":
                        return selected_path
                elif action == "Enter":
                    runtime_path = selected_path
                    
            else:
                if mode == "multi":
                    # Toggle path selection
                    if selected_path in selected_paths:
                        selected_paths.remove(selected_path)
                    else:
                        selected_paths.append(selected_path)
                elif mode == "single":
                    return selected_path

        except Exception as e:
            xlog.log_fail(f"xPaths Select ERROR: {e}")
            return None

def get_filepath(CONFIG, MOD, source_path, mode="single"):
    """
    Interactive Menu for selecting a file, using a root path.
    Automatically enters directories rather than selecting them.
    :param MOD: object: Object for the project modules.
    :param source_request: string: Root-path for selection.
    :return: A string of the selected file path or None on Exit.
    """
    
    questionary = MOD["python"]["questionary"]
    xpaths = MOD["utils"]["xpaths"]
    xlog = MOD["utils"]["log"]
    tools = MOD["utils"]["tools"]
    
    if not check_path_exists(source_path):
        xlog.log_error(f"Given path not valid: {source_path}")
        return None
    
    LANG = CONFIG["lang"]
    
    runtime_path = source_path 
    selected_paths = []
    
    while True:
        try:
            tools.cls()
            xlog.log_header(LANG, MOD)
            xlog.log(f"\nFile Selector.\n\nCurrent path: {runtime_path}\nSelected Paths: {len(selected_paths)}\n", LANG, 2, "top")

            files = os.listdir(runtime_path)

            if runtime_path != source_path:
                files = [".."] + files

            files_with_indicators = [
                f"{file}" if os.path.isfile(os.path.join(runtime_path, file))
                else f"{file}/ (Folder)"
                for file in files
            ]

            files_with_indicators.append(">> Confirm Multi-Select")
            files_with_indicators.append(">> Exit")
            
            choice = questionary.select(
                "Select a File or navigate a Folder:", choices=files_with_indicators
            ).ask()

            if choice in [None, ">> Exit"]:
                return None

            # Handling directory navigation and file selection
            choice = choice.replace("[v] ", "")
            if choice == "..":
                runtime_path = os.path.dirname(runtime_path)
                continue

            selected_path = os.path.join(runtime_path, choice.replace("/ (Folder)", ""))

            if os.path.isdir(selected_path):
                runtime_path = selected_path
                continue

            if mode == "multi":
                if selected_path in selected_paths:
                    selected_paths.remove(selected_path)
                else:
                    selected_paths.append(selected_path)
            elif mode == "single":
                return selected_path

        except Exception as e:
            xlog.log_fail(f"xPaths Select ERROR: {e}")
            return None

def get_size(file_path):
    if os.path.isfile(file_path):
        return os.path.getsize(file_path)
    elif os.path.isdir(file_path):
        total_size = 0
        for root, dirs, files in os.walk(file_path):
            for f in files:
                file_path = os.path.join(root, f)
                total_size += os.path.getsize(file_path)
        return total_size
    return 0


def check_path_exists(path):
    """
    Checks if path exists.
    :param path: Path to check.
    :return: True if exists, False otherwise.
    """
    if os.path.exists(path):
        return True
    else:
        return False
