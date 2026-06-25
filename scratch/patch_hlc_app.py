import re

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update renderHlcDict to add "Editar" button
old_render = r'''function renderHlcDict() {
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
}'''

new_render = '''let hlcEditKey = null;

function renderHlcDict() {
    const tbody = document.querySelector('#table-hlc-dict tbody');
    if(!tbody) return;
    
    // Sort keys alphabetically
    const sortedEntries = Object.entries(hlcDict).sort((a, b) => a[0].localeCompare(b[0]));
    
    tbody.innerHTML = sortedEntries.map(([k,v]) => `
        <tr>
            <td>${k}</td>
            <td><strong>${v}</strong></td>
            <td class="td-actions" style="display:flex; gap:6px;">
                <button class="btn-secondary btn-sm" onclick="editarHlcDict('${k}')">✏️ Editar</button>
                <button class="btn-secondary btn-sm" onclick="removerHlcDict('${k}')">Excluir</button>
            </td>
        </tr>
    `).join('');
}'''

text = text.replace(old_render, new_render)

# 2. Add editarHlcDict and update adicionarHlcDict
old_add = r'''function adicionarHlcDict() {
    const k = document.getElementById('hlc-key-input').value.trim();
    const v = document.getElementById('hlc-val-input').value.trim();
    if(!k || !v) return;
    hlcDict[k] = v;
    document.getElementById('hlc-key-input').value = '';
    document.getElementById('hlc-val-input').value = '';
    renderHlcDict();
}'''

new_add = '''function editarHlcDict(k) {
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
    
    // Força Maiúsculas e padronização para o Dicionário
    const k = kInput.toUpperCase();
    const v = vInput; // Mantém a capitalização da classificação (ex: Cirurgia Geral)
    
    hlcDict[k] = v;
    
    // Reset form
    hlcEditKey = null;
    document.getElementById('hlc-key-input').value = '';
    document.getElementById('hlc-val-input').value = '';
    
    const btn = document.getElementById('btn-adicionar-hlc');
    if(btn) {
        btn.innerText = 'Adicionar';
        btn.style.backgroundColor = '';
    }
    
    renderHlcDict();
}'''

text = text.replace(old_add, new_add)

# 3. Add populate Datalist logic to the bottom of the file
datalist_logic = '''
// ─── CARREGAMENTO DE ESPECIALIDADES CNES NO DATALIST ───
async function popularDatalistCNES() {
    try {
        const res = await fetchAPI('/cnes/especialidades');
        const datalist = document.getElementById('cnes-especialidades-list');
        if (datalist && res && Array.isArray(res)) {
            datalist.innerHTML = res.map(esp => `<option value="${esp}">`).join('');
        }
    } catch(e) {
        console.error("Erro ao carregar especialidades CNES:", e);
    }
}
popularDatalistCNES();
'''

text = text + datalist_logic

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('app.js patched for HLC dict UI features.')
