import os
from pathlib import Path

try:
    import ujson as json
except ModuleNotFoundError:
    import json

path = Path() / "data" / "setu"
file = path / "customer_api.json"
if file.exists():
    with open(file, "r", encoding="utf8") as f:
        customer_api = json.load(f)
else:
    customer_api = {}
    if not path.exists():
        os.makedirs(path)


def save():
    with open(file, "w", encoding="utf8") as files:
        json.dump(customer_api, files, ensure_ascii=False, indent=4)
