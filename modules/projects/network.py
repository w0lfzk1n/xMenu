#!/usr/bin/env python3

import subprocess

def config(CONFIG, MOD):
    config_tool.runconfig(CONFIG, MOD, [["hosts"]])
    
def ping_server(MOD):
    host = questionary.select("Choose host to ping:", choices=list(HOSTS.keys())).ask()
    if host:
        host_ip = tools.basic_menu(MOD, HOSTS[host]["ipadr"], "Choose a IP of this host:")
        xlog.log_info(f"Pinging {host} ({host_ip})...")
        response = subprocess.run(["ping", "-c", "4", host_ip], capture_output=True, text=True)
        xlog.log_input(response.stdout + "\n\nPress ENTER to continue...")

def ssh_into_server(CONFIG, MOD):
    try:
        host = questionary.select("Choose host to SSH into:", choices=list(HOSTS.keys())).ask()
        if host:
            host_ip = tools.basic_menu(MOD, HOSTS[host]["ipadr"], "Choose a IP of this host:")
            
            username = questionary.select("Choose username:", choices=list(HOSTS[host]["users"].keys())).ask()
            if username:
                password = HOSTS[host]["users"][username]["p"]
                user = HOSTS[host]["users"][username]["u"]
                xlog.log_info(f"SSH into {host} ({host_ip}) with username {username}. Pass: {password}")
                subprocess.run(["sshpass", "-p", tools.decrypt_string(CONFIG, MOD, password) , "ssh", "-o StrictHostKeyChecking=no", f"{user}@{host_ip}"])
                xlog.log_input("Press ENTER to continue. . .")
    except Exception as e:
        xlog.log_error(f"[netw-ssh] ERROR: {e}")

def sftp_to_server(CONFIG, MOD):
    try:
        host = questionary.select("Choose host to SFTP into:", choices=list(HOSTS.keys())).ask()
        if host:
            host_ip = tools.basic_menu(MOD, HOSTS[host]["ipadr"], "Choose a IP of this host:")
            
            use_host_path = questionary.select("Do you want to use the saved SFTP paths or RAW connect:", choices=["Use saved Paths", "Continue RAW"]).ask()
            
            if use_host_path == "Use saved Paths":
                chosen_path = questionary.select("Choose the path for SFTP:", choices=list(HOSTS[host]["paths"]["as_ext_host"])).ask()
            else:
                chosen_path = None
            
            username = questionary.select("Choose saved User:", choices=list(HOSTS[host]["users"].keys())).ask()
            if username:
                password = HOSTS[host]["users"][username]["p"]
                user = HOSTS[host]["users"][username]["u"]
                decrypted_password = tools.decrypt_string(CONFIG, MOD, password)
                xlog.log_info(f"SFTP into {host} ({host_ip}) with username {user}. Pass: {password}")
                if chosen_path:
                    sftp_command = f"sshpass -p '{decrypted_password}' sftp -o StrictHostKeyChecking=no {user}@{host_ip}:{chosen_path}"
                    subprocess.run(sftp_command, shell=True)
                else:
                    subprocess.run(f"sshpass -p {decrypted_password} sftp -o StrictHostKeyChecking=no {user}@{host_ip}", shell=True)
                xlog.log_input("Press ENTER to continue. . .")
    except Exception as e:
        xlog.log_error(f"[netw-sftp] ERROR: {e}")

def idrac():
    script = xpaths.format_path(os.path.join(SCRIPT_PATH, "modules/projects/power_idrac.sh"))
    
    main_action = questionary.select(
        "Choose an action:",
        choices=[
            "on",
            "off",
            "fan",
            "cycle",
            "status"
        ]
    ).ask()

    if main_action == "fan":
        fan_speed = questionary.select(
            "Choose a fan speed:",
            choices=[
                "10",
                "15",
                "20",
                "25",
                "30",
                "35",
                "40",
                "45",
                "50",
                "55",
                "60"
            ]
        ).ask()
        command = f"bash {script} fan {fan_speed}"
    else:
        command = f"bash {script} {main_action}"

    xlog.log_info(f"Executing: {command}")
    subprocess.run(command, shell=True)
    xlog.log_input("Press ENTER to continue...") 

def network(CONFIG, MOD, args):
    global os, glob, questionary, subprocesss, tools, xlog, xpaths, xjson, config_tool, LANG, HOSTS, SCRIPT_PATH
    pymod = MOD["python"]
    psys = MOD["system"]
    utils = MOD["utils"]

    os = pymod["os"]
    subprocesss = pymod["subprocess"]
    glob = pymod["glob"]
    questionary = pymod["questionary"]
    xlog = utils["log"]
    xjson = utils["xjson"]
    xpaths = utils["xpaths"]
    tools = utils["tools"]
    config_tool = psys["config"]

    LANG = CONFIG["lang"]
    HOSTS = CONFIG["hosts"]
    SCRIPT_PATH = CONFIG["core"]["cpaths"]["project_path"]
    
    main_menu_options = ["Edit Config", "Ping Server", "iDRAC", "SSH into Server", "SFTP to Server", "Exit"]
    
    while True:
        tools.cls()
        xlog.log_header(LANG, MOD)
        xlog.log(f"== Starting NETWORK Menu ==", LANG, 2)
        if not HOSTS:
            xlog.log_error(f"You have not configured a host yet! Go back to the terminal and run 'config'")
            xlog.log_input("Press ENTER to continue. . .")
            return
        selection = questionary.select("MainMenu:", choices=main_menu_options).ask()
        
        if selection == "Exit" or not selection:
            xlog.log_info("Exiting NETW Programm!")
            return
        
        elif selection == "Edit Config":
            config(CONFIG, MOD)
        
        elif selection == "Ping Server":
            ping_server(MOD)
            
        elif selection == "SSH into Server":
            ssh_into_server(CONFIG, MOD)
            
        elif selection == "SFTP to Server":
            sftp_to_server(CONFIG, MOD)
            
        elif selection == "iDRAC":
            idrac()