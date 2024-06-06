from random import randint

def get_folder_path(CONFIG, MOD, core_path):
    while True:
        # folder_paths_input = input("Enter the Path(s) to the Mediafiles (separated by commas): ")
        #folder_paths = [xpaths.format_path(path.strip()) for path in folder_paths_input.split(",")]
        folder_paths = xpaths.get_path(CONFIG, MOD, core_path, "multi")
        
        if not folder_paths or folder_paths == None:
            return None
        
        if not all(folder_paths):
            xlog.log_error("Input is not valid! Do it correctly.")
            continue
        
        invalid_paths = [path for path in folder_paths if not os.path.isdir(path)]
        if invalid_paths:
            xlog.log_error("These are not valid 'folder'-paths: {}".format(", ".join(invalid_paths)))
            continue
        
        num_files = []
        for folder_path in folder_paths:
            folder_files = [filename for filename in os.listdir(folder_path) if os.path.splitext(filename)[1].lower() in extensions and not any(skip_part in filename for skip_part in skip_parts)]
            num_files.append(len(folder_files))
            
        return [folder_paths, num_files]


def get_settings(MOD, curr_settings):
    copy_settings = curr_settings
    options = ["Change mode", "Change Host", "Change Path (set host first)", "Back"]
    try:
        choice = tools.basic_menu(MOD, options, "DupeYeet Settings")
        
        if not choice or choice == "" or choice == "Back":
            return curr_settings
        
        elif choice == "Change mode":
            modes = ["single", "multi"]
            curr_mode = copy_settings["mode"]
            new_mode = tools.basic_menu(MOD, modes, f"Choose the path-selection-mode. (Current: {curr_mode})")
            if not new_mode or new_mode == "" or new_mode == "Back":
                return curr_settings
            copy_settings["mode"] = new_mode
            xlog.log_info(f">> Changed mode to: {new_mode}")
            return copy_settings

        elif choice == "Change Host":
            curr_host = copy_settings["host"]
            new_host = tools.basic_menu(MOD, list(hosts.keys()), f"Choose a saved Host. (Current: {curr_host})")
            if not new_host or new_host == "" or new_host == "Back":
                return curr_settings
            copy_settings["host"] = new_host
            xlog.log_info(f">> Changed host to: {new_host}")
            
            host_paths = hosts[f"{new_host}"]["paths"]["as_runtime"]
            curr_path = copy_settings["path"]
            new_path = tools.basic_menu(MOD, host_paths, f"Choose a saved Path. (Current: {curr_path})")
            if not new_path or new_path == "" or new_path == "Back":
                return curr_settings
            copy_settings["path"] = new_path
            xlog.log_info(f">> Changed path to: {new_path}")
            return copy_settings
        
        elif choice == "Change Path (set host first)":
            curr_host = copy_settings["host"]
            host_paths = hosts[curr_host]["paths"]["as_runtime"]
            curr_path = copy_settings["path"]
            new_path = tools.basic_menu(MOD, host_paths, f"Choose a saved Path. (Current: {curr_path})")
            copy_settings["path"] = new_path
            xlog.log_info(f">> Changed path to: {new_path}")
            return copy_settings
        
    except Exception as e:
        xlog.log_error(f"[dupeyeet-settings] ERROR: {e}")
    
    
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_duplicates(file_hashes, folder_path, filecount):
    total_files = 0
    total_size = 0
    saved_size = 0
    total_dupes = 0
    achievement_trigger = True
    update_threshold_files = max(int(filecount * 0.15), 1)
    update_threshold_dupes = max(int(filecount * 0.05), 1)

    xlog.log(
        f">> Starting Duplicate Search\n>> Folderpath: {folder_path}\n>> We are about to scan [ {filecount} ] files for you!\n>> Update-threshold: Dupes({update_threshold_dupes}) / Files({update_threshold_files})\n>>   PLEASE HOLD ON WHILE WE ARE WORKING ON IT...\n",
        LANG
    )
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isdir(file_path):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in extensions or any(s in filename for s in skip_parts):
            continue
        
        if (total_files % update_threshold_files == 0 and total_files > 0) or (total_dupes % update_threshold_dupes == 0 and total_dupes > 0):
            if total_files % update_threshold_files == 0:
                update_trigger = "File Counter"
            else:
                update_trigger = "Dupe Counter"
            texts = [
    "Yeah, we're working on ya shit!",
    "Calm down brownie, everything is under control!",
    "Sir, put the red button away!",
    "Yep, I am still on it, problems?",
    "Just a small fish in the sea...",
    "We'll be done soon, stop talking!",
    "My hands already hurt and I have dirt in my pants.. Can I have a break please?",
    "I am scanning as fast as I can dude!"
]
            random_text = texts[randint(0, len(texts) - 1)]
            xlog.log_info(f"'{update_trigger}' Update {filecount-(filecount - total_files)+1}/{filecount} | {total_dupes} Dupes | {random_text}")

        if total_dupes == 1 and achievement_trigger:
            achievement_trigger = False
            xlog.log_info(f"First Dupelicate found! | Files: {filecount-(filecount - total_files)+1}/{filecount}")
        elif total_dupes == 5 and achievement_trigger:
            achievement_trigger = False
            xlog.log_info(f"Ok, we found 5 Duplicates so far. | Files: {filecount-(filecount - total_files)+1}/{filecount}")
        elif total_dupes == 10 and achievement_trigger:
            achievement_trigger = False
            xlog.log_info(f"Already 10 Dupelicates found! | Files: {filecount-(filecount - total_files)+1}/{filecount}")
        elif total_dupes == 25 and achievement_trigger:
            achievement_trigger = False
            xlog.log_info(f"Amazing! 25 Dupelicates found! | Files: {filecount-(filecount - total_files)+1}/{filecount}")
        elif total_dupes == 50 and achievement_trigger:
            achievement_trigger = False
            xlog.log_info(f"Wow! 50 Dupelicates found! | Files: {filecount-(filecount - total_files)+1}/{filecount}")
        elif total_dupes == 100 and achievement_trigger:
            achievement_trigger = False
            xlog.log_info(f"No Way! We found 100 Dupelicates! | Files: {filecount-(filecount - total_files)+1}/{filecount}")
        elif total_dupes == 200 and achievement_trigger:
            achievement_trigger = False
            xlog.log_info(f"Uhm, We already found 200 Duplicates... | Files: {filecount-(filecount - total_files)+1}/{filecount}")
        elif total_dupes == 500 and achievement_trigger:
            achievement_trigger = False
            xlog.log_info(f"OMG! 500 Duplicates found!! | Files: {filecount-(filecount - total_files)+1}/{filecount}")
        elif total_dupes == 1000 and achievement_trigger:
            achievement_trigger = False
            xlog.log_info(f"Ough... Did we really just found 1'000 Duplicates? <-< | Files: {filecount-(filecount - total_files)+1}/{filecount}")

        file_size = os.path.getsize(file_path)
        total_files += 1
        total_size += file_size

        file_hash = get_file_hash(file_path)

        if file_hash in file_hashes:
            os.remove(file_path)
            saved_size += file_size
            total_dupes += 1
            achievement_trigger = True
        else:
            file_hashes[file_hash] = filename

    xlog.log(f"         File-Count Before: {total_files}", LANG, 3, "top")
    xlog.log(f"Total-Size Before: {total_size / (1024*1024):.2f} MB\n", LANG)

    total_files_after = total_files - total_dupes
    total_size_after = total_size - saved_size

    xlog.log(f" >> Total Duplikates found: {total_dupes}\n          >> Saved {saved_size / (1024*1024):.2f} MB\n", LANG)

    xlog.log(f"File-Count After: {total_files_after}", LANG)
    xlog.log(f"         Total-Size After: {total_size_after / (1024*1024):.2f} MB", LANG, 3, "bottom")
    xlog.log_input("Please press ENTER to continue...")
    return saved_size


def dupeyeet(CONFIG, MOD, args):
    global os, glob, questionary, hashlib, xlog, xpaths, tools, LANG, extensions, skip_parts, total_saved_space, file_hashes, hosts
    pymod = MOD["python"]
    utils = MOD["utils"]

    os = pymod["os"]
    glob = pymod["glob"]
    questionary = pymod["questionary"]
    hashlib = pymod["hashlib"]
    
    xlog = utils["log"]
    xjson = utils["xjson"]
    xpaths = utils["xpaths"]
    tools = utils["tools"]

    LANG = CONFIG["lang"]
    default_host = CONFIG['core']['default_host']
    hosts = CONFIG["hosts"]
    
    settings = {
        "mode": "multi",
        "host": f"{default_host}",
        "path": f"{CONFIG['paths']['media']['core_paths'][f'{default_host}']}"
    }
    
    folder_path = None
    folder_filecount = None
    
    extensions = [".jpg", ".jpeg", ".png", ".mp4", ".mov", ".m4v", ".mkv", ".gif"]
    skip_parts = ["-poster", ".nfo"]
    total_saved_space = 0
    file_hashes = {}
    
    while True:
        tools.cls()
        xlog.log_header(LANG, MOD)
        xlog.log(f"\nWelcome to Dupe-Checker Tool.\nScan folder with Images or Videos for duplicates using their hashes and remove them.\n\n>> Current Host: {settings['host']}\n\n>> Session Hashlist: {len(file_hashes)} Hashes\n>> Session saved Space: {total_saved_space  / (1024*1024):.2f} MB\n", LANG, 2, "top")
        xlog.log_info(f"Settings:")
        xlog.log_json_data(settings, LANG)
        main_menu_choices = [
            f"[{'NOT SET' if not folder_path else len(folder_path)}] Folder - Select folder",
            "Settings",
            "Reset client",
            "Start Scanning",
            "Exit Programm",
        ]
        selection = questionary.select("MainMenu:", choices=main_menu_choices).ask()
        
        if selection == "Exit Programm" or selection is None:
            xlog.log_info("Program Terminated!")
            return
        
        elif selection == "Reset client":
            xlog.log_info("Resetting client. Clear current hashlist and set 'saved_space' to 0")
            total_saved_space = 0
            file_hashes = {}
            xlog.log_input("Reset done. Press Enter to continue. . .")
        
        elif selection.startswith(f"[{'NOT SET' if not folder_path else len(folder_path)}] Folder - Select folder"):
            folder_data = get_folder_path(CONFIG, MOD, settings["path"])
            if folder_data == None:
                xlog.log_info("No Path set. User exit")
                continue
            folder_path = folder_data[0]
            folder_filecount = folder_data[1]
            if folder_path:
                xlog.log_success(f"We have saved [ {len(folder_path)} ] paths | Files Counted: {sum(folder_filecount)}")
            else:
                xlog.log_fail("No Path set.")

        elif selection.startswith("Settings"):
            settings = get_settings(MOD, settings)
                
        elif selection == "Start Scanning":
            if folder_path:
                i = 0
                for path in folder_path:
                    space_saved = scan_duplicates(file_hashes, path, folder_filecount[i])
                    total_saved_space += space_saved
                    i += 1
            else:
                xlog.log_warning(
                    "Please first set the Source-Path!", LANG
                )