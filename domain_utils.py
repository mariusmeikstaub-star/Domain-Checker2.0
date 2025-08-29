import json
import logging
import re

import requests

# Configure a basic logger that writes to ``domain_checker.log``.
logger = logging.getLogger("domain_checker")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("domain_checker.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def check_availability(domain):
    """Return ``True`` if *domain* is unregistered using RDAP."""

    url = f"https://rdap.org/domain/{domain}"
    try:
        r = requests.get(url, timeout=10)
        logger.info("RDAP response for %s: %s", domain, r.status_code)
        if r.status_code == 404:
            return True
        if r.ok:
            return False
        logger.error("Unexpected RDAP status for %s: %s", domain, r.status_code)
    except Exception as e:
        logger.error("Error checking availability for %s via RDAP: %s", domain, e)
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
    """Return an estimate of the number of pages for *domain* in Common Crawl."""

    try:
        collinfo = requests.get("https://index.commoncrawl.org/collinfo.json", timeout=10).json()
        latest = collinfo[0]["id"]
        url = f"https://index.commoncrawl.org/{latest}-index?url={domain}&output=json"
        r = requests.get(url, timeout=10)
        logger.info("CommonCrawl index response for %s: %s", domain, r.status_code)
        if r.ok:
            lines = [line for line in r.text.splitlines() if line.strip()]
            visits = len(lines)
            logger.info("Fetched traffic for %s: %s", domain, visits)
            return visits
    except Exception as e:
        logger.error("Error fetching traffic for %s via CommonCrawl: %s", domain, e)
    logger.info("Returning 'N/A' for traffic of %s", domain)
    return "N/A"

def get_backlinks(domain):
    """Return number of referring domains for *domain* using Web Graph."""

    url = f"https://webgraph.cc/api/graph?url={domain}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        logger.info("WebGraph API response for %s: %s", domain, r.status_code)
        r.raise_for_status()
        data = r.json()
        backlinks = _find_number(data, {"inlinks", "inbound", "inbound_count", "inCount"})
        if backlinks is not None:
            backlinks = int(backlinks)
            logger.info("Fetched backlinks for %s: %s", domain, backlinks)
            return backlinks
        logger.warning("Could not parse backlinks for %s", domain)
    except Exception as e:
        logger.error("Error fetching backlinks for %s: %s", domain, e)
    logger.info("Returning 'N/A' for backlinks of %s", domain)
    return "N/A"
