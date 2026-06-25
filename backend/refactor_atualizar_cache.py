import re
import os

with open('scripts/atualizar_cache.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add imports for supabase if not present
if "from supabase import" not in text:
    imports = """import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(Path(__file__).parent.parent / "backend" / ".env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

from datetime import datetime"""
    text = re.sub(r'import json\nfrom datetime import datetime', imports, text, count=1)

old_save = """    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(sync_status, f, ensure_ascii=False, indent=2)"""

new_save = """    if supabase:
        try:
            supabase.table("app_state").upsert({"id": "sync_status", "data": sync_status}).execute()
        except:
            pass
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(sync_status, f, ensure_ascii=False, indent=2)"""

if old_save in text:
    text = text.replace(old_save, new_save)
    with open('scripts/atualizar_cache.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("atualizar_cache.py refactored for Supabase")
else:
    print("Could not find the target string in atualizar_cache.py")

