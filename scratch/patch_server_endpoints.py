import re

with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix get_pbm_config
text = text.replace('return _PBM_CACHE', 'return _PBM_CACHE or {}')

# Add missing endpoints
endpoints_code = """
# ─── COLIH DATA ENDPOINTS ───────────────────────────────────────────────────
@app.get("/api/colih/medicos")
def api_get_colih_medicos():
    if not supabase: return []
    try:
        res = supabase.table("dados_colih_medicos").select("*").execute()
        return res.data
    except Exception as e:
        print("Erro colih medicos:", e)
        return []

@app.get("/api/colih/membros")
def api_get_colih_membros():
    if not supabase: return []
    try:
        res = supabase.table("dados_colih_membros").select("*").execute()
        return res.data
    except Exception as e:
        print("Erro colih membros:", e)
        return []

# ─── CONFIG ENDPOINTS ───────────────────────────────────────────────────────
@app.get("/api/config/escopo")
def api_get_config_escopo():
    # Retorna o escopo do CNES fixo por enquanto
    return {
        "municipios": [
            {"codigo": "292740", "nome": "Salvador"},
            {"codigo": "291920", "nome": "Lauro de Freitas"},
            {"codigo": "292530", "nome": "Simões Filho"},
            {"codigo": "290570", "nome": "Camaçari"},
            {"codigo": "291992", "nome": "Madre de Deus"},
            {"codigo": "292370", "nome": "São Francisco do Conde"}
        ]
    }

@app.get("/api/config/termos_apoio")
def api_get_config_termos():
    return ["recuperador", "cell saver"]
"""

if '/api/colih/medicos' not in text:
    text += endpoints_code
    with open('backend/server.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Server patched successfully')
else:
    print('Endpoints already exist')
