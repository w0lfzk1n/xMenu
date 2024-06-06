# !/usr/bin/env python3

def display_paths(paths):
    xlog.log_info("Savepaths:")
    for index, path in enumerate(paths):
        print(f"  {index}: {path}")


def add_path(CONFIG, MOD):
    new_path = xpaths.get_path(CONFIG, MOD, base_path, "single")
    if new_path == None:
        xlog.log_warn("No new Path has been entered. No save done")
        return

    create_newdir = tools.yesno(MOD, "Create new folder?")
    if create_newdir:
        result = tools.create_folder(CONFIG, MOD, [new_path])
        if result:
            new_path = result

    CONFIG["paths"]["media"]["ytd_save_paths"].append(new_path.replace(base_path, ""))
    xjson.save_config_json(SCRIPT_PATH, CONFIG)

    xlog.log_continue(f"Added new savepath: {new_path}")


def edit_path(CONFIG):
    display_paths(CONFIG["paths"]["media"]["ytd_save_paths"])
    index = int(xlog.log_input("Choose the number for editing the path"))
    if index < 0 or index > len(CONFIG["paths"]["media"]["ytd_save_paths"]) - 1:
        xlog.log_error("Invalid index.")
        return
    new_path = questionary.text("Enter the new Value", default=CONFIG["paths"]["media"]["ytd_save_paths"][index]).ask()
    if not new_path:
        xlog.log_continue("No new value entered, exit Edit Config. . .")
        return
    CONFIG["paths"]["media"]["ytd_save_paths"][index] = xpaths.format_path(new_path)
    xjson.save_config_json(SCRIPT_PATH, CONFIG)
    xlog.log_success(f"Edited path: {new_path}")


def delete_path(CONFIG):
    display_paths(CONFIG["paths"]["media"]["ytd_save_paths"])
    index = int(xlog.log_input("Choose the number for deleting the path"))
    if index < 0 or index > len(CONFIG["paths"]["media"]["ytd_save_paths"]) - 1:
        xlog.log_error("Invalid index.")
        return
    del CONFIG["paths"]["media"]["ytd_save_paths"][index]
    xjson.save_config_json(SCRIPT_PATH, CONFIG)
    xlog.log_success(f"Deleted path index: {index}")


def add_encr_link(CONFIG, MOD):
    tools = MOD["utils"]["tools"]
    while True:
        link = xlog.log_input("Enter link")

        if not tools.is_valid_url(link):
            xlog.log_error("Invalid URL.")
            continue
        else:
            xlog.log_info(">> Link is valid.")
            break
    save_encrypted_link(CONFIG, MOD, link)
    xlog.log_success("Link saved.")


def manage_paths(CONFIG, MOD):
    while True:
        tools.cls()
        xlog.log_header(LANG, MOD)
        display_paths(PATHS)
        xlog.log_bar(LANG, 2)
        try:
            options = {
                "1": "add_path",
                "2": "create_folder",
                "3": "edit_path",
                "4": "delete_path",
                "5": "update_secret_phrase",
                "6": "add_encr_link",
                "7": "open_txtfile",
                "8": "exit",
            }
            xlog.log(f"# CONFIG #\n", LANG)
            xlog.log("Options:", LANG)
            xlog.log("1: Add new save path", LANG)
            xlog.log("2: Create a folder", LANG)
            xlog.log("3: Edit a save path", LANG)
            xlog.log("4: Delete a save path", LANG)
            xlog.log("5: Secret phrase refresh", LANG)
            xlog.log("6: Add a Single Encrypted Link", LANG)
            xlog.log("7: Open Link File", LANG)
            xlog.log("8: Back", LANG)
            choice = xlog.log_input("Choose your option: ")
            if choice in options:
                if choice == "8" or str(choice) == "" or choice == None or str(choice).lower() in ["exit", "back"]:
                    break
                else:
                    if choice == "1":
                        add_path(CONFIG, MOD)
                    elif choice == "2":
                        tools.create_folder(CONFIG, MOD)
                    elif choice == "3":
                        edit_path(CONFIG)
                    elif choice == "4":
                        delete_path(CONFIG)
                    elif choice == "5":
                        tools.update_secret_phrase(CONFIG, MOD)
                        xlog.log_continue("Secret for En- and Decryption has been updatet. Keep in mind that now saved things like SSH-Passwords and Links for YTDL cannot be decrypted anymore!")
                    elif choice == "6":
                        add_encr_link(CONFIG, MOD)
                    elif choice == "7":
                        tools.open_txtfile(MOD, [LNK_PTH])
            else:
                print("Invalid Option.")
        except KeyboardInterrupt:
            break


def save_encrypted_link(CONFIG, MOD, link):
    encrypted_link = tools.encrypt_string(CONFIG, MOD, link)
    with open(LNK_PTH, "a") as file:
        file.write(encrypted_link + "\n")
    xlog.log_continue(">> Encrypted link has been saved to textfile.")


def is_hashed_link(link):
    return link.startswith(ENC_TAG)


def download_files(SCRIPT_PATH, CONFIG, MOD, links):
    global cnt_failed, cnt_success
    bar4 = LANG["bar4"]
    processed_links = 0
    total_links = len(links)
    for link in links:
        if link:
            processed_links += 1
            xlog.log_info(f"[{processed_links}/{total_links}] Processing links...")
            if is_hashed_link(link):
                xlog.log_info(f">> {ENC_TAG} - Encrypted link found!")
                link = tools.decrypt_string(SCRIPT_PATH, CONFIG, MOD, link)
                is_valid = tools.is_valid_url(link)
                if not is_valid:
                    xlog.log_info(f">> {ENC_TAG} - Decrypted link is not valid!")
                    continue
                xlog.log_info(f">> {ENC_TAG} - Successful! Decrypted link!")
            elif not tools.is_valid_url(link):
                xlog.log_info(f">> Invalid link: {link}")
                continue
            xlog.log_info(">> Link is valid.")
            if processed_links - 1 % 3 == 0 and processed_links != 1:
                xlog.log_info(
                    f">> WAITING 30 seconds now, processed {processed_links} Links."
                )
                time.sleep(30)

            start_time = datetime.datetime.now()
            filename = tools.gen_name(CONFIG, MOD)[0] + ".mp4"
            cmd = "youtube-dl -o " + os.path.join(save_path, filename) + " " + link
            xlog.log_info(">> CMD: " + cmd)
            result = call(cmd.split(" "))
            end_time = datetime.datetime.now()
            if result != 0:
                failed_downloads.append(link)
                res_ok = "FAILED"
                cnt_failed += 1
            elif result == 0:
                res_ok = "OK"
                cnt_success += 1
            detail_string = f"{bar4}\nStatus: {res_ok}\nN° {processed_links}/{total_links}\nLink: {link}\nPath: {os.path.join(save_path, filename)}\nStart: {start_time}\nEnd  : {end_time}\n"
            less_detail_string = f"{bar4}\nStatus: {res_ok}\nN° {processed_links}/{total_links}\nLink: {link}\nStart: {start_time}"
            download_details.append(less_detail_string)
            print(detail_string)
    print(LANG["bar2"])


def cleanerf(paths):
    xlog.log("Cleaner Started", LANG, 2, "top")
    for path in paths:
        if os.path.exists(path):
            xlog.log(
                f"    # $ CLEANING {os.path.basename(os.path.normpath(path))}",
                LANG,
                4,
                "top",
            )
            part_files = glob.glob(os.path.join(path, "*.part")) + glob.glob(
                os.path.join(path, "*.ytdl")
            )

            if part_files:
                xlog.log_info("     #> Detected *.part or *.ytdl File(s) !")
                for part_file in part_files:
                    try:
                        os.remove(part_file)
                        xlog.log_success(f"     #> Deleted {part_file}")
                    except OSError as e:
                        xlog.log_fail(f"     #> Error deleting {part_file}: {e}")
            else:
                xlog.log_info("     #> NO *.part or *.ytdl Files FOUND!")

    xlog.log(f"     CLEANER FINISHED", LANG, 2)
    xlog.log_input("Press ENTER to continue. . .")


# ============================
# MAIN
# ============================


def ytdl(CONFIG, MOD, args=[]):
    global PATHS, LANG, SCRIPT_PATH, LNK_PTH, xlog, xpaths, xjson, tools, os, random, string, glob, base64, questionary, time, datetime, call, save_path, download_details, failed_downloads, cnt_success, cnt_failed, cnt_retry_fail, cnt_retry_suc, SECRET_KEY, ENC_TAG, base_path
    """
    Runs the YouTube DL Module.
    """

    LANG = CONFIG["lang"]
    MEDIA = CONFIG["paths"]["media"]
    PATHS = MEDIA["ytd_save_paths"]

    LNK_PTH = MEDIA["ytd_path"] + "links.txt"
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]

    # ModuleCores
    pymod = MOD["python"]
    utils = MOD["utils"]

    # Imported Modules
    os = pymod["os"]
    time = pymod["time"]
    datetime = pymod["datetime"]
    random = pymod["random"]
    string = pymod["string"]
    glob = pymod["glob"]
    base64 = pymod["base64"]
    questionary = pymod["questionary"]

    call = pymod["subprocess.call"]

    xlog = utils["log"]
    xpaths = utils["xpaths"]
    xjson = utils["xjson"]
    tools = utils["tools"]

    xlog.log_info("If the host you are on is not listed, run 'conf' and edit the 'core_paths' in the 'lang' config!")
    host = questionary.select("Choose the host you are on:", choices=list(MEDIA["core_paths"].keys())).ask()

    base_path = MEDIA["core_paths"][host]
    SECRET_KEY = CONFIG["core"]["coredata"]["secret_phrase"]
    ENC_TAG = CONFIG["core"]["coredata"]["enc_tag"]

    failed_downloads = []
    download_details = []
    cnt_success = cnt_failed = cnt_retry_suc = cnt_retry_fail = 0
    save_paths = [
        xpaths.format_path(path, base_path) for path in PATHS
    ]

    # If os is windows, return. Not supported.
    if os.name == "nt":
        xlog.log_fail("Windows is not supported.")
        # return

    # ===========================================
    #   Start Actual Skript
    while True:
        try:
            tools.cls()
            xlog.log_header(LANG, MOD)
            xlog.log_bar(LANG, 2)
            xlog.log_info(">> YouTube DL Started")
            xlog.log_info(">> Choose a path where the files should be saved. (Set up in config)")
            for i, path in enumerate(save_paths):
                if os.path.exists(path):
                    file_count = 0
                    need_cleanup = False

                    for file in os.listdir(path):
                        if not file.endswith("-poster.jpg"):
                            file_count += 1
                        if file.endswith(".part") or file.endswith(".ytdl"):
                            need_cleanup = True

                    status = "NeedCleanup" if need_cleanup else "Clean"
                    xlog.log(
                        f"    -> {i}: /{str(file_count).rjust(4)} files {status}/ {os.path.basename(os.path.normpath(path)).ljust(20)}",
                        LANG,
                    )

                else:
                    xlog.log(
                        f"    -> {i}: Path does not exist / {os.path.basename(os.path.normpath(path))}",
                        LANG,
                    )
            xlog.log(f"     -> {len(save_paths)}: # CLEANER #", LANG)
            xlog.log(f"     -> {len(save_paths)+1}: # CONFIG #", LANG)
            xlog.log(f"     -> {len(save_paths)+2}: # EXIT #", LANG)

            while True:
                try:
                    index = int(xlog.log_input(">> Enter index of desired save path: "))
                    if index < 0 or index > len(save_paths) + 2:
                        raise ValueError
                    break
                except ValueError:
                    print(">!! Invalid Input!")

            if index == len(save_paths) + 2 or str(index) == "" or index == None or str(index).lower() in ["exit", "back"]:
                xlog.log_info("Exiting YouTube DL")
                return

            elif index == len(save_paths):
                cleanerf(save_paths)
                continue

            elif index == len(save_paths) + 1:
                manage_paths(CONFIG, MOD)
                continue

            save_path = save_paths[index]

            file_epened = tools.open_txtfile(MOD, [LNK_PTH])

            if not file_epened:
                xlog.log_fail("No links.txt found.")
                return

            xlog.log_info(f">> Started downloading videos to {save_path}")

            with open(LNK_PTH, "r") as file:
                try:
                    links_read = file.readlines()
                    links = [link.strip() for link in links_read]
                    download_files(SCRIPT_PATH, CONFIG, MOD, links)
                except KeyboardInterrupt as e:
                    xlog.log_info("KEYBOARDINTERRUPT.")
                    xlog.log_info("Cleaning up *.part files")
                    cleanerf(save_paths)
                    for detail in download_details:
                        print(detail)
                    return
            os.remove(LNK_PTH)
            if failed_downloads:
                is_fail = True
                len_failed = len(failed_downloads)
                cleaner = tools.yesno(MOD, f">> {len_failed} Downloads Failed. Retry failed downloads?").ask()
                if cleaner:
                    try:
                        download_files(SCRIPT_PATH, CONFIG, MOD, failed_downloads)
                    except KeyboardInterrupt as e:
                        xlog.log_info("KEYBOARDINTERRUPT.")
                        xlog.log_info("Cleaning up *.part files")
                        cleanerf(save_paths)
                        for detail in download_details:
                            print(detail)
                        return

                elif cleaner.lower() in ["n", "nein", "no"]:
                    xlog.log_info(">> Do you want to save the failed downloads to a file?")
                    encryp_save = tools.yesno(MOD, ">> Do you want to save the failed downloads to a file?").ask()
                    if encryp_save:
                        xlog.log_info(">> Start saving encrypted links of failed runs.")
                        for link in failed_downloads:
                            save_encrypted_link(CONFIG, MOD, link)
                            # remove failed link
                            failed_downloads.remove(link)

                        xlog.log_info(">> Successfully saved!")
                    else:
                        pass

            if is_fail:
                f_t = "\n -- Which is recommended since some downloads failed!"
            else:
                f_t = ""
                print("\n")
            cleaner = tools.yesno(MOD, f"\nDownloading finished. Run the cleaner?{f_t}").ask()
            if cleaner:
                cleanerf(save_paths)
            else:
                xlog.log_info("  #### NOT CLEANING UP ####\n\n")

            if failed_downloads:
                encryp_save = tools.yesno(MOD, "Do you want to save the failed downloads to a file?").ask()
                if encryp_save:
                    xlog.log_info(">> Start saving encrypted links of failed runs.")
                    for link in failed_downloads:
                        save_encrypted_link(SCRIPT_PATH, CONFIG, MOD, link)
                        failed_downloads.remove(link)

                    xlog.log_info(">> Successfully saved!")
                else:
                    pass

            for detail in download_details:
                print(detail)

            xlog.log(
                f"FINISHED {len(download_details)} Runs\n{cnt_failed} failed.\n{cnt_success} successful.\nCYA :)",
                LANG,
            )
            break
        except Exception as e:
            xlog.log_error(f"[ytdl] ERROR: {e}")