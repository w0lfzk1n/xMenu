# !/usr/bin/env python3

# RSYNC notizen
# -avx = archive, verbose, extended attributes
# --progress = show progress
# --delete = delete extraneous files from dest dirs
# --exclude="/path" = exclude files matching pattern
# --ignore-existing = skip files that exist on receiver

def selectSource():
    torrent_path = source_path
    while True:
        print(f"Current path: {torrent_path}")
        if not os.path.exists(source_path):
            xlog.log_error(f"The chosen source-path [ {source_path} ] does not exist on this system!\nChange the host or core-source-path!")
            xlog.log_input("Press ENTER to continue. . .")
            return None
        files = os.listdir(torrent_path)
        if torrent_path != source_path:
            files = [".."] + files
        files_with_indicators = [
            (
                f"{file}/ (Folder)"
                if os.path.isdir(os.path.join(torrent_path, file))
                else file
            )
            for file in files
        ]
        files_with_indicators.sort()
        files_with_indicators.append("Exit")
        file = questionary.select(
            "Select file to copy", choices=files_with_indicators
        ).ask()
        
        if file == None or file == "":
            return None

        file = file.replace("/ (Folder)", "") if file not in ["Exit", ".."] else file

        if file == "Exit":
            return None 

        if file == "..":
            torrent_path = os.path.dirname(torrent_path.rstrip("/"))
            continue

        selected_path = os.path.join(torrent_path, file)

        if os.path.isdir(selected_path):
            action = questionary.select(
                "Do you want to select this folder or enter it?",
                choices=["Select", "Enter"],
            ).ask()
            if action == "Select":
                return xpaths.format_path(selected_path + "/")
            elif action == "Enter":
                torrent_path = selected_path
        else:
            return xpaths.format_path(
                selected_path
            )

def selectDestination(NETW,CONFIG, MOD):
    global enc_passwd
    host_type = questionary.select(
        "Select destination type:",
        choices=["local host", "extern host"]
    ).ask()

    if host_type == "local host":
        destination_path = destin_path
        while True:
            print(f"Current destination: {destination_path}")
            if not os.path.exists(destination_path):
                xlog.log_error(f"The chosen destination-path [ {destination_path} ] does not exist on this system!\nChange the host or core-destination-path!")
                xlog.log_input("Press ENTER to continue. . .")
                return None
            directories = [
                d
                for d in os.listdir(destination_path)
                if os.path.isdir(os.path.join(destination_path, d))
            ]
            if destination_path != destin_path:
                directories = [".."] + directories
            directories.sort()
            directories.append("Exit")
            choices = [
                "> Continue",
            ] + directories

            selection = questionary.select(
                "Select a folder or action:", choices=choices
            ).ask()

            if selection == "Exit":
                return None

            if selection == "..":
                destination_path = os.path.dirname(destination_path.rstrip("/"))
                continue

            if selection == "> Continue":
                new_folder_name = questionary.text("Enter name for the new folder:").ask()
                if new_folder_name in ["/", "", None, " "]:
                    return xpaths.format_path(destination_path + "/")
                full_path = os.path.join(destination_path, new_folder_name)
                return xpaths.format_path(full_path + "/")

            selected_path = os.path.join(destination_path, selection)

            if os.path.isdir(selected_path):
                action = questionary.select(
                    "Do you want to select this folder or enter it?",
                    choices=["Select", "Enter"],
                ).ask()
                if action == "Select":
                    return xpaths.format_path(selected_path + "/")
                elif action == "Enter":
                    destination_path = selected_path

    elif host_type == "extern host":
        host = questionary.select("Choose host:", choices=list(NETW.keys())).ask()
        if not host:
            return None

        host_ip = tools.basic_menu(MOD, NETW[host]["ipadr"], "Choose a IP of this host:")

        username = questionary.select("Choose saved User:", choices=list(NETW[host]["users"].keys())).ask()
        if not username:
            return None  # Beenden, wenn kein Benutzername ausgewählt wurde
        user = NETW[host]["users"][username]["u"]
        
        if not questionary.confirm("Do you want to use the saved password?").ask():
            enc_passwd = None
        else:
            enc_passwd = tools.decrypt_string(CONFIG, MOD, NETW[host]["users"][username]["p"])
        path_choice = questionary.select(
            "Choose destination path option:",
            choices=["Use Config SFTP Paths", "Enter Own Path"]
        ).ask()

        if path_choice == "Use Config SFTP Paths":
            sftp_paths = NETW[host]["paths"]["as_ext_host"]
            if sftp_paths:
                dest_path = questionary.select("Choose SFTP path:", choices=sftp_paths).ask()
                foldername = xlog.log_input(f"Enter a name for the new folder (Without / at end || Can be empty) {dest_path}")
                if foldername:
                    dest_path = dest_path + foldername + "/"
            else:
                xlog.log_fail("No configured SFTP paths available for this host.")
                return None
        else:
            dest_path = questionary.text("Enter the destination path on the remote server:").ask()
            
        return f"{user}@{host_ip}:{dest_path}"

def interactive_rsync_menu():
    global enc_passwd
    rOptions = {
        "archive": True,  
        "verbose": True,  
        "compress": True, 
        "progress": True, 
        "partial": False,
        "remove-source-files": False,
        "skip-existing": False,
    }

    option_commands = {
        "archive": "--archive",
        "verbose": "--verbose",
        "compress": "--compress",
        "progress": "--progress",
        "partial": "--partial",
        "remove-source-files": "--remove-source-files",
        "skip-existing": "--skip-existing",
    }

    option_descriptions = {
        "archive": "Archivmodus (bewahrt Berechtigungen, Eigentümer, Zeitstempel)",
        "verbose": "Ausführliche Ausgabe",
        "compress": "Komprimiert Dateidaten während der Übertragung",
        "progress": "Zeigt den Fortschritt der Übertragung an",
        "partial": "Erlaubt das Fortsetzen unterbrochener Übertragungen",
        "remove-source-files": "Löscht Quelldateien nach erfolgreicher Übertragung",
        "skip-existing": "Überspringt die Übertragung von Dateien, die im Zielverzeichnis bereits existieren",
    }

    while True:
        choices = [
            questionary.Choice("Start", value="start"),
        ]
        for option, enabled in rOptions.items():
            option_text = f"[{'ON' if enabled else 'OFF'}] {option} >> ({option_descriptions[option]})"
            choices.append(questionary.Choice(option_text, value=option))

        choices.append(questionary.Choice("Exit", value="exit"))

        selection = questionary.select(
            "Choose your RSYNC-Options:", choices=choices
        ).ask()

        if selection == "start":
            break
        elif selection == "exit" or selection is None:
            return
        else:
            rOptions[selection] = not rOptions[selection]

    xlog.log_info("Chosen RSYNC-Options:")
    for option, enabled in rOptions.items():
        if enabled:
            print(f"- {option} ({option_descriptions[option]})")
    execute_rsync(ppath, dpath, rOptions, option_commands)

def execute_rsync(ppath, dpath, rOptions, option_commands):
    global enc_passwd
    command = "rsync"
    for option, enabled in rOptions.items():
        if enabled:
            command += f" {option_commands[option]}"
    command += f' "{ppath}" "{dpath}"'

    if "@" in dpath and enc_passwd:
        password = enc_passwd
        command = f'sshpass -p {password} ' + command

    os.system(command)
    enc_passwd = None
    xlog.log_input("Press ENTER to continue. . .")

def rsync(CONFIG, MOD, args=[]):
    global os, questionary, source_path, destin_path, ppath, dpath, xlog, xpaths, tools, enc_passwd, default_host
    
    pymod = MOD["python"]
    psys = MOD["system"]
    utils = MOD["utils"]

    os = pymod["os"]
    questionary = pymod["questionary"]

    xlog = utils["log"]
    xpaths = utils["xpaths"]
    tools = utils["tools"]

    LANG = CONFIG["lang"]
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
    NETW = CONFIG["hosts"]
    default_hostpath = tools.basic_menu(MOD, NETW.keys(), f"Select the host you are on (Enter to use Default: {CONFIG['core']['default_host']}):")
    if not default_hostpath:
        default_hostpath = CONFIG["core"]["default_host"]
    
    source_path = tools.basic_menu(MOD, NETW[f"{default_hostpath}"]["paths"]["as_runtime"], "Choose a Source Path:")
    if not source_path:
        xlog.log_error("RSYNC Canvelled by user.")
        return
    destin_path = tools.basic_menu(MOD, NETW[f"{default_hostpath}"]["paths"]["as_ext_host"], "Choose a Destination Path:")
    if not destin_path:
        xlog.log_error("RSYNC Canvelled by user.")
        return
    
    enc_passwd = None

    ppath = None
    dpath = None

    while True:
        tools.cls()
        xlog.log_header(LANG, MOD)
        xlog.log(f"\nWelcome to RSYNC / ZIP Tool.\n\nSet Host to: {default_hostpath}\n", LANG, 2, "top")

        main_menu_choices = [
            "Start RSYNC",
            "Set Host",
            "Set core-paths",
            f"[{'NOT SET' if not ppath else ppath}] - SOURCE-Path",
            f"[{'NOT SET' if not dpath else dpath}] - DESTINATION-Path",
            "Exit Programm",
        ]
        selection = questionary.select("MainMenu:", choices=main_menu_choices).ask()

        if selection.startswith(f"[{'NOT SET' if not ppath else ppath}] - SOURCE-Path"):
            ppath = selectSource()
            if ppath:
                xlog.log_success(f"Set Source-Path: {ppath}")
            else:
                xlog.log_fail("No Path set.")

        elif selection.startswith(
            f"[{'NOT SET' if not dpath else dpath}] - DESTINATION-Path"
        ):
            dpath = selectDestination(NETW, CONFIG, MOD)
            if dpath:
                xlog.log_success(f"Set Destination-Path: {dpath}")
            else:
                xlog.log_fail("No Path set.")

        elif selection == "Start RSYNC":
            if ppath and dpath:
                interactive_rsync_menu()
            else:
                xlog.log_warning(
                    "Please first set the Source and Destiantion-Path!", LANG
                )

        elif selection == "Set Host":
            xlog.log_info("Setting Host Path Value.\n>> This changes the settings for the Corepath for the folder/file selection for RSYNC.")
            HPselection = questionary.select("Set Host to:", choices=NETW.keys()).ask()
            
            if HPselection == "Back" or HPselection == "" or HPselection == None:
                xlog.log_info("No changes where made...")
            else:
                default_hostpath = HPselection
                source_path = tools.basic_menu(MOD, NETW[f"{HPselection}"]["paths"]["as_runtime"], "Choose a Source Path")
                destin_path = tools.basic_menu(MOD, NETW[f"{HPselection}"]["paths"]["as_ext_host"], "Choose a Destination Path")
                xlog.log_info(f"Set Host paths for Host: {HPselection}")

        elif selection == "Set core-paths":
            if tools.yesno(MOD, "Do you want to set a new host?"):
                default_hostpath = tools.basic_menu(MOD, NETW.keys(), "Select the host you are on:")
            if tools.yesno(MOD, "Do you want to set a source_path from the hosts saved paths?"):
                source_path = tools.basic_menu(MOD, NETW[f"{default_hostpath}"]["paths"]["as_runtime"], "Choose a Source Path:")
            if tools.yesno(MOD, "Do you want to set a destination_path from the hosts saved paths?"):
                destin_path = tools.basic_menu(MOD, NETW[f"{default_hostpath}"]["paths"]["as_ext_host"], "Choose a local Destination Path:")

        elif selection == "Exit Programm" or selection is None:
            xlog.log_info("Program Terminated!")
            break