import logging
import re

import whois
import requests
from bs4 import BeautifulSoup
from whois.parser import PywhoisError

# Configure a basic logger that writes to ``domain_checker.log``.
logger = logging.getLogger("domain_checker")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("domain_checker.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def check_availability(domain):
    """Return ``True`` if *domain* is unregistered using Whois."""

    try:
        w = whois.whois(domain)
        available = w.domain_name is None
        logger.info("Checked availability for %s: %s", domain, available)
        return available
    except PywhoisError as e:
        if "free" in str(e).lower():
            logger.info("Checked availability for %s: True", domain)
            return True
        logger.error("Whois lookup failed for %s: %s", domain, e)
    except Exception as e:
        logger.error("Error checking availability for %s: %s", domain, e)
    return None

def _parse_number(value):
    """Return ``value`` as ``float`` while respecting thousand separators.

    The function removes grouping symbols (``.`` or ``,``) that are used as
    thousand separators and normalises the decimal separator to ``.``. This
    allows numbers such as ``"1.234,56"`` or ``"1,234.56"`` to be parsed
    safely.
    """

    if isinstance(value, (int, float)):
        return float(value)

    # Keep only digits and potential separators.
    s = re.sub(r"[^0-9.,]", "", str(value))

    # Remove thousand separators (a dot or comma followed by groups of three
    # digits and then either another separator or the end of the string).
    s = re.sub(r"(?<=\d)[.,](?=\d{3}(?:[.,]|$))", "", s)

    # Convert a remaining comma to a decimal dot.
    s = s.replace(",", ".")

    return float(s)


def get_traffic(domain):
    """Return rough monthly visit estimate for *domain*.

    The function tries two public sources (StatsCrop and Hypestat).  Both
    provide *daily* visitor numbers which are scaled to a monthly value.  If
    neither source yields a result ``0`` is returned instead of ``"N/A"`` so
    callers always receive a number.
    """

    headers = {"User-Agent": "Mozilla/5.0"}

    def _from_text(text):
        match = re.search(r"Daily\s+Visitors[^0-9]*([0-9.,]+)", text, re.I)
        if not match:
            match = re.search(r"Daily\s+Pageviews[^0-9]*([0-9.,]+)", text, re.I)
        if match:
            return int(_parse_number(match.group(1)) * 30)
        return None

    sources = [
        ("StatsCrop", f"https://www.statscrop.com/www/{domain}"),
        ("Hypestat", f"https://hypestat.com/info/{domain}"),
    ]

    for name, url in sources:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            logger.info("%s response for %s: %s", name, domain, r.status_code)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            monthly = _from_text(soup.get_text(" ", strip=True))
            if monthly is not None:
                logger.info("Fetched traffic for %s via %s: %s", domain, name, monthly)
                return monthly
            logger.warning("Could not parse traffic data for %s via %s", domain, name)
        except Exception as e:
            logger.error("Error fetching traffic for %s via %s: %s", domain, name, e)

    logger.info("Returning 0 for traffic of %s", domain)
    return 0

def get_backlinks(domain):
    """Return number of backlinks for *domain*.

    A small count is obtained from HackerTarget's free API.  If that request
    fails or yields an error message the function falls back to scraping
    OpenLinkProfiler.  Should both approaches fail ``0`` is returned.
    """

    headers = {"User-Agent": "Mozilla/5.0"}

    # HackerTarget returns up to ten backlinks, one per line
    try:
        url = f"https://api.hackertarget.com/backlinks/?q={domain}"
        r = requests.get(url, headers=headers, timeout=10)
        logger.info("HackerTarget backlinks response for %s: %s", domain, r.status_code)
        r.raise_for_status()
        lines = [line for line in r.text.splitlines() if line.strip()]
        if lines and not lines[0].lower().startswith("error"):
            backlinks = len(lines)
            logger.info("Fetched backlinks for %s via HackerTarget: %s", domain, backlinks)
            return backlinks
    except Exception as e:
        logger.error("Error fetching backlinks for %s via HackerTarget: %s", domain, e)

    # Fallback: scrape OpenLinkProfiler summary page
    try:
        url = f"https://www.openlinkprofiler.org/r/{domain}"
        r = requests.get(url, headers=headers, timeout=10)
        logger.info("OpenLinkProfiler response for %s: %s", domain, r.status_code)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        match = re.search(r"Backlinks[^0-9]*([0-9.,]+)", text, re.I)
        if match:
            backlinks = int(_parse_number(match.group(1)))
            logger.info("Fetched backlinks for %s via OpenLinkProfiler: %s", domain, backlinks)
            return backlinks
        logger.warning("Could not parse backlinks for %s via OpenLinkProfiler", domain)
    except Exception as e:
        logger.error("Error fetching backlinks for %s via OpenLinkProfiler: %s", domain, e)

    logger.info("Returning 0 for backlinks of %s", domain)
    return 0
