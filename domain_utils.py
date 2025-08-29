import whois
import requests
import os
import logging

# Configure a basic logger that writes to ``domain_checker.log``.
logger = logging.getLogger("domain_checker")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("domain_checker.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def check_availability(domain):
    try:
        w = whois.whois(domain)
        available = w.domain_name is None
        logger.info("Checked availability for %s: %s", domain, available)
        return available
    except Exception as e:
        logger.exception("Error checking availability for %s: %s", domain, e)
        return True

def get_traffic(domain):
    """Return estimated visits for *domain*.

    Versucht zunächst, die SimilarWeb-API mit einem API-Key zu nutzen. Sollte kein
    Schlüssel vorhanden sein oder die Abfrage fehlschlagen, wird als Fallback
    die öffentliche SimilarWeb-Datenquelle verwendet. Führen beide Versuche zu
    keinem Ergebnis, wird ``"N/A"`` zurückgegeben.
    """

    api_key = os.getenv("SIMILARWEB_API_KEY")
    if api_key:
        url = (
            f"https://api.similarweb.com/v1/website/{domain}/traffic-and-engagement/visits"
            f"?api_key={api_key}&country=world"
        )
        try:
            r = requests.get(url, timeout=10)
            logger.info("SimilarWeb API response for %s: %s", domain, r.status_code)
            r.raise_for_status()
            data = r.json()
            visits = data.get("visits")
            if isinstance(visits, dict):
                total = sum(visits.values())
                logger.info("Fetched traffic for %s: %s", domain, total)
                return total
        except Exception as e:
            logger.exception(
                "Error fetching traffic for %s via SimilarWeb API: %s", domain, e
            )

    fallback_url = f"https://data.similarweb.com/api/v1/data?domain={domain}"
    try:
        r = requests.get(fallback_url, timeout=10)
        logger.info(
            "SimilarWeb public API response for %s: %s", domain, r.status_code
        )
        r.raise_for_status()
        data = r.json()
        visits = data.get("EstimatedMonthlyVisits")
        if isinstance(visits, dict):
            total = sum(visits.values())
            logger.info("Fetched traffic for %s via fallback: %s", domain, total)
            return total
    except Exception as e:
        logger.exception(
            "Error fetching traffic for %s via public SimilarWeb API: %s", domain, e
        )
    logger.info("Returning 'N/A' for traffic of %s", domain)
    return "N/A"

def get_backlinks(domain):
    """Return number of referring domains for *domain*.

    Primär wird die Open-Page-Rank-API verwendet. Fehlt der API-Key oder ist
    keine Antwort verfügbar, greift die Funktion auf die offene
    OpenLinkProfiler-API zurück.
    """

    api_key = os.getenv("OPR_API_KEY")
    if api_key:
        url = (
            f"https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D={domain}"
        )
        headers = {"API-OPR": api_key}
        try:
            r = requests.get(url, headers=headers, timeout=10)
            logger.info("Open Page Rank response for %s: %s", domain, r.status_code)
            r.raise_for_status()
            data = r.json()
            response = data.get("response", [])
            if response:
                referring = response[0].get("referring_domains")
                if referring is not None:
                    logger.info("Fetched backlinks for %s: %s", domain, referring)
                    return referring
        except Exception as e:
            logger.exception(
                "Error fetching backlinks for %s via Open Page Rank: %s", domain, e
            )

    fallback_url = (
        f"https://api.openlinkprofiler.org/summary?domain={domain}&format=json"
    )
    try:
        r = requests.get(fallback_url, timeout=10)
        logger.info(
            "OpenLinkProfiler response for %s: %s", domain, r.status_code
        )
        r.raise_for_status()
        data = r.json()
        backlinks = (
            data.get("summary", {}).get("backlinks")
            or data.get("response", {}).get("summary", {}).get("backlinks")
            or data.get("backlinks")
        )
        if backlinks is not None:
            logger.info(
                "Fetched backlinks for %s via fallback: %s", domain, backlinks
            )
            return backlinks
    except Exception as e:
        logger.exception(
            "Error fetching backlinks for %s via OpenLinkProfiler: %s", domain, e
        )
    logger.info("Returning 'N/A' for backlinks of %s", domain)
    return "N/A"
