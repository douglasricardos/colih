with open('frontend/app.js', 'a', encoding='utf-8') as f:
    f.write("""

// ─── CONFIG: ESCOPO GEOGRAFICO ────────────────────────────────────────────────
async function loadConfigEscopo() {
    try {
        const res = await fetchAPI('/config/escopo');
        if (res) {
            if (res.uf) {
                const ufSelect = document.getElementById('config-uf');
                if(ufSelect) ufSelect.value = res.uf;
            }
            if (res.municipios_especificos) {
                const munInput = document.getElementById('config-municipios');
                if(munInput) munInput.value = res.municipios_especificos.join(', ');
            }
        }
    } catch(e) { console.error('Erro load escopo', e); }
}

async function salvarConfigEscopo() {
    const uf = document.getElementById('config-uf').value;
    const munRaw = document.getElementById('config-municipios').value;
    const municipios = munRaw.split(',').map(m => m.trim()).filter(Boolean);
    
    try {
        await fetchAPI('/config/escopo', {
            method: 'POST',
            body: JSON.stringify({ uf: uf, municipios_especificos: municipios })
        });
        alert('Escopo salvo com sucesso! As alterações farão efeito na próxima sincronização do CNES.');
    } catch(e) { alert('Erro ao salvar escopo'); }
}

// Ensure the new config loads
setTimeout(() => { loadConfigEscopo(); }, 1500);

// Override openTab to handle sidebar active states
const origOpenTab3 = window.openTab;
window.openTab = function(tabId, btnElement) {
    if (origOpenTab3) {
        origOpenTab3(tabId, btnElement);
    }
    
    // Update sidebar active class
    const items = document.querySelectorAll('.sidebar .menu-item');
    items.forEach(item => item.classList.remove('active'));
    if (btnElement) {
        btnElement.classList.add('active');
    }
    
    // Auto-load config if config tabs are opened
    if (tabId === 'config-cnes') {
        loadConfigEscopo();
    }
}
""")
print('Added Escopo UI logic to app.js')
