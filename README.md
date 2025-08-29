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

## API-Keys und Fallbacks

Für die Abfragen von Traffic und Backlinks werden nach Möglichkeit
API-Schlüssel verwendet. Setzen Sie vor dem Start folgende
Umgebungsvariablen, falls verfügbar:

* `SIMILARWEB_API_KEY` – Traffic-Abfrage über die SimilarWeb-API
* `OPR_API_KEY` – Backlink-Abfrage über [Open Page Rank](https://www.openpagerank.com/)

Sind keine API-Schlüssel gesetzt oder liefern die APIs keine Daten,
versucht das Programm, alternative öffentliche Quellen zu nutzen
(`data.similarweb.com` für Traffic bzw. `api.openlinkprofiler.org` für
Backlinks). Erst wenn auch diese Abfragen fehlschlagen, wird für die
jeweiligen Felder `N/A` zurückgegeben.

## Logging

Während der Verarbeitung schreibt die Anwendung Status- und Fehlermeldungen
in die Datei `domain_checker.log`. Anhand dieser Logdatei lässt sich
nachvollziehen, welche API-Aufrufe erfolgreich waren und wo eventuell
Probleme auftraten.
