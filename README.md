
### Anforderungen 

1. **Dokumentation:**
    - Erstellt ein detailliertes `DevContainer_README.md`, das das Projekt erklärt und beschreibt, wie das Repository in einem Dev-Container geöffnet und die Anwendung gestartet wird (idealerweise mit F5).
    - Die Anleitung sollte so verfasst sein, dass ein neues Teammitglied schnell und effizient in das Projekt einsteigen kann.
2. **Automatisierte Installation:**
    - Stellt sicher, dass alle notwendigen externen Abhängigkeiten beim Erstellen des Containers automatisch installiert werden.
3. **Nützliche Extensions:**
    - Wählt Extensions aus, die den Entwicklungsprozess unterstützen und vereinfachen. Dokumentiert euren Entscheidungsprozess für die von euch ausgewählten Extensions.
4. **Debugging-Unterstützung:**
    - Euer Container sollte die Möglichkeit bieten, das Debugging effizient zu nutzen.
5. **Datenbankintegration:**
    - Euer Demo-Projekt sollte eine Datenbankanbindung haben.
    - Integriert ein Tool zur Überprüfung des Datenbankinhalts.
6. **Produktionsbereite Container:**
    - Erstellt Dockerfiles/Docker-Compose Files für den Einsatz in der Produktion.
7. **Sicheres Handling sensibler Daten:**
    - Verwendet eine `.env`Datei für Passwörter und sensible Daten (diese Datei darf nicht ins Repository eingecheckt werden). Dokumentiere die notwendige Struktur der  `.env`Datei in einer Datei mit dem Namen `env-schema.txt`. Diese Datei soll ins Repository eingecheckt werden.
8. **Demodaten:**
    - Implementiert einen Mechanismus zum Initialisieren der Applikation/Datenbank mit Testdaten.
9. **Effiziente Alternativlösung:**
    - Erstellt in einem separaten Branch eine Version eures Projekts, die einen bereits konfigurierten Dev-Container aus eurem Docker-Hub bezieht. Dies ist ideal für Projekte mit vielen Abhängigkeiten. Der Befehl `docker commit` könnte hierbei nützlich sein.
10. **One-Click Setup:**
    - Fügt im `README.md` einen Button hinzu, der es ermöglicht, das Repository in einem Dev-Container mit einem Klick zu öffnen.
        
        ![2024-03-17 15_35_36-vscode-remote-try-java_README.md at main · seeli-teaching_vscode-remote-try-java.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/fc447b71-8dd4-4788-82ff-d33d9e7142f5/f88152d1-a15c-4901-a383-46b3ff277f8b/2024-03-17_15_35_36-vscode-remote-try-java_README.md_at_main__seeli-teaching_vscode-remote-try-java.png)
        
11. **Pull Request:**
    - Reicht eure Dev-Container Erweiterung als Pull Request beim Originalprojekt ein. Versucht, den Pull Request so zu gestalten, dass er akzeptiert wird.
    - Dokumentiert die einzelnen Schritte und die dabei entstandene Kommunikation mit dem Owner des Originalprojektes.


[![Open in Codespares](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?skip_quickstart=true&machine=basicLinux32gb&repo=816813863&ref=main&devcontainer_path=.devcontainer%2Fdevcontainer.json&geo=EuropeWest)

### Vorkonfigurationen für das Projekt

Um xMenu in deinem Terminal starten zu können, nachdem du das Alias eingerichtet hast, folge diesen Schritten:

1. **Stelle sicher, dass du das Alias hinzugefügt hast**:
   - Du hast die Zeile `alias xmenu="cd /path/to/your/xMenu && bash start.sh start"` am Ende der Datei `/etc/bash.bashrc` hinzugefügt und die Datei gespeichert.

2. **Lade die Bash-Konfiguration neu**:
   - Stelle sicher, dass die neue Konfiguration geladen ist, indem du den folgenden Befehl im Terminal ausführst:
     ```bash
     source /etc/bash.bashrc
     ```

3. **Starte xMenu**:
   - Nun solltest du xMenu einfach starten können, indem du im Terminal den Befehl `xmenu` eingibst:
     ```bash
     xmenu
     ```

Hier ist eine detaillierte Anleitung zu den Schritten:

### Alias hinzufügen

1. Öffne ein Terminal und bearbeite die Bash-Konfigurationsdatei:
   ```bash
   sudo nano /etc/bash.bashrc
   ```

2. Scrolle zum Ende der Datei und füge das Alias hinzu:
   ```bash
   alias xmenu="cd /path/to/your/xMenu && bash start.sh start"
   ```
   Ersetze `/path/to/your/xMenu` mit dem tatsächlichen Pfad zu deinem xMenu-Verzeichnis.

3. Speichere die Datei und schließe den Editor:
   - Drücke `CTRL + O`, dann `Enter`, um zu speichern.
   - Drücke `CTRL + X`, um den Editor zu schließen.

### Bash-Konfiguration neu laden

1. Lade die neue Bash-Konfiguration:
   ```bash
   source /etc/bash.bashrc
   ```

### xMenu starten

1. Starte xMenu mit dem neuen Alias:
   ```bash
   xmenu
   ```

Wenn alles korrekt eingerichtet ist, sollte der Befehl `xmenu` das Skript `start.sh` im xMenu-Verzeichnis starten und das Projekt ausführen. Wenn du auf Probleme stößt oder Fehlermeldungen erhältst, lass es mich wissen, damit ich dir weiterhelfen kann.

### Tastenkombinationen-Einstellungen festlegen

### Schritt 1: Öffne die Tastenkombinationen-Einstellungen

1. **Visual Studio Code öffnen**:
   - Öffne Visual Studio Code.

2. **Tastenkombinationen-Einstellungen öffnen**:
   - Gehe zu `File > Preferences > Keyboard Shortcuts` oder drücke `Ctrl + K, Ctrl + S`.


### Schritt 2: `keybindings.json`-Datei öffnen

1. **`keybindings.json`-Datei öffnen**:
   - Klicke auf das Symbol `Open Keyboard Shortcuts (JSON)` oben rechts, um die `keybindings.json`-Datei zu öffnen.


### Schritt 3: Tastenkombination hinzufügen

1. **Tastenkombination hinzufügen**:
   - Füge den folgenden JSON-Code in die `keybindings.json`-Datei ein:

     ```json
     [
         {
             "key": "f5 + f6",
             "command": "workbench.action.tasks.runTask",
             "args": "Start xMenu"
         }
     ]
     ```

     - Falls die Datei bereits andere Einträge enthält, stelle sicher, dass du diese neue Konfiguration zu den bestehenden Einträgen hinzufügst und nicht den gesamten Inhalt ersetzt. Hier ist ein Beispiel, wie es aussehen könnte, wenn bereits andere Tastenkombinationen existieren:

     ```json
     [
         {
             "key": "f5 + f6",
             "command": "workbench.action.tasks.runTask",
             "args": "Start xMenu"
         },
         {
             "key": "ctrl+shift+p",
             "command": "workbench.action.showCommands"
         }
     ]
     ```

   

2. **Datei speichern**:
   - Speichere die Datei mit `Ctrl + S`.

### Schritt 4: Task mit Tastenkombination testen

1. **Visual Studio Code neu starten**:
   - Starte Visual Studio Code neu, damit alle Änderungen wirksam werden.

2. **Task mit Tastenkombination ausführen**:
   - Drücke die zugewiesene Taste (z.B. `F12`), um den Task zu starten und zu prüfen, ob das Skript `start.sh` ausgeführt wird.

Durch diese Schritte kannst du sicherstellen, dass die Tastenkombination korrekt eingerichtet ist, um den `xMenu`-Task in Visual Studio Code zu starten.


### Wie kann man den starten?

Man muss das Terminal öffnen und dort `F5` + `F6` drücken. Dann öffnet sich das Projekt und startet direkt. Sobald der Startvorgang abgeschlossen ist, muss man einmal die `Enter`-Taste drücken. Danach kann man das Terminal bedienen.