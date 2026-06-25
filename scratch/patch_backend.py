import re

with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'# ─── COLIH SYNC ENDPOINTS ───────────────────────────────────────────────────.*', text, re.DOTALL)
if m:
    colih_endpoints = m.group(0)
    text = text.replace(colih_endpoints, '')
    
    # Also add hlc-dict endpoint
    hlc_dict_endpoint = """
@app.get("/api/config/hlc-dict")
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
    return {}
"""
    
    colih_endpoints = colih_endpoints + hlc_dict_endpoint
    
    text = text.replace('if FRONTEND_DIR.exists():', colih_endpoints + '\nif FRONTEND_DIR.exists():')
    
    with open('backend/server.py', 'w', encoding='utf-8') as f:
        f.write(text)
    
    print('server.py patched successfully.')
else:
    print('COLIH endpoints not found.')
