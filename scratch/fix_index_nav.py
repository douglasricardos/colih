import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the current sidebar and topbar
new_sidebar_and_topbar = """
  <!-- ─── SIDEBAR ESQUERDA (GLPI Style) ───────────────────────── -->
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <img src="logo-colih-portal.png" alt="COLIH" style="max-height: 40px; margin-bottom: 5px;"><br>
      COLIH Salvador
    </div>
    
    <!-- MODULE: SUS -->
    <ul class="sidebar-menu" id="sidebar-sus">
      <li class="menu-group">Dados SUS</li>
      <li class="menu-item active" onclick="openTab('hospitais', this)"><i class="fas fa-hospital"></i> Instituições</li>
      <li class="menu-item" onclick="openTab('profissionais', this)"><i class="fas fa-user-md"></i> Profissionais</li>
      <li class="menu-item" onclick="openTab('stats', this)"><i class="fas fa-chart-line"></i> Captação / HLC</li>
      <li class="menu-item" onclick="openTab('pipeline', this)"><i class="fas fa-clipboard-list"></i> Prospectos</li>
      <li class="menu-item" onclick="openTab('contatos', this)"><i class="fas fa-phone"></i> Histórico Contatos</li>
    </ul>

    <!-- MODULE: COLIH -->
    <ul class="sidebar-menu" id="sidebar-colih" style="display:none;">
      <li class="menu-group">Dados COLIH</li>
      <li class="menu-item" onclick="openTab('colih-medicos', this)"><i class="fas fa-handshake"></i> Cooperadores</li>
      <li class="menu-item" onclick="openTab('colih-membros', this)"><i class="fas fa-users"></i> Membros Regionais</li>
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
  <main class="main-content">
    <div class="topbar">
      <div class="top-modules" style="display:flex; gap:10px;">
        <button class="module-btn active" onclick="switchModule('sus', this)"><i class="fas fa-hospital"></i> Dados SUS</button>
        <button class="module-btn" onclick="switchModule('colih', this)"><i class="fas fa-users"></i> Dados COLIH</button>
        <button class="module-btn" onclick="switchModule('config', this)"><i class="fas fa-cog"></i> Configurações</button>
      </div>
      <!-- Sync Button -->
      <div class="sync-status" id="btnOpenSyncModal" onclick="document.getElementById('syncStatusModal').style.display='flex'">
        <i class="fas fa-database"></i> Status: <span id="lblDataSync">Carregando...</span>
      </div>
    </div>
"""

pattern = r'<!-- ─── SIDEBAR ESQUERDA \(GLPI Style\) ───────────────────────── -->.*?</aside>\s*<!-- ─── CONTEÚDO PRINCIPAL ────────────────────────────────────── -->\s*<main class="main-content">\s*<div class="topbar">.*?</div>\s*</div>'

if re.search(pattern, text, re.DOTALL):
    text = re.sub(pattern, new_sidebar_and_topbar.strip(), text, flags=re.DOTALL)
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('index.html updated successfully with Top Modules + Sidebar')
else:
    print('Pattern not found in index.html! Trying fallback.')
    # Fallback to manual replace
    pattern_start = "<!-- ─── SIDEBAR ESQUERDA (GLPI Style) ───────────────────────── -->"
    pattern_end = '<div class="sync-status" id="btnOpenSyncModal" onclick="document.getElementById(\'syncStatusModal\').style.display=\'flex\'">\n        <i class="fas fa-database"></i> Status: <span id="lblDataSync">Carregando...</span>\n      </div>\n    </div>'
    
    start_idx = text.find(pattern_start)
    end_idx = text.find(pattern_end) + len(pattern_end)
    
    if start_idx != -1 and end_idx > start_idx:
        text = text[:start_idx] + new_sidebar_and_topbar.strip() + text[end_idx:]
        with open('frontend/index.html', 'w', encoding='utf-8') as f:
            f.write(text)
        print('Fallback replacement successful!')
    else:
        print('Fallback failed too.')
