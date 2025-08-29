import json
import logging
import re

import whois
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
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


def _find_number(data, keys):
    """Return the first numeric value found for any of ``keys`` in ``data``."""

    if isinstance(data, dict):
        for k, v in data.items():
            if k in keys and isinstance(v, (int, float, str)):
                try:
                    return _parse_number(v)
                except ValueError:
                    pass
            result = _find_number(v, keys)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = _find_number(item, keys)
            if result is not None:
                return result
    return None


def get_traffic(domain):
    """Return estimated monthly visits for *domain* via SimilarWeb."""

    url = f"https://www.similarweb.com/website/{domain}/"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            response = page.goto(url, timeout=10000)
            status = response.status if response else "N/A"
            logger.info("SimilarWeb HTML response for %s: %s", domain, status)
            script = page.locator("script#__NEXT_DATA__")
            if script.count() > 0:
                data = json.loads(script.first.inner_text())
                visits = _find_number(
                    data, {"visits", "estimatedVisits", "visitsValue", "totalVisits"}
                )
                if visits is not None:
                    visits = int(visits)
                    logger.info("Fetched traffic for %s: %s", domain, visits)
                    return visits
            logger.warning("Could not parse traffic data for %s", domain)
    except Exception as e:
        logger.error("Error fetching traffic for %s: %s", domain, e)
    logger.info("Returning 'N/A' for traffic of %s", domain)
    return "N/A"

def get_backlinks(domain):
    """Return number of backlinks for *domain* via OpenLinkProfiler."""

    url = f"https://openlinkprofiler.org/r/{domain}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            response = page.goto(url, timeout=10000)
            status = response.status if response else "N/A"
            logger.info("OpenLinkProfiler HTML response for %s: %s", domain, status)
            soup = BeautifulSoup(page.content(), "html.parser")
            text = soup.get_text(" ", strip=True)
            match = re.search(r"Backlinks[^0-9]*([0-9.,]+)", text)
            if match:
                backlinks = int(_parse_number(match.group(1)))
                logger.info("Fetched backlinks for %s: %s", domain, backlinks)
                return backlinks
            logger.warning("Could not parse backlinks for %s", domain)
    except Exception as e:
        logger.error("Error fetching backlinks for %s: %s", domain, e)
    logger.info("Returning 'N/A' for backlinks of %s", domain)
    return "N/A"
