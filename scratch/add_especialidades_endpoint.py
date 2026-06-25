import re

with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_endpoint = '''
cnes_especialidades_cache = []

@app.get("/api/cnes/especialidades")
def api_get_cnes_especialidades():
    global cnes_especialidades_cache
    if cnes_especialidades_cache:
        return cnes_especialidades_cache
        
    sp_set = set()
    
    # 1. Puxar do cache de medicos do CNES
    cache_file = DATA_DIR / "medicos_cache.json"
    if cache_file.exists():
        try:
            import json
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                docs = data.get("medicos", [])
                for d in docs:
                    esp = d.get("especialidade")
                    if esp:
                        # O CNES retorna especialidades separadas por " / "
                        for e in esp.split(" / "):
                            clean_e = e.strip().upper()
                            if clean_e: sp_set.add(clean_e)
        except Exception as e:
            print("Erro lendo cache de especialidades CNES:", e)
            
    # 2. Puxar da base da COLIH
    if supabase:
        try:
            res = supabase.table("dados_colih_medicos").select("especialidade_1_colih, especialidade_1_hid").execute()
            for row in res.data:
                e1 = row.get("especialidade_1_colih")
                e2 = row.get("especialidade_1_hid")
                if e1: sp_set.add(e1.strip().upper())
                if e2: sp_set.add(e2.strip().upper())
        except Exception as e:
            print("Erro lendo especialidades COLIH:", e)
            
    cnes_especialidades_cache = sorted(list(sp_set))
    return cnes_especialidades_cache
'''

old_get_hospitais = re.search(r'@app\.get\(\"/api/hospitais\"\).*?return res\.data\n', text, re.DOTALL).group(0)
text = text.replace(old_get_hospitais, new_endpoint + '\n' + old_get_hospitais)

with open('backend/server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Endpoint /api/cnes/especialidades adicionado.")
