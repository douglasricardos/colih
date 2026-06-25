import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace FontAwesome with Lucide
text = re.sub(r'<link rel="stylesheet" href="https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/.*?">', '<script src="https://unpkg.com/lucide@latest"></script>', text)

# 2. Icon Replacements
icon_map = {
    'fa-chevron-down': 'chevron-down',
    'fa-chevron-right': 'chevron-right',
    'fa-hospital': 'building-2',
    'fa-user-md': 'stethoscope',
    'fa-clipboard-list': 'list-todo',
    'fa-chart-line': 'bar-chart-3',
    'fa-handshake': 'users',
    'fa-users': 'users',
    'fa-phone': 'phone',
    'fa-book-medical': 'book',
    'fa-map-marked-alt': 'map-pin',
    'fa-cogs': 'settings',
    'fa-database': 'database',
    'fa-cog': 'settings'
}

for fa_icon, lucide_icon in icon_map.items():
    text = re.sub(fr'<i class="fas {fa_icon}"(.*?)></i>', fr'<i data-lucide="{lucide_icon}"\1></i>', text)

# Remove FontAwesome classes from remaining icons just in case
text = re.sub(r'<i class="fas fa-[^"]+"(.*?)></i>', r'<i data-lucide="circle"\1></i>', text)

# 3. Remove panel-headers
text = re.sub(r'<div class="panel-header">.*?</div>', '', text, flags=re.DOTALL)

# 4. Remove topbar
text = re.sub(r'<div class="topbar".*?>\s*<div class="header-meta".*?</div>\s*</div>\s*</div>', '', text, flags=re.DOTALL)
# Try more aggressive removal of topbar if regex failed
if '<div class="topbar"' in text:
    topbar_start = text.find('<div class="topbar"')
    topbar_end = text.find('</div>\n    </div>', topbar_start) + 16
    if topbar_start != -1:
        text = text[:topbar_start] + text[topbar_end:]

# 5. Insert Badges Footer into Sidebar
sidebar_footer = '''
    <!-- SIDEBAR STATUS FOOTER -->
    <div style="margin-top: auto; padding: 15px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; gap: 10px; font-size: 11px;">
      
      <!-- STATUS CNES -->
      <div id="syncStatusBadge" onclick="document.getElementById('syncStatusModal').style.display='flex'" style="cursor: pointer; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 8px 10px; display: flex; align-items: center; justify-content: space-between;">
        <div style="display:flex; flex-direction:column; gap:2px;">
           <span style="color: #94a3b8; font-weight: bold; font-size: 9px; letter-spacing: 0.5px;">FONTE CNES</span>
           <span id="syncStatusText" style="color: #ffaa00; font-weight: bold;">Verificando...</span>
        </div>
        <div class="status-dot" id="syncStatusDot" style="width: 8px; height: 8px; border-radius: 50%; background: #ffaa00; box-shadow: 0 0 5px #ffaa00;"></div>
      </div>
      
      <!-- ATUALIZAÇÃO -->
      <div style="display:flex; justify-content:space-between; align-items:center; padding: 4px 5px;">
         <span style="color: #64748b; display:flex; align-items:center; gap:5px;"><i data-lucide="calendar" style="width:12px; height:12px;"></i> Atualizado</span>
         <span id="data-atualizacao" style="color: #e2e8f0; font-weight:600;">--</span>
      </div>

      <!-- COMPETÊNCIA -->
      <div style="display:flex; justify-content:space-between; align-items:center; padding: 4px 5px;">
         <span style="color: #64748b; display:flex; align-items:center; gap:5px;"><i data-lucide="clock" style="width:12px; height:12px;"></i> Competência</span>
         <span id="competencia-valor" style="color: #e2e8f0; font-weight:600;">--</span>
      </div>

      <!-- MÉDICOS -->
      <div style="display:flex; justify-content:space-between; align-items:center; padding: 4px 5px;">
         <span style="color: #64748b; display:flex; align-items:center; gap:5px;"><i data-lucide="stethoscope" style="width:12px; height:12px;"></i> Médicos</span>
         <span id="total-medicos-valor" style="color: #38bdf8; font-weight:bold;">--</span>
      </div>
    </div>
  </aside>
'''

text = re.sub(r'\s*</aside>', sidebar_footer, text)

# Write changes
with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('index.html UI updated.')
