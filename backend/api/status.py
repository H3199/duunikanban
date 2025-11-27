import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

THEIRSTACK_KEY = os.getenv("THEIRSTACK_API_KEY")

def get_credits() -> int:
    url = "https://api.theirstack.com/v0/billing/credit-balance"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {THEIRSTACK_KEY}"
        }
    response = requests.get(url, headers=headers)
    print(response)
    if not response.ok:
        raise RuntimeError(
            f"Credits fetch failed: {response.status_code} {response.text}"
        )
    payload = response.json()
    remaining = payload.get("api_credits", 0) - payload.get("used_api_credits", 0)
    return max(remaining, 0)
