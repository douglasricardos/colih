import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the old sidebar footer
sidebar_footer = '''
    <!-- SIDEBAR STATUS FOOTER (COMPACT & DYNAMIC) -->
    <div style="margin-top: auto; padding: 15px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 8px;">
      
      <!-- CNES MASTER BUTTON -->
      <button onclick="document.getElementById('cnesDetailsModal').style.display='flex'" style="width:100%; display:flex; align-items:center; justify-content:space-between; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:8px 12px; cursor:pointer; transition:0.2s; color:#94a3b8; font-family:inherit;" onmouseover="this.style.background='rgba(0,0,0,0.4)'" onmouseout="this.style.background='rgba(0,0,0,0.25)'">
        <div style="display:flex; align-items:center; gap:8px;">
          <i data-lucide="database" style="width:14px; height:14px;"></i>
          <span style="font-size:11px; font-weight:700; letter-spacing:0.5px;">CNES</span>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
          <span id="cnesStatusCompact" style="font-size:10px; font-weight:600; color:#ffaa00;">Aguarde...</span>
          <div id="cnesStatusDot" style="width:6px; height:6px; border-radius:50%; background:#ffaa00; box-shadow:0 0 5px #ffaa00;"></div>
        </div>
      </button>

      <!-- COLIH.MED MASTER BUTTON -->
      <button onclick="document.getElementById('colihDetailsModal').style.display='flex'" style="width:100%; display:flex; align-items:center; justify-content:space-between; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:8px 12px; cursor:pointer; transition:0.2s; color:#94a3b8; font-family:inherit;" onmouseover="this.style.background='rgba(0,0,0,0.4)'" onmouseout="this.style.background='rgba(0,0,0,0.25)'">
        <div style="display:flex; align-items:center; gap:8px;">
          <i data-lucide="server" style="width:14px; height:14px;"></i>
          <span style="font-size:11px; font-weight:700; letter-spacing:0.5px;">COLIH.MED</span>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
          <span id="colihStatusCompact" style="font-size:10px; font-weight:600; color:#22c55e;">Online</span>
          <div style="width:6px; height:6px; border-radius:50%; background:#22c55e; box-shadow:0 0 5px #22c55e;"></div>
        </div>
      </button>

    </div>
  </aside>

  <!-- CNES DETAILS MODAL -->
  <div class="modal-overlay" id="cnesDetailsModal" style="z-index:9999;">
    <div class="modal-content" style="max-width: 400px; background:var(--bg-card); color:var(--text-primary); border-radius:12px; padding:24px;">
      <h2 style="font-size:18px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-color); padding-bottom:12px; margin-bottom:16px;">
        <div><i data-lucide="database" style="color:var(--accent-blue); margin-right:8px; vertical-align:middle;"></i> Status CNES (Datasus)</div>
        <button class="btn-icon" onclick="document.getElementById('cnesDetailsModal').style.display='none'"><i data-lucide="x"></i></button>
      </h2>
      <div style="display:flex; flex-direction:column; gap:12px; font-size:14px;">
        <div style="display:flex; justify-content:space-between; padding:10px; background:var(--bg-surface); border-radius:8px;">
           <span style="color:var(--text-secondary);"><i data-lucide="activity" style="width:16px; height:16px; vertical-align:middle; margin-right:4px;"></i> Estado Atual</span>
           <span id="modal-cnes-status" style="font-weight:700; color:#ffaa00;">Sincronizando...</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid var(--border-color);">
           <span style="color:var(--text-secondary);"><i data-lucide="calendar" style="width:16px; height:16px; vertical-align:middle; margin-right:4px;"></i> Atualizado em</span>
           <span id="data-atualizacao" style="font-weight:600;">--</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid var(--border-color);">
           <span style="color:var(--text-secondary);"><i data-lucide="clock" style="width:16px; height:16px; vertical-align:middle; margin-right:4px;"></i> Competência</span>
           <span id="competencia-valor" style="font-weight:600;">--</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid var(--border-color);">
           <span style="color:var(--text-secondary);"><i data-lucide="stethoscope" style="width:16px; height:16px; vertical-align:middle; margin-right:4px;"></i> Médicos na Base</span>
           <span id="total-medicos-valor" style="font-weight:700; color:var(--accent-blue);">--</span>
        </div>
        <div id="syncStatusDetails" style="margin-top:10px;"></div>
      </div>
    </div>
  </div>

  <!-- COLIH DETAILS MODAL -->
  <div class="modal-overlay" id="colihDetailsModal" style="z-index:9999;">
    <div class="modal-content" style="max-width: 400px; background:var(--bg-card); color:var(--text-primary); border-radius:12px; padding:24px;">
      <h2 style="font-size:18px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-color); padding-bottom:12px; margin-bottom:16px;">
        <div><i data-lucide="server" style="color:#22c55e; margin-right:8px; vertical-align:middle;"></i> Banco de Dados COLIH.MED</div>
        <button class="btn-icon" onclick="document.getElementById('colihDetailsModal').style.display='none'"><i data-lucide="x"></i></button>
      </h2>
      <div style="display:flex; flex-direction:column; gap:12px; font-size:14px;">
        <div style="display:flex; justify-content:space-between; padding:10px; background:rgba(34,197,94,0.1); border-radius:8px; border:1px solid rgba(34,197,94,0.2);">
           <span style="color:var(--text-secondary);"><i data-lucide="activity" style="width:16px; height:16px; vertical-align:middle; margin-right:4px;"></i> Conexão Local</span>
           <span style="font-weight:700; color:#22c55e;">Online e Ativa</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid var(--border-color);">
           <span style="color:var(--text-secondary);"><i data-lucide="users" style="width:16px; height:16px; vertical-align:middle; margin-right:4px;"></i> Membros Cadastrados</span>
           <span id="colih-membros-count" style="font-weight:600;">Verificando...</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid var(--border-color);">
           <span style="color:var(--text-secondary);"><i data-lucide="handshake" style="width:16px; height:16px; vertical-align:middle; margin-right:4px;"></i> Cooperadores Ativos</span>
           <span id="colih-coop-count" style="font-weight:600;">Verificando...</span>
        </div>
      </div>
    </div>
  </div>
'''

text = re.sub(r'<!-- SIDEBAR STATUS FOOTER -->.*?</aside>', sidebar_footer, text, flags=re.DOTALL)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Sidebar updated with dynamic footer and modals.')
