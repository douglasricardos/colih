import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

sidebar_html = """
<div style="display: flex; height: calc(100vh - 60px); overflow: hidden;">
  <!-- ─── SIDEBAR ESQUERDA (GLPI Style) ───────────────────────── -->
  <aside class="sidebar" id="sidebar">
    <!-- MODULE: SUS -->
    <ul class="sidebar-menu" id="sidebar-sus">
      <li class="menu-group">Dados do SUS</li>
      <li class="menu-item active" onclick="openTab('hospitais', this)"><i class="fas fa-hospital"></i> Instituições</li>
      <li class="menu-item" onclick="openTab('medicos', this)"><i class="fas fa-user-md"></i> Profissionais</li>
      <li class="menu-item" onclick="openTab('pipeline', this)"><i class="fas fa-clipboard-list"></i> Prospectos <span class="tab-badge" id="pipeline-count">0</span></li>
      <li class="menu-item" onclick="openTab('stats', this)"><i class="fas fa-chart-line"></i> Captação / HLC</li>
    </ul>

    <!-- MODULE: COLIH -->
    <ul class="sidebar-menu" id="sidebar-colih" style="display:none;">
      <li class="menu-group">Dados COLIH</li>
      <li class="menu-item" onclick="openTab('colih-medicos', this)"><i class="fas fa-handshake"></i> Cooperadores</li>
      <li class="menu-item" onclick="openTab('colih-membros', this)"><i class="fas fa-users"></i> Membros Regionais</li>
      <li class="menu-item" onclick="openTab('contatos', this)"><i class="fas fa-phone"></i> Histórico Contatos</li>
    </ul>

    <!-- MODULE: CONFIG -->
    <ul class="sidebar-menu" id="sidebar-config" style="display:none;">
      <li class="menu-group">Configurações</li>
      <li class="menu-item" onclick="openTab('config-hlc', this)"><i class="fas fa-book-medical"></i> Dicionário HLC-9</li>
      <li class="menu-item" onclick="openTab('config-cnes', this)"><i class="fas fa-map-marked-alt"></i> Escopo CNES</li>
      <li class="menu-item" onclick="openTab('config-apoio', this)"><i class="fas fa-cogs"></i> Termos de Apoio</li>
    </ul>
  </aside>

  <!-- ─── CONTEÚDO PRINCIPAL ────────────────────────────────────── -->
  <main class="main-content" style="flex: 1; overflow-y: auto;">
"""

# 1. We inject Top Navbar buttons into <header>
top_modules_html = """
    <!-- Top Modules Navbar -->
    <div class="top-modules" style="display:flex; gap:20px; align-items:center; margin-left: 30px;">
      <button class="module-btn active" onclick="switchModule('sus', this)" style="background:transparent; border:none; color:#fff; font-size:16px; cursor:pointer; padding:10px; border-bottom: 2px solid #3b82f6;"><i class="fas fa-hospital"></i> Dados do SUS</button>
      <button class="module-btn" onclick="switchModule('colih', this)" style="background:transparent; border:none; color:#94a3b8; font-size:16px; cursor:pointer; padding:10px; border-bottom: 2px solid transparent;"><i class="fas fa-users"></i> Dados COLIH</button>
      <button class="module-btn" onclick="switchModule('config', this)" style="background:transparent; border:none; color:#94a3b8; font-size:16px; cursor:pointer; padding:10px; border-bottom: 2px solid transparent;"><i class="fas fa-cog"></i> Configurações</button>
    </div>
"""

# Let's insert `top_modules_html` inside <header class="app-header"> right after `<div class="header-inner">`
# Wait, actually, let's put it next to the brand-text
text = text.replace('</div>\n    </div>\n\n    <div class="header-meta" id="header-meta">', '</div>\n    </div>\n' + top_modules_html + '\n    <div class="header-meta" id="header-meta">')

# 2. Replace <nav class="tab-nav"> with sidebar_html
nav_start = text.find('<!-- ═══════════════════════════════════════════════════════ NAV TABS -->')
nav_end = text.find('</nav>') + 6

if nav_start != -1 and nav_end > nav_start:
    text = text[:nav_start] + sidebar_html + text[nav_end:]

# 3. Add closing </div> for the flex container right before the modals
modal_start = text.find('<!-- ═══════════════════════════════════════════════════════ MODAIS -->')
if modal_start != -1:
    text = text[:modal_start] + '  </main>\n</div>\n\n' + text[modal_start:]

# 4. Modify 'configuracoes' tab. The current index.html probably still has `id="tab-configuracoes"`
# Wait, let me check if it has `tab-configuracoes`. My previous script ran locally but not on index.html, no wait, the fallback failed so it wasn't modified!
config_match = re.search(r'<section class="tab-panel" id="tab-configuracoes">(.*?)</section>', text, re.DOTALL)
if config_match:
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
    <div style="background:var(--bg-card); border-radius:12px; padding:20px; border:1px solid var(--border-color); margin-top:20px; max-width:600px;">
        <div style="margin-bottom:15px;">
            <label style="display:block; font-weight:700; color:var(--text-secondary); margin-bottom:5px;">Estado (UF)</label>
            <select id="config-uf" style="width:100%; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-dark); color:#fff; font-size:16px;">
                <option value="BA">BA - Bahia</option>
                <option value="SP">SP - São Paulo</option>
                <option value="RJ">RJ - Rio de Janeiro</option>
                <option value="MG">MG - Minas Gerais</option>
                <option value="RS">RS - Rio Grande do Sul</option>
                <option value="PR">PR - Paraná</option>
                <option value="SC">SC - Santa Catarina</option>
                <option value="PE">PE - Pernambuco</option>
                <option value="CE">CE - Ceará</option>
                <option value="GO">GO - Goiás</option>
                <option value="DF">DF - Distrito Federal</option>
                <option value="ES">ES - Espírito Santo</option>
                <option value="MT">MT - Mato Grosso</option>
                <option value="MS">MS - Mato Grosso do Sul</option>
                <option value="AM">AM - Amazonas</option>
                <option value="PA">PA - Pará</option>
                <option value="PB">PB - Paraíba</option>
                <option value="RN">RN - Rio Grande do Norte</option>
                <option value="AL">AL - Alagoas</option>
                <option value="SE">SE - Sergipe</option>
                <option value="PI">PI - Piauí</option>
                <option value="MA">MA - Maranhão</option>
                <option value="TO">TO - Tocantins</option>
                <option value="RO">RO - Rondônia</option>
                <option value="RR">RR - Roraima</option>
                <option value="AC">AC - Acre</option>
                <option value="AP">AP - Amapá</option>
            </select>
        </div>
        <div style="margin-bottom:15px;">
            <label style="display:block; font-weight:700; color:var(--text-secondary); margin-bottom:5px;">Códigos IBGE (Separados por vírgula)</label>
            <input type="text" id="config-municipios" placeholder="Ex: 292740, 291920 (Deixe em branco para o estado todo)" style="width:100%; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-dark); color:#fff; font-size:14px;">
            <p style="font-size:12px; color:var(--text-muted); margin-top:5px;">Atenção: Apenas os hospitais e médicos destes municípios serão lidos e importados na próxima sincronização do CNES.</p>
        </div>
        <div style="text-align:right;">
            <button class="btn-primary" onclick="salvarConfigEscopo()">💾 Salvar Escopo</button>
        </div>
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
print("index.html structure successfully updated.")
