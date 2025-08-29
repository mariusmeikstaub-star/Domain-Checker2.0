import whois
import requests
import os

def check_availability(domain):
    try:
        w = whois.whois(domain)
        return w.domain_name is None
    except Exception:
        return True

def get_traffic(domain):
    api_key = os.getenv("SIMILARWEB_API_KEY")
    if not api_key:
        return None
    url = f"https://api.similarweb.com/v1/website/{domain}/traffic-and-engagement/visits?api_key={api_key}&country=world"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        visits = data.get("visits")
        if isinstance(visits, dict):
            return sum(visits.values())
        return None
    except Exception:
        return None

def get_backlinks(domain):
    api_key = os.getenv("OPR_API_KEY")
    if not api_key:
        return None
    url = f"https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D={domain}"
    headers = {"API-OPR": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        response = data.get("response", [])
        if response:
            return response[0].get("referring_domains")
        return None
    except Exception:
        return None
