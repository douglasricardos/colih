import re
import os

with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Helper function to get from supabase
# Instead of doing massive regex, we'll write specific wrappers

# 1. Pipeline
text = re.sub(
    r'def get_pipeline\(\):[\s\S]*?return load_json\(PIPELINE_FILE, \{\}\)',
    '''def get_pipeline():
    if supabase:
        try:
            res = supabase.table("pipeline").select("*").execute()
            return {row["cns"]: row["data"] for row in res.data}
        except:
            pass
    return load_json(PIPELINE_FILE, {})''',
    text
)

text = re.sub(
    r'save_json\(PIPELINE_FILE, pipeline\)',
    '''if supabase:
        try:
            # We must upsert the specific cns that was modified
            # It's easier to just upsert everything or the specific one.
            # But the functions modify pipeline[cns]
            rows = [{"cns": k, "data": v} for k, v in pipeline.items()]
            supabase.table("pipeline").upsert(rows).execute()
        except Exception as e: print("Supabase error:", e)
    else:
        save_json(PIPELINE_FILE, pipeline)''',
    text
)

# 2. Usuarios
text = re.sub(
    r'def get_usuarios\(\):[\s\S]*?return load_json\(USUARIOS_FILE, \{\}\)',
    '''def get_usuarios():
    if supabase:
        try:
            res = supabase.table("usuarios").select("*").execute()
            return {row["email"]: row["data"] for row in res.data}
        except:
            pass
    return load_json(USUARIOS_FILE, {})''',
    text
)

text = re.sub(
    r'save_json\(USUARIOS_FILE, usuarios\)',
    '''if supabase:
        try:
            rows = [{"email": k, "data": v} for k, v in usuarios.items()]
            supabase.table("usuarios").upsert(rows).execute()
        except Exception as e: print("Supabase error:", e)
    else:
        save_json(USUARIOS_FILE, usuarios)''',
    text
)

# 3. TMO Custom
text = re.sub(
    r'config = load_json\(TMO_CUSTOM_FILE, \{\}\)\n    config\[cnes_id\] = dados_tmo',
    '''config = load_json(TMO_CUSTOM_FILE, {})
    config[cnes_id] = dados_tmo
    if supabase:
        try:
            supabase.table("tmo_custom").upsert({"cnes": cnes_id, "data": dados_tmo}).execute()
        except Exception as e: print("Supabase error:", e)''',
    text
)

text = re.sub(
    r'save_json\(TMO_CUSTOM_FILE, config\)',
    '''if not supabase:
        save_json(TMO_CUSTOM_FILE, config)''',
    text
)

text = re.sub(
    r'tmo_config = load_json\(TMO_CUSTOM_FILE, \{\}\)',
    '''tmo_config = {}
    if supabase:
        try:
            res = supabase.table("tmo_custom").select("*").execute()
            tmo_config = {row["cnes"]: row["data"] for row in res.data}
        except:
            pass
    if not tmo_config:
        tmo_config = load_json(TMO_CUSTOM_FILE, {})''',
    text
)

# 4. Sync Config
text = re.sub(
    r'def get_sync_config\(\):[\s\S]*?return \{\"uf\": \"BA\", \"municipios_especificos\": \[\], \"descricao\": \"Bahia \(estado completo\)\"\}',
    '''def get_sync_config():
    if supabase:
        try:
            res = supabase.table("app_state").select("data").eq("id", "sync_config").execute()
            if res.data: return res.data[0]["data"]
        except:
            pass
    config_file = DATA_DIR / "sync_config.json"
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"uf": "BA", "municipios_especificos": [], "descricao": "Bahia (estado completo)"}''',
    text
)

text = re.sub(
    r'def save_sync_config\(body: dict\):[\s\S]*?json\.dump\(body, f, indent=4, ensure_ascii=False\)',
    '''def save_sync_config(body: dict):
    if supabase:
        try:
            supabase.table("app_state").upsert({"id": "sync_config", "data": body}).execute()
        except:
            pass
    config_file = DATA_DIR / "sync_config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(body, f, indent=4, ensure_ascii=False)''',
    text
)


with open('backend/server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('server.py refactored for pipeline, usuarios, tmo, sync_config')
