import re

with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_endpoint = '''@app.get("/api/colih/membros")
def api_get_colih_membros():
    if not supabase: return []
    try:
        res = supabase.table("dados_colih_membros").select("*").execute()
        return res.data
    except Exception as e:
        print("Erro colih membros:", e)
        return []

@app.post("/api/colih/membros/{membro_id}/coords")
def api_update_colih_membros_coords(membro_id: int, body: dict):
    if not supabase: return {"success": False, "error": "No DB"}
    try:
        lat = body.get('lat')
        lon = body.get('lon')
        endereco = body.get('endereco_atual')
        update_data = {}
        if lat is not None: update_data['lat'] = lat
        if lon is not None: update_data['lon'] = lon
        if endereco is not None: update_data['endereco_atual'] = endereco
        
        supabase.table("dados_colih_membros").update(update_data).eq("id", membro_id).execute()
        return {"success": True}
    except Exception as e:
        print("Erro atualizando coordenadas:", e)
        return {"success": False, "error": str(e)}
'''

old_endpoint = re.search(r'@app\.get\(\"/api/colih/membros\"\).*?return \[\]\n', text, re.DOTALL).group(0)
text = text.replace(old_endpoint, new_endpoint)

with open('backend/server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Coord endpoint added to server.py')
