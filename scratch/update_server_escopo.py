import re

with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_code = """
@app.get("/api/config/escopo")
def api_get_config_escopo():
    config_file = DATA_DIR / "sync_config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"uf": "BA", "municipios_especificos": []}

@app.post("/api/config/escopo")
def api_post_config_escopo(body: dict):
    config_file = DATA_DIR / "sync_config.json"
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(body, f, ensure_ascii=False, indent=2)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
"""

pattern = r'@app\.get\("/api/config/escopo"\).*?(?=@app\.get\("/api/config/termos_apoio"\))'
if re.search(pattern, text, re.DOTALL):
    text = re.sub(pattern, new_code + '\n', text, flags=re.DOTALL)
    with open('backend/server.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('server.py updated for dynamic escopo')
else:
    print('Pattern not found')
