#!/bin/bash

VENV_DIR="UNIX_venv"
VENV_REQUIREMENTS="configs/requirements/venv_requirements.txt"
PROJECT_REQUIREMENTS="configs/requirements/requirements.txt"

activate_venv() {
    echo -e ">> Activating venv now...\n"
  if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
  else
    echo -e "Error: 'venv' not present. Please run 'start.sh install'."
    exit 1
  fi
}

deactivate_venv() {
  echo -e ">> Dectivating venv now...\n"
  deactivate
}

install_venv() {
  echo -e "\n\n>> Installing requirements for virtual enviroment...\n"
  pip install -r "$VENV_REQUIREMENTS"
  echo -e "'\n+++++++++++++++++++++++++++++++++++++++++++++\n"
  if [ ! -d "$VENV_DIR" ]; then
    echo -e ">> Creating virtual enviroment...\n"
    python3 -m venv "$VENV_DIR"
  fi
  activate_venv
  echo -e "\n\n>> Installing requirements for project enviroment...\n"
  pip install -r "$PROJECT_REQUIREMENTS"
  deactivate_venv
  echo -e "\n>> Installation complete."
  echo -e "'\n+++++++++++++++++++++++++++++++++++++++++++++\n\nEnter to continue..."
}

# Funktion zum Starten des Projekts
start_project() {
echo -e "\n+++++++++++++++++++++++++++++++++++++++++++++\n>> Activating ENV"
  activate_venv
  echo -e "\n>> Starting the Project..."
  python run.py
  if [ $? -ne 0 ]; then
    echo -e "\n>> ERROR: Could not start script 'run.py'..."
  fi
  deactivate_venv
  echo -e "\n>> Deactivating ENV\n\n+++++++++++++++++++++++++++++++++++++++++++++"
}

# Menü anzeigen
display_menu() {
  echo -e "Please choose an option:\n1) Start\n2) First Install\n3) Exit"
  read -p "Option: " option
  case $option in
    1)
      start_project
      ;;
    2)
      install_venv
      start_project
      ;;
    3)
      echo -e "\n+++++++++++++++++++++++++++++++++++++++++++++\nWe are going to be shut down guys!\nSay ya'll prayers! Your wifes miss ya!"
      exit 0
      ;;
    *)
      echo -e "\n+++++++++++++++++++++++++++++++++++++++++++++\nWe are going to be shut down guys!\nSay ya'll prayers! Your wifes miss ya!"
      exit 1
      ;;
  esac
}

if [ $# -eq 0 ]; then
  display_menu
else
  case $1 in
    start)
      start_project
      ;;
    install)
      install_venv
      start_project
      ;;
    *)
      echo -e "\n+++++++++++++++++++++++++++++++++++++++++++++\nNah man, this is XMENU, not some bullshit { $1 }!\n\n It's 'start' 'install' or nothing! Got id?!"
      exit 1
      ;;
  esac
fi