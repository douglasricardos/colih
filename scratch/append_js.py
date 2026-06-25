with open('frontend/app.js', 'a', encoding='utf-8') as f:
    f.write('''

// ─── COLIH Logic ──────────────────────────────────────────────────────────────
let colihMedicosCache = [];
let colihMembrosCache = [];

async function loadColihData() {
  try {
    const medRes = await fetchAPI('/colih/medicos');
    const memRes = await fetchAPI('/colih/membros');
    colihMedicosCache = medRes || [];
    colihMembrosCache = memRes || [];
    
    // Alerta de coordenadas ausentes
    const missingCoords = colihMembrosCache.some(m => !m.lat || !m.lon);
    const alertEl = document.getElementById('alerta-coords-membros');
    if (alertEl) {
        alertEl.style.display = missingCoords ? 'block' : 'none';
    }
  } catch (e) {
    console.error('Erro ao carregar COLIH', e);
  }
}

function renderColihMedicos() {
    const term = (document.getElementById('busca-colih-medico')?.value || '').toLowerCase();
    const grid = document.getElementById('colih-medicos-grid');
    if (!grid) return;
    
    const filtered = colihMedicosCache.filter(m => 
        (m.nome || '').toLowerCase().includes(term) ||
        (m.especialidade_1_colih || '').toLowerCase().includes(term)
    );
    
    grid.innerHTML = filtered.map(m => `
        <div class="medico-card" style="border-left: 4px solid #10b981; padding: 16px; background: var(--bg-card); border-radius: 8px; border-right: 1px solid var(--border-color); border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="font-weight:700; font-size:16px; color:var(--text-primary); margin-bottom:4px;">${m.nome}</div>
            <div style="font-size:13px; color:var(--text-muted); margin-bottom:8px;">${m.especialidade_1_colih || ''} ${m.especialidade_2_colih ? ' / ' + m.especialidade_2_colih : ''}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Colaboração:</strong> ${m.colaboracao || '—'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Membro Resp:</strong> ${m.membro_resp || '—'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Celular:</strong> ${m.celular || '—'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Atende SUS:</strong> ${m.atende_sus || '—'}</div>
            <div style="font-size:12px; color:var(--text-muted); margin-top:8px;"><em>Última visita: ${m.ultima_visita || '—'}</em></div>
        </div>
    `).join('');
}

function renderColihMembros() {
    const term = (document.getElementById('busca-colih-membro')?.value || '').toLowerCase();
    const grid = document.getElementById('colih-membros-grid');
    if (!grid) return;
    
    const filtered = colihMembrosCache.filter(m => 
        (m.nome || '').toLowerCase().includes(term) ||
        (m.funcao || '').toLowerCase().includes(term)
    );
    
    grid.innerHTML = filtered.map(m => {
        const hasCoords = m.lat && m.lon;
        const borderStyle = hasCoords ? 'border-left: 4px solid #3b82f6;' : 'border-left: 4px solid #ef4444; background: rgba(239,68,68,0.05);';
        return `
        <div class="medico-card" style="${borderStyle} padding: 16px; border-radius: 8px; border-right: 1px solid var(--border-color); border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="font-weight:700; font-size:16px; color:var(--text-primary); margin-bottom:4px;">${m.nome}</div>
            <div style="font-size:13px; color:var(--text-muted); margin-bottom:8px;">${m.funcao || '—'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Telefone:</strong> ${m.telefone || '—'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Hospital:</strong> ${m.hospital || '—'}</div>
            <div style="font-size:12px; margin-bottom:4px;">
                <strong>Geolocalização:</strong> 
                ${hasCoords ? '<span style="color:#10b981;">Validada</span>' : '<span style="color:#ef4444; font-weight:bold;">Pendente</span>'}
            </div>
            ${!hasCoords ? `<div style="font-size:11px; color:#ef4444; margin-top:8px;">Falta coordenadas no CSV.</div>` : ''}
        </div>
    `}).join('');
}

// Intercept openTab to render COLIH panels if opened
const originalOpenTab = window.openTab;
window.openTab = function(tabId, btnElement) {
    if (tabId === 'colih-medicos') {
        renderColihMedicos();
    } else if (tabId === 'colih-membros') {
        renderColihMembros();
    }
    if(originalOpenTab) {
        originalOpenTab(tabId, btnElement);
    } else {
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('tab-' + tabId).classList.add('active');
        if(btnElement) btnElement.classList.add('active');
    }
}

setTimeout(() => {
    loadColihData();
}, 2000);

''')
print('App JS logic updated.')
