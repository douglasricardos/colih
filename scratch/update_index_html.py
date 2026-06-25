import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

sidebar_html = """
  <!-- ─── SIDEBAR ESQUERDA (GLPI Style) ───────────────────────── -->
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <img src="logo-colih-portal.png" alt="COLIH" style="max-height: 40px; margin-bottom: 5px;"><br>
      COLIH Salvador
    </div>
    <ul class="sidebar-menu">
      <li class="menu-group">Dados SUS</li>
      <li class="menu-item active" onclick="openTab('hospitais', this)"><i class="fas fa-hospital"></i> Hospitais</li>
      <li class="menu-item" onclick="openTab('profissionais', this)"><i class="fas fa-user-md"></i> Profissionais</li>
      <li class="menu-item" onclick="openTab('stats', this)"><i class="fas fa-chart-line"></i> Captação / HLC</li>

      <li class="menu-group">Dados COLIH</li>
      <li class="menu-item" onclick="openTab('colih-medicos', this)"><i class="fas fa-handshake"></i> Cooperadores</li>
      <li class="menu-item" onclick="openTab('colih-membros', this)"><i class="fas fa-users"></i> Membros</li>

      <li class="menu-group">Configurações</li>
      <li class="menu-item" onclick="openTab('config-hlc', this)"><i class="fas fa-book-medical"></i> Dicionário HLC-9</li>
      <li class="menu-item" onclick="openTab('config-cnes', this)"><i class="fas fa-map-marked-alt"></i> Escopo CNES</li>
      <li class="menu-item" onclick="openTab('config-apoio', this)"><i class="fas fa-cogs"></i> Termos de Apoio</li>
    </ul>
  </aside>

  <!-- ─── CONTEÚDO PRINCIPAL ────────────────────────────────────── -->
  <main class="main-content">
    <div class="topbar">
      <!-- Sync Button -->
      <div class="sync-status" id="btnOpenSyncModal" onclick="document.getElementById('syncStatusModal').style.display='flex'">
        <i class="fas fa-database"></i> Status: <span id="lblDataSync">Carregando...</span>
      </div>
    </div>
"""

# Replace the start of body
text = re.sub(r'<body>\s*<nav class="navbar">.*?</nav>', '<body>\n' + sidebar_html, text, flags=re.DOTALL)

# Add closing </main> right before the modals (before <div id="syncStatusModal")
text = text.replace('<div id="syncStatusModal"', '</main>\n  <div id="syncStatusModal"')

# Now we need to extract the config tabs. The current "tab-configuracoes" needs to be split.
# Find tab-configuracoes
config_match = re.search(r'<section class="tab-panel" id="tab-configuracoes">(.*?)</section>', text, re.DOTALL)
if config_match:
    config_inner = config_match.group(1)
    
    # We will replace tab-configuracoes with three separate sections.
    new_configs = """
  <!-- ⚙️ CONFIG: DICIONÁRIO HLC-9 ⚙️ -->
  <section class="tab-panel" id="tab-config-hlc" style="display:none;">
    <div class="panel-header">
      <h1>⚙️ Dicionário de Especialidades HLC-9</h1>
      <p>Gerencie o mapeamento De-Para das especialidades médicas.</p>
    </div>
    <div style="background:var(--bg-card); border-radius:12px; padding:20px; border:1px solid var(--border-color); margin-top:20px;">
        <div style="display:flex; gap:10px; margin-bottom:15px;">
            <input type="text" id="hlc-key-input" placeholder="Especialidade CNES (Ex: CARDIOLOGIA)" style="flex:1; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-dark); color:#fff;">
            <input type="text" id="hlc-val-input" placeholder="Termo HLC-9 (Ex: CLÍNICA MÉDICA)" style="flex:1; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-dark); color:#fff;">
            <button class="btn-primary" onclick="adicionarHlcDict()">Adicionar</button>
        </div>
        <table class="data-table" id="table-hlc-dict">
            <thead>
                <tr>
                    <th>Termo CNES / Origem</th>
                    <th>Classificação HLC-9</th>
                    <th width="100">Ações</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
        <div style="margin-top:15px; text-align:right;">
            <button class="btn-primary" onclick="salvarHlcDict()">💾 Salvar Dicionário</button>
        </div>
    </div>
  </section>

  <!-- ⚙️ CONFIG: ESCOPO CNES ⚙️ -->
  <section class="tab-panel" id="tab-config-cnes" style="display:none;">
    <div class="panel-header">
      <h1>🌍 Escopo Geográfico (CNES)</h1>
      <p>Municípios cobertos pela busca de hospitais e médicos no DATASUS.</p>
    </div>
    <div id="cnes-escopo-list" style="margin-top:20px; display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:16px;">
        Carregando escopo...
    </div>
  </section>

  <!-- ⚙️ CONFIG: TERMOS DE EQUIPAMENTOS DE APOIO ⚙️ -->
  <section class="tab-panel" id="tab-config-apoio" style="display:none;">
    <div class="panel-header">
      <h1>🛠️ Termos de Equipamentos de Apoio COLIH</h1>
      <p>Termos buscados na lista de equipamentos hospitalares para marcar Hospitais com Apoio.</p>
    </div>
    <div id="apoio-termos-list" style="margin-top:20px; display:flex; flex-wrap:wrap; gap:10px;">
        Carregando termos...
    </div>
  </section>
"""
    text = text.replace(config_match.group(0), new_configs)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('index.html updated for Sidebar layout')
