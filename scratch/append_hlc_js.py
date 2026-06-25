with open('frontend/app.js', 'a', encoding='utf-8') as f:
    f.write("""

// ─── SYNC & HLC CONFIG LOGIC ──────────────────────────────────────────────────
async function forceSyncUpdateMultiple() {
    const doCnes = document.getElementById('syncCheckCnes')?.checked;
    const doColih = document.getElementById('syncCheckColih')?.checked;
    
    if(!doCnes && !doColih) {
        alert('Selecione ao menos uma fonte para sincronizar.');
        return;
    }
    
    document.getElementById('btnForceSync').disabled = true;
    document.getElementById('btnForceSync').innerHTML = 'Iniciando...';
    
    try {
        if(doCnes) {
            await fetchAPI('/sync', { method: 'POST' });
        }
        if(doColih) {
            await fetchAPI('/colih/sync', { method: 'POST' });
        }
        alert('Sincronização iniciada em segundo plano. Os dados serão atualizados em breve.');
        document.getElementById('syncStatusModal').style.display = 'none';
        carregarStatusSync();
    } catch(e) {
        alert('Erro ao iniciar sincronização.');
    } finally {
        document.getElementById('btnForceSync').disabled = false;
        document.getElementById('btnForceSync').innerHTML = '<i class="fas fa-sync-alt"></i> Forçar Sincronização';
    }
}

let hlcDict = {};
async function loadHlcDict() {
    try {
        const res = await fetchAPI('/config/hlc-dict');
        hlcDict = res || {};
        renderHlcDict();
    } catch(e) { console.error('Erro load HLC dict', e); }
}

function renderHlcDict() {
    const tbody = document.querySelector('#table-hlc-dict tbody');
    if(!tbody) return;
    tbody.innerHTML = Object.entries(hlcDict).map(([k,v]) => `
        <tr>
            <td>${k}</td>
            <td><strong>${v}</strong></td>
            <td class="td-actions">
                <button class="btn-secondary btn-sm" onclick="removerHlcDict('${k}')">Excluir</button>
            </td>
        </tr>
    `).join('');
}

function adicionarHlcDict() {
    const k = document.getElementById('hlc-key-input').value.trim();
    const v = document.getElementById('hlc-val-input').value.trim();
    if(!k || !v) return;
    hlcDict[k] = v;
    document.getElementById('hlc-key-input').value = '';
    document.getElementById('hlc-val-input').value = '';
    renderHlcDict();
}

function removerHlcDict(k) {
    delete hlcDict[k];
    renderHlcDict();
}

async function salvarHlcDict() {
    try {
        await fetchAPI('/config/hlc-dict', { method: 'POST', body: JSON.stringify(hlcDict) });
        alert('Dicionário salvo com sucesso!');
    } catch(e) { alert('Erro ao salvar dicionário'); }
}

setTimeout(() => { loadHlcDict(); }, 1500);
""")
print('Multiple Sync & HLC logic added to app.js')
