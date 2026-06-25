with open('frontend/app.js', 'a', encoding='utf-8') as f:
    f.write("""

// ─── DASHBOARD GAMIFICAÇÃO HLC ────────────────────────────────────────────────
async function renderDashboardGamificacao() {
    try {
        // Fetch necessary data
        const [dictRes, colihMed, susMed, hospRes] = await Promise.all([
            fetchAPI('/config/hlc-dict').catch(() => ({})),
            fetchAPI('/colih/medicos').catch(() => []),
            fetchAPI('/medicos?limit=1000').catch(() => ({ medicos: [] })), // try to get as many as possible or rely on backend
            fetchAPI('/hospitais?limit=1000').catch(() => ({ hospitais: [] }))
        ]);
        
        const hlcDict = dictRes || {};
        const colihDocs = colihMed || [];
        
        // Extract unique HLC target specialties
        const targetSpecialties = [...new Set(Object.values(hlcDict))].filter(Boolean);
        if (targetSpecialties.length === 0) return; // No config yet
        
        // Find covered specialties in COLIH doctors
        const covered = new Set();
        colihDocs.forEach(d => {
            const esp1 = (d.especialidade_1_colih || '').toUpperCase();
            const esp2 = (d.especialidade_2_colih || '').toUpperCase();
            if (targetSpecialties.includes(esp1)) covered.add(esp1);
            if (targetSpecialties.includes(esp2)) covered.add(esp2);
        });
        
        const coveragePct = Math.round((covered.size / targetSpecialties.length) * 100);
        document.getElementById('dash-cobertura-pct').innerText = `${coveragePct}%`;
        document.getElementById('dash-total-coop').innerText = colihDocs.length;
        
        const missing = targetSpecialties.filter(t => !covered.has(t));
        document.getElementById('dash-red-flags').innerText = missing.length;
        
        // Render Red Flags list
        const redListEl = document.getElementById('dash-red-list');
        redListEl.innerHTML = missing.map(m => `
            <span style="background: rgba(239, 68, 68, 0.1); color: #ef4444; padding: 4px 12px; border-radius: 16px; font-size: 13px; font-weight: 700; border: 1px solid #ef4444;">
                ${m}
            </span>
        `).join('');
        
        // Find High Complexity Hospitals that might have these missing specialties
        // Actually, we look for hospitals with Alta Complexidade
        const hospitals = hospRes.hospitais || [];
        const highComp = hospitals.filter(h => h.alta_complexidade === 'Sim').slice(0, 10); // top 10
        
        const targetsEl = document.getElementById('dash-targets-list');
        targetsEl.innerHTML = highComp.map(h => `
            <div style="background:var(--bg-card); padding:16px; border-radius:8px; border:1px solid var(--border-color); border-left:4px solid #f59e0b;">
                <div style="font-weight:700; font-size:14px; margin-bottom:4px;">${h.nome_fantasia}</div>
                <div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">${h.municipio} - Alta Complexidade</div>
                <button class="btn-secondary btn-sm" onclick="abrirHospitalDoDashboard('${h.cnes}')">Ver Detalhes</button>
            </div>
        `).join('');
        
    } catch(e) { console.error('Erro ao renderizar gamificação', e); }
}

window.abrirHospitalDoDashboard = function(cnes) {
    const btn = document.querySelector('#tab-btn-hospitais');
    if(btn) btn.click();
    setTimeout(() => abrirDetalheHospital(cnes), 100);
}

// Hook into openTab to render dashboard
const origOpenTab2 = window.openTab;
window.openTab = function(tabId, btnElement) {
    if (tabId === 'stats') {
        renderDashboardGamificacao();
    }
    if (origOpenTab2) {
        origOpenTab2(tabId, btnElement);
    }
}
""")
print('Gamification dashboard logic added.')
