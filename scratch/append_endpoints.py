with open('backend/server.py', 'a', encoding='utf-8') as f:
    f.write('''

# ─── COLIH SYNC ENDPOINTS ───────────────────────────────────────────────────
from sync_colih import sync_colih_data

@app.post("/api/colih/sync")
def api_colih_sync(action: str = Query("preview", description="'preview', 'commit', or 'discard'")):
    """
    Sincroniza os dados da COLIH.
    - preview: Baixa dados e retorna diff sem salvar.
    - commit: Salva os dados previamente processados no preview.
    - discard: Descarta o preview.
    """
    try:
        if action == "preview":
            res = sync_colih_data(preview=True)
            return res
        elif action == "commit":
            res = sync_colih_data(commit=True)
            return res
        elif action == "discard":
            res = sync_colih_data(discard=True)
            return res
        else:
            return {"success": False, "error": "Invalid action"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
''')
print('Endpoints added to server.py')
