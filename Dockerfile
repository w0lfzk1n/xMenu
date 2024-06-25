# Basis-Image
FROM python:3.12-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die requirements-Datei in den Container
COPY ./configs/requirements/requirements.txt ./configs/requirements/

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r ./configs/requirements/requirements.txt

# Kopiere den Rest des Anwendungs-Codes in den Container
COPY . .

# Definiere den Befehl zum Starten der Anwendung
CMD ["python3", "run.py"]
