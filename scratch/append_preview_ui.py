with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

preview_html = """
        <!-- COLIH Preview UI -->
        <div id="syncColihPreviewArea" style="display:none; margin-bottom: 1rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem;">
            <h4 style="margin-top:0; color:#ffaa00;">Revisão de Alterações COLIH</h4>
            <div id="syncColihDiff" style="font-size:13px; color:#ddd; max-height:150px; overflow-y:auto; margin-bottom:12px; background:rgba(0,0,0,0.2); padding:10px; border-radius:6px;"></div>
            <div style="display:flex; gap:10px;">
                <button class="btn btn-primary" onclick="commitColihSync()">Confirmar e Aplicar COLIH</button>
                <button class="btn btn-outline" onclick="discardColihSync()" style="color:#ef4444; border-color:#ef4444;">Descartar</button>
            </div>
        </div>
"""

if 'id="syncColihPreviewArea"' not in text:
    text = text.replace('<div id="importZipPanel"', preview_html + '\n        <div id="importZipPanel"')
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Preview UI added to index.html')
else:
    print('Preview UI already exists')
