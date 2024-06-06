# !/usr/bin/env python3

def get_files_by_extension(path, valid_extensions):
    available_extensions = set()
    files = []

    for ext in valid_extensions:
        matched_files = glob.glob(os.path.join(path, f"*{ext}"))
        files.extend(matched_files)

        if matched_files:
            available_extensions.add(ext)

    return files, available_extensions


def blkrename(CONFIG, MOD, folder_path=[None]):
    global os, glob
    # ModuleCores
    pymod = MOD["python"]
    utils = MOD["utils"]

    os = pymod["os"]
    glob = pymod["glob"]
    questionary = pymod["questionary"]

    xlog = utils["log"] 
    xpaths = utils["xpaths"]
    xpaths = utils["xpaths"]
    tools = utils["tools"]

    LANG = CONFIG["lang"]
    MEDIA = CONFIG["paths"]["media"]
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]

    if len(MEDIA["core_paths"]) == 0:
        xlog.log_error("You have not configured 'core_paths' in the 'paths' config!")
        return

    xlog.log_info("If the host you are on is not listed, run 'conf' and edit the 'core_paths' in the 'lang' config!")
    host = questionary.select("Choose the host you are on:", choices=list(MEDIA["core_paths"])).ask()
    base_path = MEDIA["core_paths"][host]

    valid_extensions = MEDIA["valid_rename_extensions"]
    exclude_parts = MEDIA["rename_exclude_part"]

    xlog.log_bar(LANG, 2)
    xlog.log_info("Configfile core path: python_data/core_conf.json")
    xlog.log_info("Otherwise you can type in the full path manually.")
    xlog.log_info(f"BasePath from configfile: {base_path}\n")
    use_core = tools.yesno(MOD, f">> Do you want to use the base path or enter your own?")
    if use_core:
        base_path = base_path
    else:
        while True:
            base_path = xlog.log_input("Enter a path")
            if not os.path.exists(base_path):
                xlog.log_info("The given path does not exist!")
    
    if not len(folder_path) > 1:
        folder_path = None
    else:
        folder_path = folder_path[1]

    while True:
        if folder_path == None:
            folder_path = xpaths.get_path(CONFIG, MOD, base_path, "single")
            print(folder_path)
            print(folder_path[0])

            if folder_path == None:
                xlog.log_info("Exiting BLK-Renamer...")
                return
            
        folder_path = xpaths.format_path(folder_path)

        if not os.path.exists(folder_path):
            xlog.log_error(f">> Path '{folder_path}' does not exist. Please try again.")
            return

        else:
            xlog.log_success(f">> Path '{folder_path}' is valid")
            break

    while True:
        xlog.log(
            "\nBLK-Renamer Options\n1) Own Name\n2) Random Name\n3) Random Nature Name\n4) Random Tec Name\n5) Random Myth Name\n6) Random Space Name",
            LANG,
            2,
            "top",
        )
        names = xlog.log_input("Choice: ")
        if names in ["1", "2", "3", "4", "5", "6"]:
            break
        xlog.log_error("Wrong Input. Please enter between 1 and 6.")

    files = []
    for ext in valid_extensions:
        files.extend(
            glob.glob(xpaths.format_path(os.path.join(folder_path, f"*{ext}")))
        )

    # Hole Dateien und verfügbare Erweiterungen
    files, available_extensions = get_files_by_extension(folder_path, valid_extensions)

    xlog.log_bar(LANG, 2)
    for i, ext in enumerate(valid_extensions):
        print(f"-- {ext}")
    xlog.log_bar(LANG, 2)
    xlog.log_info("Available extensions in the directory:")
    for i, ext in enumerate(available_extensions):
        print(f"{i}: {ext}")

    chosen_extension_indexes = []
    while True:
        chosen_extension_indexes = xlog.log_input(
            "Choose one or more extensions by index (comma-separated): "
        ).split(",")
        valid_input = True
        for index in chosen_extension_indexes:
            index = index.strip()
            if not index.isdigit() or int(index) not in range(len(available_extensions)):
                valid_input = False
                break
        if valid_input:
            break
        else:
            xlog.log_error("Invalid input. Please enter valid extension index(es).")

    valid_indexes = [
        int(index.strip())
        for index in chosen_extension_indexes
        if index.strip().isdigit()
        and int(index.strip()) in range(len(available_extensions))
    ]
    chosen_extensions = [list(available_extensions)[index] for index in valid_indexes]

    files = [
        file for file in files if any(file.endswith(ext) for ext in chosen_extensions)
    ]

    if names == "1":
        name = xlog.log_input("Name for files: ")

        start_counting_at = xlog.log_input(
            "Do you want to start counting at a specific number? (y/n): "
        ).lower() in ["y", "yes", "j", "ja"]

        owncounter = 0
        file_cnt = 0

        if start_counting_at:
            try:
                file_cnt = int(xlog.log_input("Start counting at: "))
            except ValueError:
                xlog.log_info("Invalid input. Counting from 0.")
                file_cnt = 0

    for file in files:
        if any(part in file for part in exclude_parts):
            trigger_part = [part for part in exclude_parts if part in file][0]
            if trigger_part == "-poster":
                os.remove(file)
                xlog.log_info(
                    f">> Deleted File [ {os.path.basename(file)} ] due {trigger_part}"
                )
            else:
                xlog.log_info(
                    f">> Skipped File [ {os.path.basename(file)} ] due {trigger_part}"
                )
            continue

        if names == "1":
            random_word = name + str(file_cnt)
            file_cnt += 1
            owncounter += 1
        elif names == "2":
            random_word = tools.gen_name(SCRIPT_PATH, CONFIG, MOD, "full")[0]
        elif names == "3":
            random_word = tools.gen_name(SCRIPT_PATH, CONFIG, MOD, "nature")[0]
        elif names == "4":
            random_word = tools.gen_name(SCRIPT_PATH, CONFIG, MOD, "tec")[0]
        elif names == "5":
            random_word = tools.gen_name(SCRIPT_PATH, CONFIG, MOD, "myth")[0]
        elif names == "6":
            random_word = tools.gen_name(SCRIPT_PATH, CONFIG, MOD, "space")[0]

        file_name, file_extension = os.path.splitext(file)
        nfo_file = file_name + '.nfo'
        if os.path.exists(nfo_file):
            new_nfofile_name = os.path.join(
                os.path.dirname(nfo_file), f"{random_word}.nfo"
            )
            os.rename(nfo_file, new_nfofile_name)
            xlog.log_info(">> Renamed NFO")
            
        poster_file = file_name + '-poster.jpg'
        if os.path.exists(poster_file):
            new_posterfile_name = os.path.join(
                os.path.dirname(poster_file), f"{random_word}-poster.jpg"
            )
            os.rename(poster_file, new_posterfile_name)
            xlog.log_info(">> Renamed Poster")
        
        new_file_name = os.path.join(
            os.path.dirname(file), f"{random_word}{file_extension}"
        )
        os.rename(file, new_file_name)
        
        xlog.log_info(
            f">> File [ {os.path.basename(file)} ] >> [ {os.path.basename(new_file_name)} ]"
        )
        
    xlog.log_info(">> Done :) Bye")
    xlog.log_bar(LANG, 2)
    return