import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix the dark theme in Config tabs
text = text.replace('background:var(--bg-dark); color:#fff;', 'background:var(--bg-input); color:var(--text-primary);')
text = text.replace('background:var(--bg-dark); color:white;', 'background:var(--bg-input); color:var(--text-primary);')

# 2. Add the topbar with badges
header_meta_html = '''
      <div class="header-meta" id="header-meta" style="display: flex; gap: 15px; align-items: center;">
      <!-- STATUS DO SERVIDOR -->
      <div class="meta-badge" id="syncStatusBadge" onclick="document.getElementById('syncStatusModal').style.display='flex'" style="cursor: pointer; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 5px 10px; display: flex; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <div class="status-dot" id="syncStatusDot" style="width: 10px; height: 10px; border-radius: 50%; background: #ffaa00; margin-right: 8px;"></div>
        <div class="meta-info" style="display: flex; flex-direction: column;">
          <span class="meta-label" style="font-size: 10px; color: #64748b; font-weight: bold;">FONTE CNES (STATUS)</span>
          <span class="meta-value" id="syncStatusText" style="color: #ffaa00; font-size: 12px; font-weight: bold;">Verificando...</span>
        </div>
      </div>
      <!-- ÚLTIMA ATUALIZAÇÃO -->
      <div class="meta-badge" id="data-badge" style="background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 20px; padding: 5px 15px; display: flex; align-items: center; gap: 8px;">
        <span class="meta-icon">🗓️</span>
        <div class="meta-info" style="display: flex; flex-direction: column;">
          <span class="meta-label" style="font-size: 10px; color: #64748b;">ÚLTIMA ATUALIZAÇÃO</span>
          <span class="meta-value" id="data-atualizacao" style="font-size: 12px; font-weight: bold;">Carregando...</span>
        </div>
      </div>
      <!-- COMPETÊNCIA -->
      <div class="meta-badge" id="competencia-badge" style="background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 20px; padding: 5px 15px; display: flex; align-items: center; gap: 8px;">
        <span class="meta-icon">📅</span>
        <div class="meta-info" style="display: flex; flex-direction: column;">
          <span class="meta-label" style="font-size: 10px; color: #64748b;">COMPETÊNCIA</span>
          <span class="meta-value" id="competencia-valor" style="font-size: 12px; font-weight: bold;">—</span>
        </div>
      </div>
      <!-- MÉDICOS NA BASE -->
      <div class="meta-badge highlight" id="total-badge" style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 20px; padding: 5px 15px; display: flex; align-items: center; gap: 8px;">
        <span class="meta-icon">👨‍⚕️</span>
        <div class="meta-info" style="display: flex; flex-direction: column;">
          <span class="meta-label" style="font-size: 10px; color: #3b82f6;">MÉDICOS NA BASE</span>
          <span class="meta-value" id="total-medicos-valor" style="font-size: 12px; font-weight: bold; color: #1d4ed8;">—</span>
        </div>
      </div>
      
      <!-- USER SELECT -->
      <div style="margin-left: 20px;">
          <select id="usuario-select" class="user-select" onchange="setUsuarioAtivo(this.value)" style="padding: 8px 15px; border-radius: 20px; border: 1px solid #e2e8f0; background: #fff; font-weight: bold; color: #334155;">
            <option value="">👤 Selecionar usuário</option>
          </select>
      </div>
    </div>
'''

topbar_html = f'''
    <div class="topbar" style="display:flex; justify-content:flex-end; align-items:center; padding:15px 30px; background-color: #ffffff; border-bottom: 1px solid #e2e8f0; width: 100%; box-sizing: border-box;">
      {header_meta_html}
    </div>
'''

if '<div class="topbar"' not in text:
    text = text.replace('<main class="main-content" style="flex: 1; overflow-y: auto;">', '<main class="main-content" style="flex: 1; overflow-y: auto; background-color: #f8fafc;">\n' + topbar_html)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Restored badges to topbar and fixed dark theme in configs.')
