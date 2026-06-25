import re

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update renderColihMedicos to update the result count
old_render_medicos_start = r'''function renderColihMedicos() {
    const term = (document.getElementById('busca-colih-medico')?.value || '').toLowerCase();
    const espFiltro = (document.getElementById('filtro-colih-especialidade')?.value || '').toLowerCase();
    const visitaFiltro = (document.getElementById('filtro-colih-visita')?.value || '');
    
    const grid = document.getElementById('colih-medicos-grid');
    if (!grid) return;'''

new_render_medicos_start = '''function renderColihMedicos() {
    const term = (document.getElementById('busca-colih-medico')?.value || '').toLowerCase();
    const espFiltro = (document.getElementById('filtro-colih-especialidade')?.value || '').toLowerCase();
    const visitaFiltro = (document.getElementById('filtro-colih-visita')?.value || '');
    
    const grid = document.getElementById('colih-medicos-grid');
    if (!grid) return;'''

# Actually, I'll just replace the innerHTML assignment to also update the count
old_grid_inner = r'''grid.innerHTML = filtered.map(m => {
        const borderCol = m._isDefasado ? '#ef4444' : '#10b981';'''

new_grid_inner = '''const countEl = document.getElementById('colih-medicos-count');
    if(countEl) countEl.innerText = `${filtered.length} médico(s) encontrado(s)`;
    
    grid.innerHTML = filtered.map(m => {
        const borderCol = m._isDefasado ? '#ef4444' : '#10b981';'''
text = text.replace(old_grid_inner, new_grid_inner)

# 2. Add HLC Custom Dropdown Logic and New Card Renderer
old_hlc_logic = re.search(r'let hlcEditKey = null;.*?function adicionarHlcDict\(\) \{.*?\}\n', text, re.DOTALL).group(0)

new_hlc_logic = '''
// ─── CUSTOM DROPDOWNS LOGIC ───
let cnesEspecialidadesFull = [];
const hlcAlvos = [
    "Anestesiologia", "Cirurgia bucomaxilofacial", "Cirurgia cardíaca", "Coloproctologia",
    "Cirurgia de transplante", "Cirurgia de trauma", "Cirurgia geral", "Ortopedia",
    "Cirurgia torácica", "Cirurgia vascular", "Clínica médica", "Medicina intensiva",
    "Gastroenterologia", "Ginecologia", "Ginecologia oncológica", "Hematologia",
    "Medicina de emergência", "Medicina hospitalar", "Nefrologia", "Neonatologia",
    "Neurocirurgia", "Obstetrícia", "Oncologia clínica", "Otorrinolaringologia",
    "Pneumologia", "Radiologia intervencionista", "Tratamento de queimados", "Urologia"
];

async function popularDatalistCNES() {
    try {
        const res = await fetchAPI('/cnes/especialidades');
        if (res && Array.isArray(res)) {
            cnesEspecialidadesFull = res;
        }
    } catch(e) { console.error(e); }
}

function renderDropdownList(listId, inputId, data, onSelect) {
    const box = document.getElementById(listId);
    const input = document.getElementById(inputId);
    const term = input.value.toLowerCase();
    
    const filtered = data.filter(d => d.toLowerCase().includes(term));
    if (filtered.length === 0) {
        box.innerHTML = `<div style="padding:10px; font-size:12px; color:var(--text-muted);">Nenhum resultado</div>`;
    } else {
        box.innerHTML = filtered.map(d => `<div class="dropdown-list-item" onclick="${onSelect}('${d}')">${d}</div>`).join('');
    }
    box.style.display = 'block';
}

function abrirDropdownCNES() { renderDropdownList('cnes-list-box', 'hlc-key-input', cnesEspecialidadesFull, 'selecionarCNES'); }
function filtrarDropdownCNES() { renderDropdownList('cnes-list-box', 'hlc-key-input', cnesEspecialidadesFull, 'selecionarCNES'); }
function selecionarCNES(val) {
    document.getElementById('hlc-key-input').value = val;
    document.getElementById('cnes-list-box').style.display = 'none';
}

function abrirDropdownHLC() { renderDropdownList('hlc-list-box', 'hlc-val-input', hlcAlvos, 'selecionarHLC'); }
function filtrarDropdownHLC() { renderDropdownList('hlc-list-box', 'hlc-val-input', hlcAlvos, 'selecionarHLC'); }
function selecionarHLC(val) {
    document.getElementById('hlc-val-input').value = val;
    document.getElementById('hlc-list-box').style.display = 'none';
}

// Close dropdowns on outside click
document.addEventListener('click', function(e) {
    if(!e.target.closest('#dropdown-cnes')) {
        const b = document.getElementById('cnes-list-box');
        if(b) b.style.display = 'none';
    }
    if(!e.target.closest('#dropdown-hlc')) {
        const b = document.getElementById('hlc-list-box');
        if(b) b.style.display = 'none';
    }
});


// ─── HLC DICT RENDERING & EDITING (AGRUPADO) ───

let hlcEditKey = null;

function renderHlcDict() {
    const container = document.getElementById('hlc-cards-container');
    if(!container) return;
    
    // Agrupar por Alvo HLC-9
    const groups = {};
    Object.entries(hlcDict).forEach(([k, v]) => {
        if(!groups[v]) groups[v] = [];
        groups[v].push(k);
    });
    
    // Sort groups alphabetically
    const sortedTargets = Object.keys(groups).sort((a,b) => a.localeCompare(b));
    
    container.innerHTML = sortedTargets.map(target => {
        const children = groups[target].sort();
        const childrenHtml = children.map(c => `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; border-bottom:1px solid var(--border-color); font-size:13px; color:var(--text-secondary); background:var(--bg-input); border-radius:4px; margin-bottom:4px;">
                <span>↳ ${c}</span>
                <div style="display:flex; gap:6px;">
                    <button class="btn-secondary btn-sm" onclick="editarHlcDict('${c}')" style="padding:2px 6px; font-size:11px;">✏️</button>
                    <button class="btn-secondary btn-sm" onclick="removerHlcDict('${c}')" style="padding:2px 6px; font-size:11px; color:#ef4444;">❌</button>
                </div>
            </div>
        `).join('');
        
        return `
        <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:8px; padding:16px;">
            <div style="font-weight:700; font-size:15px; color:var(--text-primary); margin-bottom:12px; display:flex; align-items:center; gap:8px;">
                🩺 ${target}
            </div>
            <div style="padding-left:12px;">
                ${childrenHtml}
            </div>
        </div>
        `;
    }).join('');
}

function editarHlcDict(k) {
    if (!hlcDict[k]) return;
    hlcEditKey = k;
    document.getElementById('hlc-key-input').value = k;
    document.getElementById('hlc-val-input').value = hlcDict[k];
    
    const btn = document.getElementById('btn-adicionar-hlc');
    if(btn) {
        btn.innerText = 'Salvar Edição';
        btn.style.backgroundColor = '#f59e0b';
    }
}

function adicionarHlcDict() {
    const kInput = document.getElementById('hlc-key-input').value.trim();
    const vInput = document.getElementById('hlc-val-input').value.trim();
    if(!kInput || !vInput) {
        alert("Preencha a especialidade CNES e a classificação HLC-9!");
        return;
    }
    
    // Se está editando uma chave e mudou o nome da chave, remove a antiga
    if(hlcEditKey && hlcEditKey !== kInput) {
        delete hlcDict[hlcEditKey];
    }
    
    const k = kInput.toUpperCase();
    const v = vInput;
    
    hlcDict[k] = v;
    
    hlcEditKey = null;
    document.getElementById('hlc-key-input').value = '';
    document.getElementById('hlc-val-input').value = '';
    
    const btn = document.getElementById('btn-adicionar-hlc');
    if(btn) {
        btn.innerText = 'Adicionar';
        btn.style.backgroundColor = '';
    }
    
    renderHlcDict();
}
'''
text = text.replace(old_hlc_logic, new_hlc_logic)

# Strip out the old datalist population function since we redefined it
text = re.sub(r'// ─── CARREGAMENTO DE ESPECIALIDADES CNES NO DATALIST ───.*?popularDatalistCNES\(\);\n', '', text, flags=re.DOTALL)

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('app.js successfully updated with logic for custom dropdowns and card layout.')
