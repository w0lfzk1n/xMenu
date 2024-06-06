# !/usr/bin/env python3
import os
import time
import random
import string
import subprocess

def gen_name(CONFIG, MOD, mode="full", amount=1):
    """
    Generates a random name from the wordlist.
    :param config: Config from core_conf.json.
    :param MOD: Object of imported modules from project.
    :param mode: Mode to generate the name. ["full" <Default>, "nature", "tec", "myth", "space"]
    :param amount: Amount of names to generate. [Default=1]
    returns: array: [] array of random words with given amount
    """
    random = MOD["python"]["random"]
    xjson = MOD["utils"]["xjson"]
    xpaths = MOD["utils"]["xpaths"]
    xlog = MOD["utils"]["log"]
    if CONFIG:
        SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
        wordlist = CONFIG["wordlist"]
        (
            wl_nom,
            wl_adj,
            wl_nature_nom,
            wl_nature_adj,
            wl_tec_nom,
            wl_tec_adj,
            wl_myth_nom,
            wl_myth_adj,
            wl_space_nom,
            wl_space_adj,
        ) = (
            wordlist["nom"],
            wordlist["adj"],
            wordlist["nature_nom"],
            wordlist["nature_adj"],
            wordlist["tec_nom"],
            wordlist["tec_adj"],
            wordlist["myth_nom"],
            wordlist["myth_adj"],
            wordlist["space_nom"],
            wordlist["space_adj"],
        )
    else:
        xlog.log_error("No config found")
        exit(1)

    random_words = []

    if mode == "full":
        random_word1 = wl_adj
        random_word2 = wl_nom

    elif mode == "nature":
        random_word1 = wl_nature_adj
        random_word2 = wl_nature_nom

    elif mode == "tec":
        random_word1 = wl_tec_adj
        random_word2 = wl_tec_nom

    elif mode == "myth":
        random_word1 = wl_myth_adj
        random_word2 = wl_myth_nom

    elif mode == "space":
        random_word1 = wl_space_adj
        random_word2 = wl_space_nom
    else:
        random_word1 = wl_adj
        random_word2 = wl_nom

    for i in range(amount):
        random_words.append(
            random.choice(random_word1) + "-" + random.choice(random_word2)
        )

    return random_words

def gen_ascii(CONFIG, MOD, text):
    """
    Opens a headless browser and generates ascii art from text.
    URL used: https://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20
    :param CONFIG: Config dict.
    :param MOD: Module dict.
    :param text: Text to generate ascii art from.
    """
    pymod = MOD["python"]
    utils = MOD["utils"]
    time = pymod["time"]
    Select = pymod["selenium"].webdriver.support.ui.Select
    browser_module = utils["browser"]
    xlog = utils["log"]
    
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
    browser_utils = browser_module.open_browser(SCRIPT_PATH, True)
    try:
        browser = browser_utils["browser"]
        By = browser_utils["By"]
        Select = browser_utils["Select"]

        patj_xpaths = CONFIG["xpaths"]["patorjik"]
        time.sleep(5)
        browser_module.load_site(
            browser,
            "https://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20",
        )

        dropdown = Select(browser.find_element(By.XPATH, patj_xpaths["fonts"]))
        options = dropdown.options
        dropdown.select_by_visible_text("Alpha")
        browser.find_element(By.XPATH, patj_xpaths["input_box"]).send_keys(text)
        output = browser.find_element(By.XPATH, patj_xpaths["output_box"]).text
        browser_module.close_browser(browser)
        return output
    except KeyError as e:
        xlog.log_error(f"[gen-ascii] KeyError: {e}")
    except ValueError as e:
        xlog.log_error(f"[gen-ascii] ValueError: {e}")
    except Exception as e:
        xlog.log_error(f"[gen-ascii] Unknown Error: {e}")

def cls():
    """
    Clears the console.
    """
    if os.name == "posix":
        command = "clear"
    else:
        command = "cls"
    os.system(command)

def clear_console(CONFIG, MOD, clear=True):
    cls()
    MOD['utils']['log'].log_header(CONFIG['lang'], MOD)

def xdatenow():
    """
    Returns current date as string.
    :param: None
    :return: Formatted date string. %H:%M:%S
    """
    return time.strftime("%H:%M:%S", time.localtime())

def open_txtfile(MOD, args=[]):
    """
    Opens a textfile.
    :param MOD: Module dict.
    :param args: array: Object for path to textfile.
    """
    xlog = MOD["utils"]["log"]
    xpaths = MOD["utils"]["xpaths"]

    try:
        if not args:
            raise ValueError("No arguments provided. Please specify a path to the text file.")

        file_path = xpaths.format_path(args[0])

        if os.name == "posix":
            os.system(f"nano '{file_path}'")
        else:
            os.system(f"notepad '{file_path}'")
        return True

    except ValueError as ve:
        xlog.log_fail(f"ValueError: {ve}")
        return False
    except FileNotFoundError as fnf:
        xlog.log_fail(f"FileNotFoundError: {fnf}")
        return False
    except Exception as e:
        xlog.log_fail(f"An unexpected error occurred: {e}")
        return False

def create_folder(CONFIG, MOD, args=[]):
    """
    Creates a new folder.
    :param CONFIG: Object for Config.
    :param MOD: Object for Modules.
    :param args=[]: arguments.
    :return: None.
    """
    xlog = MOD["utils"]["log"]
    questionary = MOD["python"]["questionary"]
    xpaths = MOD["utils"]["xpaths"]
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
    HOSTS = CONFIG["hosts"]

    try:
        if not args:
            host = questionary.select("Choose host for saved paths:", choices=list(HOSTS.keys())).ask()
            path = questionary.select("Choose saved path:", choices=list(HOSTS[host]["paths"]["as_runtime"])).ask()
            full_path = xpaths.get_path(CONFIG, MOD, path, "single")
            new_folder_name = xlog.log_input(f"Enter a name for the new folder in [{full_path}]")
            full_path = xpaths.format_path(new_folder_name, full_path)
        else:
            full_path = args[0]
            new_folder_name = xlog.log_input(f"Enter a name for the new folder in [{full_path}]")
            full_path = xpaths.format_path(new_folder_name, full_path)

        if not os.path.exists(full_path):
            os.makedirs(full_path)
            xlog.log_continue(f"Created folder: {full_path}")
            return full_path
        else:
            raise FileExistsError(f"Folder already exists: {full_path}")

    except FileExistsError as fee:
        xlog.log_continue(f"{fee}")
    except OSError as e:
        xlog.log_continue(f"Creation of the directory {full_path} failed.\n{e}")
    except Exception as e:
        xlog.log_continue(f"An unexpected error occurred while creating the folder: {e}")

def pad(s):
    """
    Encryption.
    Pad the string to encrypt.
    :param s: String to pad.
    :return: Padded string.
    """
    return s + (AES.block_size - len(s) % AES.block_size) * chr(
        AES.block_size - len(s) % AES.block_size
    )

def unpad(s):
    """
    Encryption.
    Unpad the encrypted string.
    :param s: Encrypted string.
    :return: Decrypted string.
    """
    return s[: -ord(s[len(s) - 1 :])]

def encrypt_string(CONFIG, MOD, string):
    global AES
    """
    Encrypts a string.
    :param SCRIPT_PATH: Rootpath to project.
    :param CONFIG: Config dict.
    :param MOD: Module dict.
    :param link: Something to encrypt.
    :return: Encrypted string.
    """
    ENC_TAG = CONFIG["core"]["coredata"]["enc_tag"]
    SECRET_KEY = CONFIG["core"]["coredata"]["secret_phrase"]
    base64 = MOD["python"]["base64"]
    AES = MOD["python"]["Crypto.Cipher.AES"]
    xlog = MOD["utils"]["log"]

    try:
        cipher = AES.new(SECRET_KEY.encode(), AES.MODE_ECB)
        padded_link = pad(string)
        encrypted = cipher.encrypt(padded_link.encode())
        return ENC_TAG + base64.b64encode(encrypted).decode()
    except Exception as e:
        xlog.log_fail(f"[encrypt] ERROR: {e}")
        return None

def decrypt_string(CONFIG, MOD, encrypted_string):
    """
    Decrypts a string.
    :param SCRIPT_PATH: Rootpath to project.
    :param CONFIG: Config dict.
    :param MOD: Module dict.
    :param encrypted_link: Something to decrypt.
    :return: Decrypted string.
    """
    ENC_TAG = CONFIG["core"]["coredata"]["enc_tag"]
    SECRET_KEY = CONFIG["core"]["coredata"]["secret_phrase"]
    base64 = MOD["python"]["base64"]
    AES = MOD["python"]["Crypto.Cipher.AES"]
    xlog = MOD["utils"]["log"]
    
    try:
        cipher = AES.new(SECRET_KEY.encode(), AES.MODE_ECB)
        encrypted_string = encrypted_string[len(ENC_TAG) :]
        decoded_encrypted_string = base64.b64decode(encrypted_string)
        decrypted = cipher.decrypt(decoded_encrypted_string)
        return unpad(decrypted.decode())
    except Exception as e:
        xlog.log_fail(f"[decrypt] ERROR: {e}")
        return None

def generate_random_key(length=32):
    """
    Generates a random key.
    :param length: Length of the key. [Default=32]
    :return: Random key as string.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_ssh_key(key_path, passphrase):
    """
    Generate SSH key pair.
    :param key_path: Path to save the key.
    :param passphrase: Passphrase for the key.
    """
    if not key_path or not passphrase:
        return False
    try:
        subprocess.run(
            ["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", key_path, "-N", passphrase],
            check=True
        )
        subprocess.run(
            ["sudo", "chmod", "600", key_path],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        return False

def update_secret_phrase(CONFIG, MOD):
    """
    Updates the secret phrase in the core_conf.json.
    :param None:
    :return None:
    """
    tools = MOD["utils"]["tools"]
    xjson = MOD["utils"]["xjson"]
    xlog = MOD["utils"]["log"]
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]

    CONFIG["core"]["coredata"]["secret_phrase"] = tools.generate_random_key()
    xjson.save_config_json(SCRIPT_PATH, CONFIG)
    xlog.log_success("Updated secret phrase.")
    
def yesno(MOD, text):
    questionary = MOD["python"]["questionary"]
    if questionary.confirm(f"{text}").ask():
        return True
    else:
        return False

def basic_menu(MOD, options=[], title="Options"):
    questionary = MOD["python"]["questionary"]
    menu_option = questionary.select(title, options).ask()
    if menu_option in [None, "", " "]:
        return None
    else:
        return menu_option
    
def is_valid_url(link):
    return link.startswith("http://") or link.startswith("https://")


def create_object(MOD, CONFIG, opt="menu"):
    """
    Allows the user to interactively create an array or a dictionary.
    :param MOD: Module dictionary for project modules.
    :param CONFIG: Configuration dictionary.
    :param opt: Specifies which type of collection to create directly ("arr" for array, "dict" for dictionary) or "menu" for choice.
    :return: The created array or dictionary, or None if the user exits.
    """
    questionary = MOD["python"]["questionary"]
    xlog = MOD["utils"]["log"]

    def create_array():
        """
        Allows the user to create and populate an array with strings.
        """
        array = []
        xlog.log_info("Creating a new array. Enter items and select 'Finish' when done.")
        while True:
            item = questionary.text("Enter a string item for the array or leave empty to complete:").ask()
            if item == '':
                break
            array.append(item)
        return array

    def create_dictionary():
        """
        Allows the user to create and populate a dictionary with keys and values.
        """
        dictionary = {}
        xlog.log_info("Creating a new dictionary. Enter items and select 'Finish' when done.")
        while True:
            key = questionary.text("Enter a key for the dictionary or leave empty to complete:").ask()
            if key == '':
                break
            value_type = questionary.select("Select the type of value:", choices=['String', 'Array', 'Dictionary', '>> Confirm']).ask()
            if value_type == ">> Confirm" or not value_type:
                break
            elif value_type == 'Array':
                value = create_array()
            elif value_type == 'Dictionary':
                value = create_dictionary()
            else:
                value = questionary.text("Enter a string value:").ask()
            dictionary[key] = value
        return dictionary

    if opt == "arr":
        return create_array()
    elif opt == "dict":
        return create_dictionary()
    else:
        action = questionary.select("Select the type of object to create:", choices=["Create Array", "Create List", "Back"]).ask()
        if action == "Create Array":
            return create_array()
        elif action == "Create List":
            return create_dictionary()
        else:
            xlog.log_info("Operation cancelled.")
            return None
