# Domain Checker 2.0

Dieses Tool prüft eine Liste von Domains aus einer CSV-Datei darauf,
ob sie registriert sind, wie viel Traffic sie haben und wie viele
Backlinks auf sie verweisen.

## Nutzung

1. Erstellen Sie eine CSV-Datei mit einer Domain pro Zeile. Optional kann die erste Zeile eine Kopfzeile `domain` enthalten.
2. Doppelklicken Sie unter Windows auf `start.bat`. Beim ersten Start lädt
   Playwright einen Browser herunter.
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

- **Traffic**: Scraping der öffentlichen SimilarWeb-Seite mit einem Headless-
  Browser (Playwright).
- **Backlinks**: Scraping der öffentlichen Daten auf OpenLinkProfiler mit
  Playwright.
- **Verfügbarkeit**: Whois-Abfrage über das Python-Paket `python-whois`.

Für alle Anfragen sind keine API-Schlüssel nötig. Da die Seiten JavaScript
verwenden, wird beim ersten Start automatisch der Playwright-Browser
installiert. Kann ein Wert nicht ermittelt werden, erscheint `N/A`.

## Logging

Während der Verarbeitung schreibt die Anwendung Status- und Fehlermeldungen
in die Datei `domain_checker.log`. Anhand dieser Logdatei lässt sich
nachvollziehen, welche API-Aufrufe erfolgreich waren und wo eventuell
Probleme auftraten.
