import re
import os

with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add imports at the top
imports = """import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

from pathlib import Path"""

text = re.sub(r'import json\nfrom pathlib import Path', imports, text, count=1)

# 2. Replace get_pbm_config
old_get_pbm = """_PBM_CACHE = None
def get_pbm_config():
    global _PBM_CACHE
    if _PBM_CACHE is None:
        _PBM_CACHE = load_json(Path("backend/data/pbm_config.json"), {})
    return _PBM_CACHE"""

new_get_pbm = """_PBM_CACHE = None
def get_pbm_config():
    global _PBM_CACHE
    if _PBM_CACHE is None:
        _PBM_CACHE = {}
        if supabase:
            try:
                res = supabase.table("pbm_config").select("*").execute()
                for row in res.data:
                    _PBM_CACHE[row["cnes"]] = {"pbm": row["pbm"], "link": row.get("link", "")}
            except Exception as e:
                print("Error loading PBM config from Supabase:", e)
    return _PBM_CACHE"""

text = text.replace(old_get_pbm, new_get_pbm)

# 3. Replace toggle_pbm
old_toggle_pbm = """def toggle_pbm(cnes: str, body: dict):
    global _PBM_CACHE, _ESTAB_CACHE
    pbm_file = Path("backend/data/pbm_config.json")
    config = load_json(pbm_file, {})
    if body.get("pbm") is False:
        if cnes in config:
            del config[cnes]
    else:
        config[cnes] = {"pbm": True, "link": body.get("link", "")}
    save_json(pbm_file, config)
    _PBM_CACHE = None # Clear cache
    
    # Update in-memory estab cache dynamically!
    if _ESTAB_CACHE is not None:
        for h in _ESTAB_CACHE.get("estabelecimentos", []):
            if h.get("cnes") == cnes:
                enrich_estab(h) # re-enrich this specific hospital
                break
                
    return {"status": "ok", "cnes": cnes, "pbm": body.get("pbm", False)}"""

new_toggle_pbm = """def toggle_pbm(cnes: str, body: dict):
    global _PBM_CACHE, _ESTAB_CACHE
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
        
    try:
        if body.get("pbm") is False:
            supabase.table("pbm_config").delete().eq("cnes", cnes).execute()
        else:
            supabase.table("pbm_config").upsert({
                "cnes": cnes,
                "pbm": True,
                "link": body.get("link", "")
            }).execute()
    except Exception as e:
        print("Error saving PBM to Supabase:", e)
        raise HTTPException(status_code=500, detail="Failed to save to database")
        
    _PBM_CACHE = None # Clear cache
    
    # Update in-memory estab cache dynamically!
    if _ESTAB_CACHE is not None:
        for h in _ESTAB_CACHE.get("estabelecimentos", []):
            if h.get("cnes") == cnes:
                enrich_estab(h) # re-enrich this specific hospital
                break
                
    return {"status": "ok", "cnes": cnes, "pbm": body.get("pbm", False)}"""

text = text.replace(old_toggle_pbm, new_toggle_pbm)

with open('backend/server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('server.py successfully refactored for Supabase')
