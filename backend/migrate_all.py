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

DATA_DIR = Path("backend/data")

def migrate_dict(filename, table_name, pk_col):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"File {filename} not found.")
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        rows = []
        for k, v in data.items():
            rows.append({pk_col: k, "data": v})
        
        if rows:
            res = supabase.table(table_name).upsert(rows).execute()
            print(f"Migrated {len(res.data)} rows from {filename} to {table_name}.")
        else:
            print(f"No rows to migrate for {filename}.")
    except Exception as e:
        print(f"Error migrating {filename}: {e}")

def migrate_single_doc(filename, table_name, doc_id):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"File {filename} not found.")
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        res = supabase.table(table_name).upsert([{"id": doc_id, "data": data}]).execute()
        print(f"Migrated document {doc_id} from {filename} to {table_name}.")
    except Exception as e:
        print(f"Error migrating {filename}: {e}")

migrate_dict("tmo_custom.json", "tmo_custom", "cnes")
migrate_dict("pipeline.json", "pipeline", "cns")
migrate_dict("usuarios.json", "usuarios", "email")
migrate_single_doc("sync_config.json", "app_state", "sync_config")
migrate_single_doc("sync_status.json", "app_state", "sync_status")
