import re
from pathlib import Path

with open('backend/server.py', 'r', encoding='utf-8') as f:
    content = f.read()

helper = """
# ─── Helper COLIH ──────────────────────────────────────────────────────────────
_colih_cache = None
def get_colih_cache():
    global _colih_cache
    if _colih_cache is None and supabase:
        try:
            docs = supabase.table("dados_colih_medicos").select("*").execute().data
            mems = supabase.table("dados_colih_membros").select("*").execute().data
            import unicodedata
            def norm(s):
                if not s: return ""
                return ''.join(c for c in unicodedata.normalize('NFKD', str(s).upper()) if not unicodedata.combining(c)).strip()
            
            docs_map = {norm(d.get('nome')): d for d in docs}
            mems_map = {norm(m.get('nome')): m for m in mems}
            _colih_cache = {"medicos": docs_map, "membros": mems_map}
        except:
            pass
    return _colih_cache or {"medicos": {}, "membros": {}}

def reset_colih_cache():
    global _colih_cache
    _colih_cache = None

def enrich_with_colih(medicos):
    cache = get_colih_cache()
    import unicodedata
    def norm(s):
        if not s: return ""
        return ''.join(c for c in unicodedata.normalize('NFKD', str(s).upper()) if not unicodedata.combining(c)).strip()
        
    for m in medicos:
        nome_norm = norm(m.get('nome'))
        if nome_norm in cache['medicos']:
            m['colih'] = cache['medicos'][nome_norm]
"""

if 'def enrich_with_colih(medicos):' not in content:
    content = content.replace('# ─── Enriquecimento de Currículos', helper + '\n# ─── Enriquecimento de Currículos')
    with open('backend/server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('COLIH helper added to server.py')
else:
    print('COLIH helper already present.')
