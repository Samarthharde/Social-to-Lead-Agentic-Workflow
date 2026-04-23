"""
Lead capture tool for AutoStream agent.
Simulates a CRM API call when a high-intent user provides their details.
"""

import json
import datetime
from typing import Optional


def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    """
    Mock CRM API function to capture a qualified lead.

    Args:
        name: Full name of the prospect
        email: Email address of the prospect
        platform: Creator platform (YouTube, Instagram, TikTok, etc.)

    Returns:
        dict with status and lead_id
    """
    # Simulate a successful API response
    lead_id = f"LEAD-{abs(hash(email)) % 100000:05d}"
    timestamp = datetime.datetime.now().isoformat()

    print("\n" + "=" * 50)
    print("✅  LEAD CAPTURED SUCCESSFULLY")
    print("=" * 50)
    print(f"  Name     : {name}")
    print(f"  Email    : {email}")
    print(f"  Platform : {platform}")
    print(f"  Lead ID  : {lead_id}")
    print(f"  Time     : {timestamp}")
    print("=" * 50 + "\n")

    return {
        "status": "success",
        "lead_id": lead_id,
        "message": f"Lead captured successfully: {name}, {email}, {platform}",
        "timestamp": timestamp,
    }
