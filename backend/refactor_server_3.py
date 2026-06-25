import re

with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_get = """@app.get("/api/status")
def get_sync_status():
    status_path = DATA_DIR / "sync_status.json"
    if status_path.exists():
        with open(status_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sucesso": False, "status_geral": "Nunca sincronizado"}"""

new_get = """@app.get("/api/status")
def get_sync_status():
    if supabase:
        try:
            res = supabase.table("app_state").select("data").eq("id", "sync_status").execute()
            if res.data: return res.data[0]["data"]
        except:
            pass
            
    status_path = DATA_DIR / "sync_status.json"
    if status_path.exists():
        with open(status_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sucesso": False, "status_geral": "Nunca sincronizado"}"""

if old_get in text:
    text = text.replace(old_get, new_get)
    with open('backend/server.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Refactored get_sync_status")
else:
    print("Could not find get_sync_status in server.py")
