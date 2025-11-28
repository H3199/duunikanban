import os
import json
import requests
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

load_dotenv()

THEIRSTACK_KEY = os.getenv("THEIRSTACK_API_KEY")

router = APIRouter(tags=["status"])


@router.get("/status/credits")
def fetch_credits():
    try:
        return {"remaining_credits": get_credits()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
