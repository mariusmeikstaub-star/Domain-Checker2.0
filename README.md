# Domain Checker 2.0

Dieses Tool prüft eine Liste von Domains aus einer CSV-Datei darauf,
ob sie registriert sind, wie viel Traffic sie haben und wie viele
Backlinks auf sie verweisen.

## Nutzung

1. Erstellen Sie eine CSV-Datei mit einer Domain pro Zeile. Optional kann die erste Zeile eine Kopfzeile `domain` enthalten.
2. Doppelklicken Sie unter Windows auf `start.bat`. Es wird eine virtuelle Umgebung eingerichtet, die Abhängigkeiten installiert und die Anwendung gestartet.
3. Laden Sie die CSV-Datei über die Benutzeroberfläche hoch.
4. Warten Sie, bis alle Domains geprüft wurden. Der Fortschritt wird angezeigt.
5. Laden Sie das Ergebnis als CSV-Datei herunter.

## CSV-Format

- Eine Domain pro Zeile
- Optionale Kopfzeile `domain`

Beispiel mit Kopfzeile:

```
domain
example.com
example.org
```

Beispiel ohne Kopfzeile:

```
example.com
example.org
```

## Datenquellen

- **Traffic**: Scraping der Seite [StatsCrop](https://www.statscrop.com/) mit Fallback auf [Hypestat](https://hypestat.com/) und Auslesen der dort angegebenen "Daily Visitors" (hochgerechnet auf den Monat).
- **Backlinks**: Abfrage der freien API von [HackerTarget](https://api.hackertarget.com/backlinks/) mit Fallback auf [OpenLinkProfiler](https://www.openlinkprofiler.org/) und Zählen der zurückgegebenen Links.
- **Verfügbarkeit**: Whois-Abfrage über das Python-Paket `python-whois`.

Für alle Anfragen sind keine API-Schlüssel nötig. Kann kein Wert ermittelt werden, wird `0` zurückgegeben.

## Logging

Während der Verarbeitung schreibt die Anwendung Status- und Fehlermeldungen
in die Datei `domain_checker.log`. Anhand dieser Logdatei lässt sich
nachvollziehen, welche API-Aufrufe erfolgreich waren und wo eventuell
Probleme auftraten.
