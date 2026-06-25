import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add count to medicos
old_search_medicos = r'''<div class="search-bar" style="display:flex; gap:10px; flex-wrap:wrap;">
      <input type="text" id="busca-colih-medico" placeholder="Filtrar médicos..." onkeyup="renderColihMedicos()" style="flex:1; min-width:200px;">'''

new_search_medicos = '''<div class="search-bar" style="display:flex; gap:10px; flex-wrap:wrap;">
      <input type="text" id="busca-colih-medico" placeholder="Filtrar médicos..." onkeyup="renderColihMedicos()" style="flex:1; min-width:200px;">'''

# Wait, the search bar is:
old_search_medicos_block = r'''<div class="search-bar" style="display:flex; gap:10px; flex-wrap:wrap;">
      <input type="text" id="busca-colih-medico" placeholder="Filtrar médicos..." onkeyup="renderColihMedicos()" style="flex:1; min-width:200px;">
      <select id="filtro-colih-especialidade" onchange="renderColihMedicos()" style="padding:12px; border-radius:8px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
          <option value="">Todas as Especialidades</option>
      </select>
      <select id="filtro-colih-visita" onchange="renderColihMedicos()" style="padding:12px; border-radius:8px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
          <option value="">Qualquer Data</option>
          <option value="recentes">Recentes (Até 6 meses)</option>
          <option value="antigos">Mais de 6 meses (Defasados)</option>
      </select>
    </div>'''

new_search_medicos_block = '''<div class="search-bar" style="display:flex; gap:10px; flex-wrap:wrap;">
      <input type="text" id="busca-colih-medico" placeholder="Filtrar médicos..." onkeyup="renderColihMedicos()" style="flex:1; min-width:200px;">
      <select id="filtro-colih-especialidade" onchange="renderColihMedicos()" style="padding:12px; border-radius:8px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
          <option value="">Todas as Especialidades</option>
      </select>
      <select id="filtro-colih-visita" onchange="renderColihMedicos()" style="padding:12px; border-radius:8px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
          <option value="">Qualquer Data</option>
          <option value="recentes">Recentes (Até 6 meses)</option>
          <option value="antigos">Mais de 6 meses (Defasados)</option>
      </select>
    </div>
    <div id="colih-medicos-count" style="margin-top:10px; font-size:13px; color:var(--text-secondary); font-weight:600;">Carregando médicos...</div>'''

text = text.replace(old_search_medicos_block, new_search_medicos_block)


# 2. Re-architect HLC Tab
old_hlc_tab = re.search(r'<section class=\"tab-panel\" id=\"tab-config-hlc\">.*?</section>', text, re.DOTALL).group(0)

new_hlc_tab = '''<section class="tab-panel" id="tab-config-hlc">
    
    <div style="background:var(--bg-card); border-radius:12px; padding:20px; border:1px solid var(--border-color); margin-top:20px;">
        <div style="display:flex; gap:10px; margin-bottom:15px; position:relative;">
            
            <div style="flex:1; position:relative;" class="custom-dropdown-container" id="dropdown-cnes">
                <input type="text" id="hlc-key-input" placeholder="Especialidade CNES (Pesquise...)" autocomplete="off" oninput="filtrarDropdownCNES()" onfocus="abrirDropdownCNES()" style="width:100%; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
                <div id="cnes-list-box" class="dropdown-list-box" style="display:none; position:absolute; top:100%; left:0; right:0; background:var(--bg-card); border:1px solid var(--border-color); border-radius:6px; margin-top:4px; max-height:200px; overflow-y:auto; z-index:100; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                </div>
            </div>
            
            <div style="flex:1; position:relative;" class="custom-dropdown-container" id="dropdown-hlc">
                <input type="text" id="hlc-val-input" placeholder="Classificação HLC-9 (Ex: Cirurgia geral)" autocomplete="off" oninput="filtrarDropdownHLC()" onfocus="abrirDropdownHLC()" style="width:100%; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
                <div id="hlc-list-box" class="dropdown-list-box" style="display:none; position:absolute; top:100%; left:0; right:0; background:var(--bg-card); border:1px solid var(--border-color); border-radius:6px; margin-top:4px; max-height:200px; overflow-y:auto; z-index:100; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                </div>
            </div>
            
            <button id="btn-adicionar-hlc" class="btn-primary" onclick="adicionarHlcDict()">Adicionar</button>
        </div>
        
        <div id="hlc-cards-container" style="display:flex; flex-direction:column; gap:16px; margin-top:20px;">
            <!-- Rendered via JS -->
        </div>
        
        <div style="margin-top:20px; display:flex; justify-content:flex-end;">
            <button class="btn-primary" onclick="salvarHlcDict()">💾 Salvar Dicionário</button>
        </div>
    </div>
</section>
'''

text = text.replace(old_hlc_tab, new_hlc_tab)

# 3. Add Custom CSS for dropdown list box items
css_to_add = '''
.dropdown-list-item {
    padding: 10px 12px;
    cursor: pointer;
    font-size: 13px;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border-color);
    transition: background 0.2s;
}
.dropdown-list-item:hover {
    background: var(--bg-hover);
}
.dropdown-list-item:last-child {
    border-bottom: none;
}
'''
text = text.replace('</style>', css_to_add + '\n</style>')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('index.html updated successfully with new HLC Layout and Custom Dropdowns.')
