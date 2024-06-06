# !/usr/bin/env python3

def admin_command(CONFIG, MOD, args=[]):
    global xlog, questionary
    """
    Admin command module to execute predefined commands from a list.
    """

    # Module imports
    os = MOD["python"]["os"]
    subprocess = MOD["python"]["subprocess"]
    questionary = MOD["python"]["questionary"]
    xlog = MOD["utils"]["log"]
    tools = MOD["utils"]["tools"]
    config = MOD["system"]["config"]
    
    LANG = CONFIG["lang"]

    current_host = None

    while True:
        tools.cls()
        xlog.log_header(LANG, MOD)
        xlog.log(f"\nWelcome to Admin Commands.\nRun saved commands outside of the project.\n\n>> Current Host: {current_host}\n", LANG, 2, "top")
        options = ["Change Host", "Select Command", "Add Command", "Exit"]
        selection = questionary.select("Choose an option:", choices=options).ask()

        if selection == "Exit" or not selection or selection == "":
            xlog.log_info("Exiting admin command module.")
            break
        elif selection == "Change Host":
            current_host = change_host(CONFIG)
        elif selection == "Add Command":
            if not current_host:
                xlog.log_error("No host selected. Please select a host first.")
            else:
                config.runconfig(CONFIG, MOD, [["hosts", current_host, "commands"]])
        elif selection == "Select Command":
            if not current_host:
                xlog.log_error("No host selected. Please select a host first.")
            else:
                execute_command(CONFIG, MOD, current_host, questionary, tools, subprocess)

def change_host(CONFIG):
    """
    Allows the user to select a host from the configuration.
    """
    hosts = list(CONFIG["hosts"].keys())
    host = questionary.select("Select a host:", choices=hosts).ask()
    return host

def execute_command(CONFIG, MOD, host, questionary, tools, subprocess):
    """
    Displays available commands for the selected host and allows the user to execute them.
    """
    commands = CONFIG["hosts"][host]["commands"]
    if not commands:
        xlog.log_continue("No commands available for this host. Please run 'config' and edit the 'commands' for this host!")
        return

    command = questionary.select("Select a command to execute:", choices=commands).ask()
    xlog.log_info(f"Command to execute: [ {command} ]")
    if tools.yesno(MOD, "Do you want to execute this command?"):
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            xlog.log_continue(f"Command executed successfully:\n{result.stdout.decode()}\n")
        except subprocess.CalledProcessError as e:
            xlog.log_error(f"Error executing command: {e.stderr.decode()}")
