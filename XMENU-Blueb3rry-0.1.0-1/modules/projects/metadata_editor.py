# !/usr/bin/env python3

from PIL import Image


def path_is_valid(file_path, isFolder=False):
    if isFolder:
        return os.path.isdir(file_path)
    return os.path.isfile(file_path)


def read_metadata(file_path):
    subprocess.run(["exiftool", "-a", file_path])
    xlog.log_continue("Operation complete!")

def change_metadata(file_path, metadata):
    subprocess.run(["exiftool", metadata, file_path])


def check_and_convert_to_expected_format(file_path):
    try:
        file_extension = file_path.split(".")[-1].lower()

        if (
            file_extension == "png"
            or file_extension == "jpg"
            or file_extension == "jpeg"
        ):
            with Image.open(file_path) as img:
                xlog.log_info(f"Original-Image format: {img.format}")
                new_file_path = None
                if img.format == "JPEG" and (
                    file_extension != "jpg" and file_extension != "jpeg"
                ):
                    # Convert PNG to JPEG
                    xlog.log_info("Converting to JPEG")
                    new_file_path = file_path[:-3] + "jpg"
                    img.save(new_file_path)
                elif img.format == "PNG" and file_extension != "png":
                    # Convert JPEG to PNG
                    xlog.log_info("Converting to PNG")
                    new_file_path = file_path[:-3] + "png"
                    img.save(new_file_path)

            if new_file_path:
                xlog.log_info(f"-- Replacing {file_path}\n-- with {new_file_path}")
                os.replace(file_path, new_file_path)
                return new_file_path
            else:
                return file_path  # Zurückgeben des ursprünglichen Dateipfads
        elif file_extension == "mp4":
            return file_path
        return False
    except Exception as e:
        xlog.log_error(f"An error occurred during format conversion: {e}")
        return False


def check_leftovers(file_path):
    # check for files including "_temp" or ending with "_original" and remove them
    files_in_directory = os.listdir(os.path.dirname(file_path))
    xlog.log_info(f"Files in directory: {len(files_in_directory)}")
    leftovers = 0
    for file in files_in_directory:
        if "_temp" in file or "_original" in file:
            os.remove(str(file_path + file))
            leftovers += 1
            xlog.log_info(f"Removed leftover file: {file}")
    xlog.log_info("Check for leftovers completed successfully.")
    xlog.log_continue(f"Removed {leftovers} leftover files.")


def remove_metadata(file_path):
    try:
        checked_path = check_and_convert_to_expected_format(file_path)
        if not checked_path:
            xlog.log_error(f"Looks like a Format-Issue - {file_path}")
            return

        else:
            file_path = checked_path

        file_extension = file_path.split(".")[-1].lower()

        if (
            file_extension == "png"
            or file_extension == "jpg"
            or file_extension == "jpeg"
        ):
            subprocess.run(["exiftool", "-all=", file_path], check=True)

        elif file_extension == "mp4":
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    file_path,
                    "-map_metadata",
                    "-1",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "copy",
                    file_path + "_temp.mp4",
                ],
                check=True,
            )
            os.replace(file_path + "_temp.mp4", file_path)
        else:
            xlog.log_info(f"Unsupported file type: {file_extension}")
    except subprocess.CalledProcessError as e:
        xlog.log_info(f"Error occurred while removing metadata from {file_path}: {e}")
    except Exception as e:
        xlog.log_info(f"An error occurred: {e}")


def batch_remove_metadata(directory):
    mediaType = questionary.select(
        "Choose media type:", choices=["Images", "Videos", "Other"]
    ).ask()
    if mediaType == "Other" or mediaType == None:
        xlog.log_info("Unsupported media type.")
        return
    elif mediaType == "Images":
        mediaType = ["png", "jpg", "jpeg"]
    elif mediaType == "Videos":
        mediaType = ["mp4"]
    xlog.log_info("Performing Type-Check ")
    conv_media = 0
    fileCount = len([name for name in os.listdir(directory) if os.path.isfile(name)])
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.split(".")[-1].lower() in mediaType:
                conv_media += 1
                check_and_convert_to_expected_format(os.path.join(root, file))
    choice = questionary.confirm(
        f"Converted {conv_media} of {fileCount} files. Do you want to continue?"
    ).ask()
    if choice:
        subprocess.run(["exiftool", "-all=", directory])
    else:
        xlog.log_info("Operation aborted.")
        return
    


def main_menu(CONFIG, MOD, args):
    
    global xlog, xpaths, os, questionary, subprocess
    
    pymod = MOD["python"]
    psys = MOD["system"]
    utils = MOD["utils"]
    
    os = pymod["os"]
    questionary = pymod["questionary"]
    subprocess = pymod["subprocess"]
    
    xlog = utils["log"]
    xpaths = utils["xpaths"]
    tools = utils["tools"]
    
    MEDIA = CONFIG["paths"]["media"]
    LANG = CONFIG["lang"]
    
    set_host = None
    set_path = None
    
    choices = [
        "Check leftovers",
        "Read metadata from a file",
        "Change metadata of a file",
        "Remove metadata from a file",
        "Batch remove metadata from a directory",
        "Change host",
        "Exit",
    ]
    
    while True:
        path_options = ["Enter own", "Choose interactive from corepath", "Back"]
        tools.cls()
        xlog.log_header(LANG, MOD)
        xlog.log(f"\nWelcome to Metadata Editor.\n!! You need EXIFTOOL installed for this to work !!\n\nSet Host to: {set_host}\nSet Path to: {set_path}\n", LANG, 2, "top")
        
        choice = questionary.select("Choose an option:", choices=choices).ask()

        if choice == choices[0] and (set_host and set_path):  # Check leftovers
            while True:
                path_opt = tools.basic_menu(MOD, path_options, "How to you want to enter the path?")
                if path_opt == "Enter own":
                    directory_path = questionary.text("Enter the file path:").ask()
                elif path_opt == "Choose interactive from corepath":
                    directory_path = xpaths.get_filepath(CONFIG, MOD, set_path, "single")
                else:
                    xlog.log_info("Quitting")
                    continue
                if directory_path[:-1] != "\\":
                    directory_path += "\\"
                if path_is_valid(directory_path, True):
                    xlog.log_info(f"Path is valid: {directory_path}")
                    break
                else:
                    xlog.log_info("Invalid file path. Please try again.")
            check_leftovers(directory_path)
            xlog.log_continue("Operation complete!")

        elif choice == choices[1] and (set_host and set_path):  # Read metadata from a file
            while True:
                path_opt = tools.basic_menu(MOD, path_options, "How to you want to enter the path?")
                if path_opt == "Enter own":
                    file_path = questionary.text("Enter the file path:").ask()
                elif path_opt == "Choose interactive from corepath":
                    file_path = xpaths.get_filepath(CONFIG, MOD, set_path, "single")
                else:
                    xlog.log_info("Quitting")
                    continue
                if path_is_valid(file_path):
                    xlog.log_info(f"Path is valid: {file_path}")
                    break
                else:
                    xlog.log_error("Invalid file path. Please try again.")
            read_metadata(file_path)

        elif choice == choices[2]  and (set_host and set_path):  # Change metadata of a file
            while True:
                path_opt = tools.basic_menu(MOD, path_options, "How to you want to enter the path?")
                if path_opt == "Enter own":
                    file_path = questionary.text("Enter the file path:").ask()
                elif path_opt == "Choose interactive from corepath":
                    file_path = xpaths.get_filepath(CONFIG, MOD, set_path, "single")
                else:
                    xlog.log_info("Quitting")
                    continue
                if path_is_valid(file_path):
                    xlog.log_info(f"Path is valid: {file_path}")
                    break
                else:
                    xlog.log_info("Invalid file path. Please try again.")
            metadata = questionary.text(
                "Enter metadata changes (e.g., '-title=NewTitle -artist=NewArtist'):"
            ).ask()
            change_metadata(file_path, metadata)
            xlog.log_continue("Operation complete!")

        elif choice == choices[3]  and (set_host and set_path):  # Remove metadata from a file
            while True:
                path_opt = tools.basic_menu(MOD, path_options, "How to you want to enter the path?")
                if path_opt == "Enter own":
                    file_path = questionary.text("Enter the file path:").ask()
                elif path_opt == "Choose interactive from corepath":
                    file_path = xpaths.get_filepath(CONFIG, MOD, set_path, "single")
                else:
                    xlog.log_info("Quitting")
                    continue
                if path_is_valid(file_path):
                    xlog.log_info(f"Path is valid: {file_path}")
                    break
                else:
                    xlog.log_error("Invalid file path. Please try again.")
            remove_metadata(file_path)

        elif choice == choices[4]  and (set_host and set_path):  # Batch remove metadata from a directory
            while True:
                path_opt = tools.basic_menu(MOD, path_options, "How to you want to enter the path?")
                if path_opt == "Enter own":
                    directory_path = questionary.text("Enter the file path:").ask()
                elif path_opt == "Choose interactive from corepath":
                    directory_path = xpaths.get_path(CONFIG, MOD, set_path, "single")
                else:
                    xlog.log_info("Quitting")
                    continue
                if path_is_valid(directory_path, True):
                    xlog.log_info(f"Path is valid: {directory_path}")
                    break
                else:
                    xlog.log_error("Invalid directory path. Please try again.")
            batch_remove_metadata(directory_path)

        elif choice == choices[5]: # Change Host
            xlog.log_info("If the host you are on is not listed, run 'conf' and edit the 'core_paths' in the 'lang' config!")
            set_host = questionary.select("Choose the host you are on:", choices=list(MEDIA["core_paths"].keys())).ask()
            
            if tools.yesno(MOD, "Do you want to set the path too?"):
                path_options.append("Use corepath")
                path_opt = tools.basic_menu(MOD, path_options, "How to you want to enter the path?")
                if path_opt == "Enter own":
                    set_path = questionary.text("Enter the file path:").ask()
                elif path_opt == "Choose interactive from corepath":
                    set_path = xpaths.get_filepath(CONFIG, MOD, MEDIA["core_paths"][set_host], "single")
                elif path_opt == "Use corepath":
                    set_path = MEDIA["core_paths"][set_host]
                else:
                    xlog.log_info("Quitting")
                    continue
            elif set_path == None:
                set_path = MEDIA["core_paths"][set_host]

        elif choice == choices[6] or choice == None:  # Exit
            break
        
        elif not set_path or not set_host:
            xlog.log_continue("You have to set the host and path first! Select 'Change host'!")


if __name__ == "__main__":
    main_menu()
