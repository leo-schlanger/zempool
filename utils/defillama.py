import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BASE_URL = "https://api.llama.fi"

def get_protocol_summary(protocol_slug: str):
    try:
        url = f"{BASE_URL}/summary/fees/{protocol_slug}?dataType=dailyFees"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"[defillama] Failed to fetch protocol fee summary: {e}")
        return None

def get_protocol_tvl(protocol_slug: str):
    try:
        url = f"{BASE_URL}/protocol/{protocol_slug}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"[defillama] Failed to fetch TVL data: {e}")
        return None

def list_defillama_protocols():
    try:
        url = f"{BASE_URL}/protocols"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"[defillama] Failed to fetch protocols: {e}")
        return []
