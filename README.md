# Domain Checker 2.0

Dieses Tool prüft eine Liste von Domains aus einer CSV-Datei darauf,
ob sie registriert sind, wie viel Traffic sie haben und wie viele
Backlinks auf sie verweisen.

## Nutzung

1. Erstellen Sie eine CSV-Datei mit einer Domain pro Zeile.
2. Doppelklicken Sie unter Windows auf `start.bat`.
3. Laden Sie die CSV-Datei über die Benutzeroberfläche hoch.
4. Warten Sie, bis alle Domains geprüft wurden. Der Fortschritt wird angezeigt.
5. Laden Sie das Ergebnis als CSV-Datei herunter.

## API-Keys

Für die Abfragen von Traffic und Backlinks werden API-Schlüssel erwartet.
Setzen Sie vor dem Start folgende Umgebungsvariablen, falls verfügbar:

* `SIMILARWEB_API_KEY` – Traffic-Abfrage
* `OPR_API_KEY` – Backlink-Abfrage über [Open Page Rank](https://www.openpagerank.com/)

Sind keine API-Schlüssel gesetzt, werden für die jeweiligen Felder `None` zurückgegeben.
