import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove Top Modules from header
text = re.sub(r'<!-- Top Modules Navbar -->.*?</div>\s*(?=<div class="header-meta" id="header-meta">)', '', text, flags=re.DOTALL)

# 2. Fix the Sidebar to have collapsible groups
new_sidebar = """
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <img src="logo-colih-portal.png" alt="COLIH" style="max-height: 40px; margin-bottom: 5px;"><br>
      COLIH Salvador
    </div>
    
    <!-- MODULE: SUS -->
    <ul class="sidebar-menu" id="sidebar-sus">
      <li class="menu-group" onclick="toggleGroup('sus')" style="cursor:pointer; display:flex; justify-content:space-between; align-items:center;">
        Dados do SUS <i class="fas fa-chevron-down" id="icon-sus"></i>
      </li>
      <div id="group-sus">
        <li class="menu-item active" onclick="openTab('hospitais', this)"><i class="fas fa-hospital"></i> Instituições</li>
        <li class="menu-item" onclick="openTab('medicos', this)"><i class="fas fa-user-md"></i> Profissionais</li>
        <li class="menu-item" onclick="openTab('pipeline', this)"><i class="fas fa-clipboard-list"></i> Prospectos <span class="tab-badge" id="pipeline-count">0</span></li>
        <li class="menu-item" onclick="openTab('stats', this)"><i class="fas fa-chart-line"></i> Captação / HLC</li>
      </div>
    </ul>

    <!-- MODULE: COLIH -->
    <ul class="sidebar-menu" id="sidebar-colih">
      <li class="menu-group" onclick="toggleGroup('colih')" style="cursor:pointer; display:flex; justify-content:space-between; align-items:center;">
        Dados COLIH <i class="fas fa-chevron-down" id="icon-colih"></i>
      </li>
      <div id="group-colih">
        <li class="menu-item" onclick="openTab('colih-medicos', this)"><i class="fas fa-handshake"></i> Cooperadores</li>
        <li class="menu-item" onclick="openTab('colih-membros', this)"><i class="fas fa-users"></i> Membros Regionais</li>
        <li class="menu-item" onclick="openTab('contatos', this)"><i class="fas fa-phone"></i> Histórico Contatos</li>
      </div>
    </ul>

    <!-- MODULE: CONFIG -->
    <ul class="sidebar-menu" id="sidebar-config">
      <li class="menu-group" onclick="toggleGroup('config')" style="cursor:pointer; display:flex; justify-content:space-between; align-items:center;">
        Configurações <i class="fas fa-chevron-right" id="icon-config"></i>
      </li>
      <div id="group-config" style="display:none;">
        <li class="menu-item" onclick="openTab('config-hlc', this)"><i class="fas fa-book-medical"></i> Dicionário HLC-9</li>
        <li class="menu-item" onclick="openTab('config-cnes', this)"><i class="fas fa-map-marked-alt"></i> Escopo CNES</li>
        <li class="menu-item" onclick="openTab('config-apoio', this)"><i class="fas fa-cogs"></i> Termos de Apoio</li>
      </div>
    </ul>
  </aside>
"""

# Replace the old sidebar with the new one
pattern_sidebar = r'<aside class="sidebar" id="sidebar">.*?</aside>'
text = re.sub(pattern_sidebar, new_sidebar.strip(), text, flags=re.DOTALL)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('index.html fixed with collapsible sidebar and no top modules.')
