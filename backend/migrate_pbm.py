import os
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
if not url or not key:
    print("Supabase credentials not found in .env")
    exit(1)

supabase: Client = create_client(url, key)

pbm_file = Path("backend/data/pbm_config.json")
if not pbm_file.exists():
    print("No JSON file found to migrate.")
    exit(0)

try:
    with open(pbm_file, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    print(f"Error reading JSON: {e}")
    exit(1)

rows = []
for cnes, data in config.items():
    rows.append({
        "cnes": cnes,
        "pbm": data.get("pbm", False),
        "link": data.get("link", "")
    })

if not rows:
    print("No rows to insert.")
else:
    # Upsert data to supabase
    res = supabase.table("pbm_config").upsert(rows).execute()
    print(f"Inserted {len(res.data)} rows into Supabase pbm_config table.")
