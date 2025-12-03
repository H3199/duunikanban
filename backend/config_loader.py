import json
import os
from functools import lru_cache

CONFIG_PATH = os.getenv("CONFIG_PATH", "/app/config.json")

@lru_cache
def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
