# !/usr/bin/env python3

def convert_mkv_to_mp4(input_file):
    """
    Main Conversion Function: Converts MKV files to MP4.
    Uses ffmpeg inside a Docker container for the conversion.
    """
    try:
        output_file = input_file.replace('.mkv', '.mp4')
        xlog.log_info(f"Start converting: {input_file} to {output_file}")

        command = [
            'docker', 'run', '--rm',
            '-u', '1000:1000',
            '-v', f"{os.path.dirname(input_file)}:/mnt",
            'jrottenberg/ffmpeg',
            '-i', f"/mnt/{os.path.basename(input_file)}",
            '-codec', 'copy', f"/mnt/{os.path.basename(output_file)}"
        ]
        xlog.log_info(f"Running Docker Command: {command}")
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            xlog.log_info("Media file successfully converted to MP4.")
            os.remove(input_file)
            xlog.log_info("Removed old file and changed ownership of the new file.")
        else:
            error_message = result.stderr.decode('utf-8')
            xlog.log_error(f"Error while converting file {input_file}: {error_message}")

    except Exception as e:
        xlog.log_error(f"An exception occurred while converting {input_file}: {str(e)}")

def mediaconvert(CONFIG, MOD, args):
    """
    Main Menu Function: Handles the user interface for media conversion.
    Provides options to set source path, start conversion, and exit the program.
    """
    global os, xpaths, xlog, tools,  questionary, LANG, subprocess, source_path
    LANG = CONFIG["lang"]
    MEDIA = CONFIG["paths"]["media"]

    pymod = MOD["python"]
    utils = MOD["utils"]

    os = pymod["os"]
    subprocess = pymod["subprocess"]
    questionary = pymod["questionary"]
    tools = utils["tools"]

    xlog = utils["log"]
    xpaths = utils["xpaths"]

    directory = None
    default_hostpath = CONFIG["core"]["default_host"]
    source_path = MEDIA["core_paths"].get(default_hostpath)

    while True:
        try:
            tools.cls()
            xlog.log_header(LANG, MOD)
            xlog.log_info(f"Welcome to Media Convert Tool.\nConverts MKV to MP4.\n!! You need Docker for this to work !!\n\n>> Current Host: {default_hostpath}\n>> Path: {source_path}")

            options = ["Start Process", "Set Host", f"[{'NOT SET' if not directory else directory}] - SOURCE-Path", "Exit"]
            selection = questionary.select("MainMenu:", choices=options).ask()

            if not selection or selection in ["", "Exit", None]:
                xlog.log_info("Exiting Program...")
                break

            elif selection.startswith("[NOT SET] - SOURCE-Path") or selection.endswith("- SOURCE-Path"):
                directory = xpaths.get_path(CONFIG, MOD, source_path, "single")
                if directory:
                    xlog.log_success(f"Set Source-Path: {directory}")
                else:
                    xlog.log_error("No Path set.")

            elif selection == "Start Process":
                if directory:
                    for root, _, files in os.walk(directory):
                        for file in files:
                            if file.endswith('.mkv'):
                                file_path = os.path.join(root, file)
                                convert_mkv_to_mp4(file_path)
                    xlog.log_info("Convert Process completed. Press ENTER to continue...")
                else:
                    xlog.log_info("Please set the Source-Path first!")

            elif selection == "Set Host":
                handle_host_selection(CONFIG, MEDIA, MOD)

        except Exception as e:
            xlog.log_error(f"An error occurred: {str(e)}")

def handle_host_selection(CONFIG, MEDIA, MOD):
    """
    Host Selection Menu: Allows the user to select the host and potentially the source path.
    """
    path_options = ["Enter own", "Choose interactive from corepath", "Back"]
    default_hostpath = questionary.select("Choose the host you are on:", choices=list(MEDIA["core_paths"].keys())).ask()

    if tools.yesno(MOD, "Do you want to set the path too?"):
        path_options.append("Use corepath")
        path_opt = tools.basic_menu(MOD, path_options, "How do you want to enter the path?")
        if path_opt == "Enter own":
            source_path = questionary.text("Enter the file path:").ask()
        elif path_opt == "Choose interactive from corepath":
            source_path = xpaths.get_filepath(CONFIG, MOD, MEDIA["core_paths"][default_hostpath], "single")
        elif path_opt == "Use corepath":
            source_path = MEDIA["core_paths"][default_hostpath]
        else:
            xlog.log_info("Quitting")
            return
    elif source_path == None:
        source_path = MEDIA["core_paths"][default_hostpath]
