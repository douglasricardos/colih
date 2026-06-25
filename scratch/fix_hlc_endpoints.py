import re

with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_get = '''@app.get("/api/config/hlc-dict")
def api_get_config_hlc_dict():
    config_file = DATA_DIR / "pbm_config.json"
    if config_file.exists():
        try:
            import json
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("hlc_dict", {})
        except:
            pass
    return {}'''

new_endpoints = '''@app.get("/api/config/hlc-dict")
def api_get_config_hlc_dict():
    config_file = DATA_DIR / "hlc_dict.json"
    if config_file.exists():
        try:
            import json
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

@app.post("/api/config/hlc-dict")
def api_post_config_hlc_dict(body: dict):
    config_file = DATA_DIR / "hlc_dict.json"
    try:
        import json
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(body, f, ensure_ascii=False, indent=2)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}'''

text = text.replace(old_get, new_endpoints)

with open('backend/server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('server.py updated with HLC dict endpoints.')
