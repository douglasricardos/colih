import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Rename sidebar items
text = text.replace('<li class="menu-item" onclick="openTab(\'colih-medicos\', this)"><i data-lucide="users"></i> Cooperadores</li>', '<li class="menu-item" onclick="openTab(\'colih-medicos\', this)"><i data-lucide="users"></i> Lista de Médicos</li>')
text = text.replace('<li class="menu-item" onclick="openTab(\'colih-membros\', this)"><i data-lucide="users"></i> Membros Regionais</li>', '<li class="menu-item" onclick="openTab(\'colih-membros\', this)"><i data-lucide="users"></i> Membros</li>')

# Replace Medicos tab
old_medicos = r'<!-- ─── ABA: COLIH MEDICOS ───────────────────────────────────── -->.*?</section>'
new_medicos = '''<!-- ─── ABA: COLIH MEDICOS ───────────────────────────────────── -->
  <section class="tab-panel" id="tab-colih-medicos">
    <div class="panel-header" style="background: linear-gradient(135deg, rgba(255, 170, 0, 0.1), transparent); border-bottom: 1px solid rgba(255, 170, 0, 0.2);">
      <h1>🤝 Lista de Médicos</h1>
      <p>Lista de médicos cadastrados na base de dados da COLIH. Atualizada a partir do sistema oficial.</p>
    </div>
    <div class="search-bar" style="display:flex; gap:10px; flex-wrap:wrap;">
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
    <div class="results-grid" id="colih-medicos-grid" style="grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));"></div>
  </section>'''

text = re.sub(old_medicos, new_medicos, text, flags=re.DOTALL)

# Replace Membros tab
old_membros = r'<!-- ─── ABA: COLIH MEMBROS ───────────────────────────────────── -->.*?</section>'
new_membros = '''<!-- ─── ABA: COLIH MEMBROS ───────────────────────────────────── -->
  <section class="tab-panel" id="tab-colih-membros">
    <div class="panel-header" style="background: linear-gradient(135deg, rgba(255, 170, 0, 0.1), transparent); border-bottom: 1px solid rgba(255, 170, 0, 0.2);">
      <h1>👥 Membros</h1>
      <p>Membros do comitê com validação de geolocalização para mapa de prospectos.</p>
    </div>
    <div class="search-bar" style="display:flex; gap:10px; flex-wrap:wrap;">
      <input type="text" id="busca-colih-membro" placeholder="Filtrar membros..." onkeyup="renderColihMembros()" style="flex:1; min-width:200px;">
      <select id="filtro-colih-regiao" onchange="renderColihMembros()" style="padding:12px; border-radius:8px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
          <option value="">Todos os Grupos (Regiões)</option>
      </select>
    </div>
    <div class="results-grid" id="colih-membros-grid" style="grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); margin-top:20px;"></div>
  </section>'''

text = re.sub(old_membros, new_membros, text, flags=re.DOTALL)

# Append Modal
modal_html = '''
<!-- Modal: Editar Coordenadas -->
<div class="modal-overlay" id="modal-coords" onclick="fecharModal('modal-coords')">
  <div class="modal-box" onclick="event.stopPropagation()" style="max-width: 400px;">
    <div class="modal-header">
      <h3>📍 Editar Coordenadas</h3>
      <button class="modal-close" onclick="fecharModal('modal-coords')">✕</button>
    </div>
    <div class="modal-body">
      <input type="hidden" id="coord-membro-id" />
      <div class="form-group">
        <label>Membro</label>
        <input type="text" id="coord-membro-nome" class="form-control" readonly style="background:var(--bg-card);" />
      </div>
      <div class="form-group">
        <label>Latitude</label>
        <input type="number" step="any" id="coord-lat" class="form-control" placeholder="Ex: -12.9714" />
      </div>
      <div class="form-group">
        <label>Longitude</label>
        <input type="number" step="any" id="coord-lon" class="form-control" placeholder="Ex: -38.5014" />
      </div>
      <div class="form-group">
        <label>Endereço / Referência (Opcional)</label>
        <input type="text" id="coord-endereco" class="form-control" placeholder="Rua, Bairro, Cidade..." />
      </div>
      <p style="font-size:12px; color:var(--text-muted); margin-top:10px;">Dica: Você pode copiar as coordenadas clicando com o botão direito no local desejado no Google Maps.</p>
    </div>
    <div class="modal-footer">
      <button class="btn-primary" onclick="salvarCoordenadasMembro()" style="width:100%;">Salvar Coordenadas</button>
    </div>
  </div>
</div>
'''

if 'modal-coords' not in text:
    text = text.replace('<!-- ═══════════════════════════════════════════════════════ MODAIS -->', '<!-- ═══════════════════════════════════════════════════════ MODAIS -->\n' + modal_html)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('index.html updated successfully.')
