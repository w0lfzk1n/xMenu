# !/usr/bin/env python3

def runconfig(CONFIG, MOD, args):
    """
    Config Editor. Edits the runtime config and saved the json when editing it.
    :param: CONFIG: The CONFIG object.
    :param: MOD: The MODULES object.
    :param: args: Optional arguments can be ['core', 'cpaths'] a direct route to a specific object/key in the config to start editing it.
    """
    
    global questionary, xlog, xpaths, xjson, changes_made
    
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
    LANG = CONFIG["lang"]

    # Core-Module imports
    pymod = MOD["python"]
    system = MOD["system"]
    utils = MOD["utils"]

    # Libraries and Modules to use
    questionary = pymod["questionary"]
    
    xpaths = utils["xpaths"]
    xjson = utils["xjson"]
    xlog = utils["log"]
    tools = utils["tools"]
    
    header_name = "[ 'root' ]"
    cnf_keys = list(CONFIG.keys())
    cnf_keys.append('>> Exit')
    OLD = CONFIG.copy()
    
    config_defaults = CONFIG["defaults"]
    no_skip = ["core_modulepack", "sub_modulepack", "function_call", "aliases"]
    changes_made = False
    
    def log_header(header):
        global changes_made
        tools.cls()
        xlog.log_header(LANG, MOD)
        xlog.log(f"\nX-Menu Config Editor.\n>> Changes made: {changes_made}\nCurrent location in CONF: {header}\n", LANG, 2, "top")
    
    def edit_config(path=[]):
        header_name = path
        try:
            current = CONFIG
            for key in path:
                print(key)
                current = current[key]
        except KeyError as e:
            xlog.log_error(f"Error: Key {e} not found in configuration.")
            return

        try:
            log_header(header_name)
            options = list(current.keys()) if isinstance(current, dict) else []
            choices = [">> Add Key/Value", ">> Delete Key/Previous Value", ">> List current object"] + options + [">> Exit"]
            selection = questionary.select("Choose an option:", choices=choices).ask()
        except Exception as e:
            xlog.log_error(f"[config-editmenu] Unexpected error: {str(e)}")
            return

        if not selection:
            return

        try:
            if selection == ">> Exit" or selection == None:
                return
            elif selection == ">> Add Key/Value":
                if path and path[-1] in ["cmd", "hosts", "users"]:
                    add_template_entry(current, path[-1])
                else:
                    add_key_value(current)
            elif selection == ">> List current object":
                log_header(header_name)
                xlog.log_json_data(current, LANG)
                xlog.log_continue("Here you go :D")
            elif selection == ">> Delete Key/Previous Value":
                delete_key_value(current)
            elif selection in options:
                if isinstance(current[selection], dict):
                    edit_config(path + [selection])
                else:
                    edit_value(current, selection)
        except KeyError as e:
            xlog.log_error(f"[config-editmenu] Error while modifying configuration: {str(e)}")
        except ValueError as e:
            xlog.log_error(f"[config-editmenu] Value error occurred: {str(e)}")
        except Exception as e:
            xlog.log_error(f"[config-editmenu] An unexpected error occurred: {str(e)}")
        edit_config(path)

    def add_key_value(current):
        global changes_made
        try:
            key_type = questionary.select("Select the type of key to add:", choices=["String", "Array", "Dictionary"]).ask()
            if not key_type:
                xlog.log_error("[config-add] No key type selected. Exiting...")
                return

            use_key = True
            key_name = None
            if key_type == "String":
                use_key = tools.yesno(MOD, "Do you want to use a key to make it an Object? (no: Just add string)")
                if use_key:
                    key_name = questionary.text("Enter the name of the key:").ask()
            else:
                key_name = questionary.text("Enter the name of the key:").ask()
        
            if not key_name and use_key:
                xlog.log_error("[config-add] No key name provided. Exiting...")
                return

            if key_name in current:
                xlog.log_error(f"[config-add] Key '{key_name}' already exists. Exiting...")
                return

            if key_type == "String":
                value = questionary.text("Enter the string value:").ask()
                if value is None:
                    xlog.log_error("[config-add] No string value provided. Exiting...")
                    return
            elif key_type == "Array":
                value = []
                more_items = True
                while more_items:
                    item = questionary.text("Enter a string to add to the array (leave blank to stop):").ask()
                    if item == "":
                        more_items = False
                    else:
                        value.append(item)
            elif key_type == "Dictionary":
                value = {}
            
            if use_key:
                current[key_name] = value
            elif not use_key and isinstance(current, list):
                current.append(value)
            changes_made = True
            
            xlog.log_continue(f"[config-add] New Value as {key_type} has been added! {key_name if use_key else 'NO KEY'}: {value}")
        except Exception as e:
            xlog.log_error(f"[config-add] An unexpected error occurred while adding a key/value: {str(e)}")

    def add_template_entry(current, category):
        global changes_made
        try:
            template = config_defaults.get(category)
            if not template:
                xlog.log_continue(f"[config-add-template] No templates available for the category '{category}'.")
                return

            template_key = questionary.select("Choose a template to use:", choices=list(template.keys())).ask()
            if not template_key:
                xlog.log_error("[config-add-template] No template selected. Exiting...")
                return

            new_entry = template[template_key].copy()
            new_key_name = questionary.text("Enter the name for the new entry:").ask()
            if not new_key_name:
                xlog.log_error("No name for the new entry provided. Exiting...")
                return

            xlog.log_info("Starting to populate the new entry based on the template.\n")

            for key, value in new_entry.items():
                xlog.log_info(f"-- Processing [ {key} ] with default value {value}\n")
                if isinstance(value, list):
                    new_entry[key] = edit_list(value, key)
                elif isinstance(value, bool):
                    options = ["True", "False"]
                    new_value = questionary.select(f"Select new value for *{key}* (current value: {value}):\n", choices=options).ask()
                    new_entry[key] = new_value == "True"
                elif isinstance(value, str):
                    prompt = f"Enter value for {key} (Default: '{value}'): "
                    new_value = questionary.text(prompt, default=value).ask()
                    if not new_value and key in no_skip:
                        xlog.log_info(f"{key} cannot be empty. Re-prompting for input.")
                        while not new_value:
                            new_value = questionary.text(prompt, default=value).ask()
                            
                    if (category == "users" or category == "hosts") and key == "p":
                        new_value = tools.encrypt_string(CONFIG, MOD, new_value)
                    new_entry[key] = new_value if new_value else value
            current[new_key_name] = new_entry
            changes_made = True
            xlog.log_continue(f"New entry '{new_key_name}' added successfully.")
        except KeyboardInterrupt:
            xlog.log_info("[config-add-template] Template filling was canceled by the user.")
        except Exception as e:
            xlog.log_error(f"[config-add-template] ERROR: {e}")

    def edit_list(existing_list, list_key):
        xlog.log_info(f"Editing list for {list_key}. Current items: {existing_list}")
        new_list = existing_list[:]

        try:
            done = False
            while not done:
                choice = questionary.select("Edit list options:", choices=["Add item", "Edit existing item", "Remove item", "Finish editing"]).ask()
                if not choice:
                    xlog.log_error("[config-editListObj] No option selected, exiting...")
                    break

                if choice == "Add item":
                    item = questionary.text("Enter new item:").ask()
                    if item:
                        new_list.append(item)
                    else:
                        xlog.log_info("No item entered. Try again.")

                elif choice == "Edit existing item":
                    if not new_list:
                        xlog.log_error("[config-editListObj] No items in the list to edit.")
                        continue
                    item_to_edit = questionary.select("Select item to edit:", choices=new_list).ask()
                    if item_to_edit:
                        new_item_value = questionary.text(f"Enter new value for item (current value: '{item_to_edit}'):").ask()
                        if new_item_value:
                            index = new_list.index(item_to_edit)
                            new_list[index] = new_item_value
                        else:
                            xlog.log_error("[config-editListObj] No new value entered. Keeping the original value.")
                    else:
                        xlog.log_info("No item selected for editing.")

                elif choice == "Remove item":
                    if not new_list:
                        xlog.log_error("[config-editListObj] No items in the list to remove.")
                        continue
                    item_to_remove = questionary.select("Select item to remove:", choices=new_list).ask()
                    if item_to_remove:
                        new_list.remove(item_to_remove)
                    else:
                        xlog.log_info("[config-editListObj] No item selected for removal.")

                elif choice == "Finish editing":
                    done = True

        except KeyboardInterrupt:
            xlog.log_error("[config-editListObj] List editing was canceled by the user.")
        except Exception as e:
            xlog.log_error(f"[config-editListObj] An unexpected error occurred: {e}")

        return new_list

    def edit_value(current, key):
        global changes_made
        try:
            if isinstance(current[key], list):
                edit_array(current, key)

            elif isinstance(current[key], bool):
                options = ["True", "False"]
                new_value = questionary.select(f"Select new value for {key} (current value: {current[key]}):", choices=options).ask()
                if new_value is None:
                    xlog.log_error("[config-editValue] No selection made. Exiting...")
                    return
                current[key] = new_value == "True"
                changes_made = True

            else:
                new_value = questionary.text(f"Enter new value for {key} (current value: {current[key]}):").ask()
                if new_value is None:
                    xlog.log_error("[config-editValue] No input provided. Exiting...")
                    return
                current[key] = new_value if new_value else current[key]
                changes_made = True
        except Exception as e:
            xlog.log_error(f"[config-editValue] An error occurred while editing the value for {key}: {str(e)}")

    def edit_array(current, key):
        global changes_made
        try:
            while True:
                options = [">> Add Item"] + [f"Edit '{item}'" for item in current[key]] + [">> Delete Item", ">> Back"]
                selection = questionary.select("Choose an option:", choices=options).ask()
                if selection == ">> Back" or not selection or selection == None:
                    xlog.log_error("[config-editArray] Exiting the array editor...")
                    break

                if selection == ">> Add Item":
                    item = questionary.text("Enter a new string to add:").ask()
                    if item:
                        current[key].append(item)
                        changes_made = True
                    else:
                        xlog.log_error("[config-editArray] No item entered. Please try again.")

                elif selection.startswith("Edit '"):
                    item_index = options.index(selection) - 1
                    new_value = questionary.text(f"Enter new value for '{current[key][item_index]}':").ask()
                    if new_value:
                        current[key][item_index] = new_value
                        changes_made = True
                    else:
                        xlog.log_error("[config-editArray] No new value entered. Keeping the original value.")

                elif selection == ">> Delete Item":
                    if current[key]:
                        item_to_delete = questionary.select("Select item to delete:", choices=current[key]).ask()
                        if item_to_delete is not None:
                            current[key].remove(item_to_delete)
                            changes_made = True
                    else:
                        xlog.log_error("[config-editArray] No items available to delete.")
        except Exception as e:
            xlog.log_error(f"An error occurred while editing the array for {key}: {str(e)}")

    def delete_key_value(current):
        global changes_made
        keys = list(current.keys())
        if not keys:
            xlog.log_error("[config-deleteKeyValue] No keys available to delete.")
            return

        key_to_delete = questionary.select("Select the key to delete:", choices=keys).ask()
        if key_to_delete is None:
            xlog.log_error("[config-deleteKeyValue] No key selected. Deletion cancelled.")
            return

        # Detailanzeige des zu löschenden Schlüssels
        value = current[key_to_delete]
        if isinstance(value, str):
            details = f"'{key_to_delete}' is a String."
        elif isinstance(value, list):
            details = f"'{key_to_delete}' is an Array with {len(value)} items."
        elif isinstance(value, dict):
            # Detailanzahl für Dictionaries auf der zweiten Ebene zählen
            sub_key_count = sum(len(current[key_to_delete][sub_key]) if isinstance(current[key_to_delete][sub_key], dict) else 1 for sub_key in current[key_to_delete])
            details = f"'{key_to_delete}' is a Dictionary with {sub_key_count} sub-items."
        else:
            details = f"'{key_to_delete}' has an unsupported type {type(value).__name__}."

        xlog.log_info(details)

        # Erste Bestätigung
        if not tools.yesno(MOD, f"Are you sure you want to delete this key? Details: {details}"):
            xlog.log_info("Deletion cancelled.")
            return

        # Zweite Bestätigung mit zusätzlicher Warnung
        if tools.yesno(MOD, "REALLY REALLY SURE YOU ARE? This action cannot be undone."):
            del current[key_to_delete]
            xlog.log_continue(f"Key '{key_to_delete}' deleted successfully.")
            changes_made = True
        else:
            xlog.log_info("[config-deleteKeyValue] Deletion cancelled.")
    
    while True:
        try:
            log_header(header_name)
            if args:
                edit_config(args[0])
                if changes_made:
                    if tools.yesno(MOD, "Do you want to save the configs?"):
                        xjson.save_config_json(SCRIPT_PATH, CONFIG)
                return
            else:
                opt = tools.basic_menu(MOD, cnf_keys, "Choose a config key:")
                if opt == ">> Exit" or opt == None:
                    if changes_made:
                        if tools.yesno(MOD, "Do you want to save the configs?"):
                            xjson.save_config_json(SCRIPT_PATH, CONFIG)
                    xlog.log_info("Exiting CONFIG Programm!")
                    return
                if opt in cnf_keys:
                    edit_config([opt])
        except Exception as e:
            xlog.log_error(f"[config] ERROR: {e}")
            return


def first_setup(CONFIG, MOD, args=[]):
    global xlog
    """
    Dev command
    """

    # Module imports
    # >> Python libraries
    pymod = MOD["python"]
    # >> modules/system scripts
    system = MOD["system"]
    # >> modules/utils scripts
    utils = MOD["utils"]
    # >> modules/projects scripts
    projects = MOD["projects"]

    os = pymod["os"]
    questionary = pymod["questionary"]
    # Module-Tools to use
    xpaths = utils["xpaths"]
    xjson = utils["xjson"]
    xlog = utils["log"]
    tools = utils["tools"]
    config = system["config"]

    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
    HOSTS = CONFIG["hosts"]
    LANG = CONFIG["lang"]
    bar = LANG["bar2"]
    
    tools.cls()
    xlog.log_header(LANG, MOD)
    xlog.log_continue("Welcome to the first setup of XMENU.\n\nYou will now walk trough some steps to setup this project and the config.\n\nWe will now setup the first 'host', which is the machine you run this project.\nYou can use this project to interact with your other servers via 'ssh' and 'sftp'/'rsync', by adding the hosts later on.\n\nChoose 'Add Key/Value' and select the template.\n\nEnter the name of your host and follow the instructions.\n\nThen 'Exit' and save to come back!\n\n")
    
    config.runconfig(CONFIG, MOD, [["hosts"]])
    
    xlog.log_continue(f"{bar}\n\nWell done my friend! Now lets select the default_host\n\nI don't know, maybe you had the feeling to create more then one...\n\n")
    
    host_keys = list(CONFIG["hosts"].keys())
    default = tools.basic_menu(MOD, host_keys, "Choose your default_host:")
    CONFIG["core"]["default_host"] = default
    
    xlog.log_info(f"{bar}\n\nGreat, you set your default_host to {default}\n\n")
    
    if tools.yesno(MOD, "Do you want to update the 'secret_phrase', which is used to encrypt and decrypt sensitive data like ssh-password.\n(Suggested if first setup)"):
        tools.update_secret_phrase(CONFIG, MOD)
    
    xlog.log_continue(f"{bar}\n\nNow lets set up some of the paths.\n\nFirst let's have a look at the 'core_path' for your host.\n\nThis is the path, that should be used as default starting point, for the 'interactive File/Folder menu'.\n\nExamples:\n  /mnt/\n  /home/user/Desktop/\n")
    
    input_save = ""
    while True:
        core_path = questionary.text(f"Enter the 'core_path' for host [{default}]: ", default=input_save).ask()
        if not xpaths.check_path_exists(core_path):
            xlog.log_info(">> This path is not valid, please make sure to enter it correctly")
            input_save = core_path
            continue
        break
    CONFIG["paths"]["media"]["core_paths"][default] = core_path

    xlog.log_continue(f"{bar}\n\nGreat, you have completed this step, now lets set up some more paths.\n\nThere are 2 types of paths you can save for each host.\n  - 'as_runtime' will be displayed in the most modules when a local path is needed.\n  - 'as_ext_host' -- The paths that can be used, when this host is selected as 'external' destination for 'sftp' or 'rsync'.\n\nLet's first setup the 'as_runtime' paths, here you can save paths to your stuff\n\n")
    
    valid_paths = []
    while True:
        hostpaths_runtime = tools.create_object(MOD, CONFIG, "arr")
        if not hostpaths_runtime:
            xlog.log_continue("No No No, you have to enter at least one path man. . .")
            continue
        
        all_paths_valid = True
        for path in hostpaths_runtime:
            if not xpaths.check_path_exists(path):
                xlog.log_continue(f"No NO NO! Path: {path} is not valid . . .")
                response = input("Do you want to edit it (e) or delete it (d)? ")
                if response.lower() == 'e':
                    new_path = input("Enter the new path: ")
                    if xpaths.check_path_count(new_path):
                        xlog.log_continue(f"Path updated to: {new_path}")
                        valid_paths.append(new_path)
                    else:
                        xlog.log_continue("Still not a valid path, it will be ignored.")
                elif response.lower() == 'd':
                    xlog.log_continue("Path deleted.")
                continue
            valid_paths.append(path)
        
        if all_paths_valid:
            break

    CONFIG["hosts"][default]["paths"]["as_runtime"] = valid_paths
    
    xlog.log_continue(f"{bar}\n\nGreat Job! Now the basics are done. You can now run 'conf' and edit the 'paths' or any other config key as you wish.\n\n")

    if tools.yeasno(MOD, "Do you want to setup the 'as_ext_host' paths too?").ask():
        valid_ext_host_paths = []
        while True:
            hostpaths_exthost = tools.create_object(MOD, CONFIG, "arr")
            if not hostpaths_exthost:
                xlog.log_continue("No No No, you have to enter at least one path man. . .")
                continue
            
            all_paths_valid = True
            for path in hostpaths_exthost:
                if not xpaths.check_path_exists(path):
                    xlog.log_continue(f"No NO NO! Path: {path} is not valid . . .")
                    response = input("Do you want to edit it (e) or delete it (d)? ")
                    if response.lower() == 'e':
                        new_path = input("Enter the new path: ")
                        if xpaths.check_path_exists(new_path):
                            xlog.log_continue(f"Path updated to: {new_path}")
                            valid_ext_host_paths.append(new_path)
                        else:
                            xlog.log_continue("Still not a valid path, it will be ignored.")
                            all_paths_valid = False
                    elif response.lower() == 'd':
                        xlog.log_continue("Path deleted.")
                    continue
                valid_ext_host_paths.append(path)
            
            if all_paths_valid:
                break

        CONFIG["hosts"][default]["paths"]["as_ext_host"] = valid_ext_host_paths

    print(f"\n{bar}\n")

    if tools.yesno(MOD, "This project offers a YouTube downloader (which works for more than just YouTube). Do you want to set up the paths for it too?").ask():
        valid_ytdl_paths = []
        while True:
            ytdl_paths = tools.create_object(MOD, CONFIG, "arr")
            if not ytdl_paths:
                xlog.log_continue("No No No, you have to enter at least one path man. . .")
                continue
            
            all_paths_valid = True
            for path in ytdl_paths:
                if not xpaths.check_path_exists(path):
                    xlog.log_continue(f"No NO NO! Path: {path} is not valid . . .")
                    response = input("Do you want to edit it (e) or delete it (d)? ")
                    if response.lower() == 'e':
                        new_path = input("Enter the new path: ")
                        if xpaths.check_path_exists(new_path):
                            xlog.log_continue(f"Path updated to: {new_path}")
                            valid_ytdl_paths.append(new_path)
                        else:
                            xlog.log_continue("Still not a valid path, it will be ignored.")
                            all_paths_valid = False
                    elif response.lower() == 'd':
                        xlog.log_continue("Path deleted.")
                    continue
                valid_ytdl_paths.append(path)
            
            if all_paths_valid:
                break
        
        CONFIG["paths"]["media"]["ytd_save_paths"] = valid_ytdl_paths
    
    xjson.save_config_json(SCRIPT_PATH, CONFIG)
    
    xlog.log_continue("Congrats! You have completed the Setup! You will now return to the main project.")
    return
