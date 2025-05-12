"""
Utility functions for interacting with the Supernova API.
"""

import requests
import json
import logging
from typing import Dict, Tuple, Union
from django.conf import settings

logger = logging.getLogger(__name__)

def get_active_basket_dict() -> Dict[str, str]:
    """
    Get active basket information from Supernova API.
    
    Returns:
        Dictionary mapping holder codes to pigeon IDs
    """
    url = f"{settings.SUPERNOVA_BASE_URL}/api/automation/presort/ready-holders"
    headers = {
        'api-key': settings.SUPERNOVA_API_KEY,
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return {
            holder["holder_code"]: holder["pigeon_id"]
            for holder in data.get('holders', [])
        }
    except Exception as e:
        logger.error(f"Error fetching active baskets: {e}")
        return {}

def get_inquiry_url(holder_id: str) -> str:
    """Generate the Supernova inquiry URL for a holder."""
    return (
        f"{settings.SUPERNOVA_BASE_URL}/api/presort/holder/{holder_id}/pigeon"
        f"?Authorization={settings.SUPERNOVA_AUTH_TOKEN}"
    )

def inquire_holder(barcode: str) -> Tuple[bool, Union[int, str]]:
    """
    Query Supernova API for holder information.
    
    Args:
        barcode: The holder barcode to query
        
    Returns:
        Tuple of (success: bool, result: Union[int, str])
        If successful, result is the pigeon ID
        If failed, result is the error message
    """
    try:
        response = requests.get(get_inquiry_url(barcode))
        status_code = response.status_code
        
        if status_code == 200:
            try:
                data = response.json()
                try:
                    return True, data['result']['pigeon']
                except KeyError:
                    return False, str(data)
            except json.JSONDecodeError:
                return False, f"Invalid JSON response: {response.text[:200]}"
        else:
            error_preview = response.text[:200] if response.text else "No error details"
            return False, f"HTTP {status_code}: {error_preview}"
            
    except requests.RequestException as e:
        logger.error(f"Request failed for barcode {barcode}: {e}")
        return False, f"Request failed: {str(e)}" 