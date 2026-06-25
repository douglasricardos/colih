import sys
import re

# PATCH HTML
with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_search = """        <span class="search-icon">🔍</span>
        <input type="text" id="hosp-search-input" placeholder="Nome do hospital, bairro..." class="search-input"
          oninput="debounce(buscarHospitais, 350)()" onkeydown="if(event.key==='Enter') buscarHospitais()" />
        <select id="hosp-sus-filter" class="filter-select" onchange="buscarHospitais()">
          <option value="">Atendimento SUS (Todos)</option>
          <option value="S">Atende SUS</option>
          <option value="N">Apenas Particular</option>
        </select>
        <select id="hosp-pa-filter" class="filter-select" onchange="buscarHospitais()">
          <option value="">Urgência (Todos)</option>
          <option value="S">Pronto Atendimento / 24h</option>
        </select>
        <button class="btn-primary" onclick="buscarHospitais()">Buscar</button>"""

new_search = """<div class="glpi-filter-box" style="display:flex; gap:10px; align-items:center; width:100%;">
          <span style="color:var(--text-secondary); font-size:13px; font-weight:bold; white-space:nowrap;">🔎 FILTRO AVANÇADO:</span>
          <select id="glpi-field" class="filter-select" onchange="window.updateGLPI()" style="width:200px;">
            <option value="nome">Nome do Hospital</option>
            <option value="bairro">Bairro</option>
            <option value="sus">Atendimento SUS</option>
            <option value="pa">Pronto Atendimento (24h)</option>
            <option value="convenio">Convênios Aceitos</option>
          </select>
          <select id="glpi-operator" class="filter-select" style="width:120px;">
            <option value="contains">Contém</option>
            <option value="equals">É igual a</option>
          </select>
          <div id="glpi-value-container" style="flex:1;">
              <input type="text" id="glpi-value" class="search-input" placeholder="Digite o valor..." onkeydown="if(event.key==='Enter') buscarHospitais()" />
          </div>
          <button class="btn-primary" onclick="buscarHospitais()">Aplicar Filtro</button>
        </div>"""

if old_search in html:
    html = html.replace(old_search, new_search)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML GLPI FIXED")

# PATCH JS
with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

new_funcs = """
window.updateGLPI = function() {
    const field = document.getElementById('glpi-field').value;
    const container = document.getElementById('glpi-value-container');
    const op = document.getElementById('glpi-operator');
    
    // reset operators
    op.innerHTML = '<option value="contains">Contém</option><option value="equals">É igual a</option>';
    
    if(field === 'sus' || field === 'pa') {
        op.innerHTML = '<option value="equals">É</option>';
        container.innerHTML = `<select id="glpi-value" class="filter-select" style="width:100%" onchange="buscarHospitais()">
            <option value="S">Sim (Atende)</option>
            <option value="N">Não (Não Atende)</option>
        </select>`;
    } else if(field === 'convenio') {
        container.innerHTML = `<select id="glpi-value" class="filter-select" style="width:100%" onchange="buscarHospitais()">
            <option value="SUS">SUS</option>
            <option value="PARTICULAR">Particular</option>
            <option value="PLANO DE SAUDE PUBLICO">Plano de Saúde Público</option>
            <option value="PLANO DE SAUDE PRIVADO">Plano de Saúde Privado</option>
            <option value="PLANO / SEGURO PROPRIO">Plano / Seguro Próprio</option>
            <option value="PLANO / SEGURO TERCEIRO">Plano / Seguro de Terceiros</option>
        </select>`;
    } else {
        container.innerHTML = `<input type="text" id="glpi-value" class="search-input" placeholder="Digite o valor..." onkeydown="if(event.key==='Enter') buscarHospitais()" />`;
    }
};

function buscarHospitais() {
"""

js = js.replace('function buscarHospitais() {', new_funcs)

body_regex = re.compile(r'function buscarHospitais\(\) \{.*?(?=function renderHospResults)', re.DOTALL)

new_body = """function buscarHospitais() {
    if (!_hospCache) return;
    
    const field = document.getElementById('glpi-field').value;
    const op = document.getElementById('glpi-operator').value;
    const valInput = document.getElementById('glpi-value');
    const value = valInput ? valInput.value.toLowerCase().trim() : '';

    const area = document.getElementById('hosp-results');
    area.innerHTML = '<div style="padding:40px; text-align:center; color:var(--text-muted)">Filtrando dados...</div>';

    setTimeout(() => {
        let filtered = _hospCache;
        
        if (value || field === 'sus' || field === 'pa' || field === 'convenio') {
            filtered = _hospCache.filter(h => {
                let match = false;
                
                if (field === 'nome') {
                    const nome = (h.nome || '').toLowerCase();
                    match = (op === 'contains') ? nome.includes(value) : nome === value;
                } else if (field === 'bairro') {
                    const b = (h.raw && h.raw.NO_BAIRRO ? h.raw.NO_BAIRRO : '').toLowerCase();
                    match = (op === 'contains') ? b.includes(value) : b === value;
                } else if (field === 'sus') {
                    const isSus = h._isSus ? 's' : 'n';
                    match = (isSus === value.toLowerCase());
                } else if (field === 'pa') {
                    const isPa = h._isPA ? 's' : 'n';
                    match = (isPa === value.toLowerCase());
                } else if (field === 'convenio') {
                    const convs = h.convenios || [];
                    const hasConv = convs.some(c => c.toLowerCase() === value.toLowerCase() || c.toLowerCase().includes(value.toLowerCase()));
                    match = (op === 'contains') ? hasConv : hasConv;
                }
                
                return match;
            });
        }

        renderHospResults(filtered.slice(0, 50));
    }, 50);
}

"""

js = body_regex.sub(new_body, js)

js = js.replace("""<div class="info-item"><label>Localização</label><span style="color:var(--text-secondary)">📍 ${bairro} (${hospData.municipio || 'BA'})</span></div>
        <div class="info-item"><label>Total de Leitos</label><strong style="font-size:16px;">${hospData._totalLeitos}</strong></div>
        <div class="info-item"><label>Atende SUS?</label><strong>${hospData._isSus ? '<span style="color:#10b981">Sim</span>' : '<span style="color:#ef4444">Não</span>'}</strong></div>
        <div class="info-item"><label>Pronto Atend. / 24h?</label><strong>${hospData._isPA ? '<span style="color:#10b981">Sim</span>' : '<span style="color:#ef4444">Não</span>'}</strong></div>""", """<div class="info-item"><label>Localização / Características</label>
           <span style="color:var(--text-secondary); display:flex; align-items:center; gap:8px;">
              <span style="font-size:16px;">📍</span> ${bairro} (${hospData.municipio || 'BA'}) 
              ${hospData._isSus ? '<span style="background:var(--accent-cyan); color:#fff; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.2);">SUS</span>' : ''}
              ${hospData._isPA ? '<span style="background:#fbbf24; color:#000; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.2);">🚑 PA</span>' : ''}
           </span>
        </div>
        <div class="info-item"><label>Convênios Atendidos</label><div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:4px;">${(hospData.convenios || []).map(c => `<span style="background:var(--bg-lighter); border:1px solid var(--border-color); color:var(--text-primary); padding:2px 8px; border-radius:4px; font-size:10px;">${c}</span>`).join('')}</div></div>
        <div class="info-item"><label>Total de Leitos</label><strong style="font-size:16px;">${hospData._totalLeitos}</strong></div>""")

old_eq_render = """${advData.equipamentos.map(x => x._highlight ? `<div style="color:#ef4444; font-weight:bold; background:rgba(239, 68, 68, 0.1); padding:4px; border-radius:4px;"><strong style="color:#ef4444;">${x.nome}</strong><br><span style="font-size:10px; font-weight:normal;">Quantidade: ${x.quantidade}</span></div>` : `<div style="padding:4px;"><strong style="color:var(--text-secondary)">${x.nome}</strong><br><span style="font-size:10px; color:var(--text-muted);">Quantidade: ${x.quantidade}</span></div>`).join('')}"""

new_eq_render = """${advData.equipamentos.map(x => x._highlight ? `<div style="color:#ef4444; font-weight:bold; background:rgba(239, 68, 68, 0.1); padding:6px; border-radius:4px;"><strong style="color:#ef4444;">${x.nome}</strong><br><span style="font-size:10px; font-weight:normal;">Existente: ${x.existente || x.quantidade} | Em uso: ${x.em_uso || '-'} | SUS: ${x.sus || '-'}</span></div>` : `<div style="padding:6px;"><strong style="color:var(--text-secondary)">${x.nome}</strong><br><span style="font-size:10px; color:var(--text-muted);">Existente: ${x.existente || x.quantidade} | Em uso: ${x.em_uso || '-'} | SUS: ${x.sus || '-'}</span></div>`).join('')}"""

js = js.replace(old_eq_render, new_eq_render)

footer_injector = """    document.getElementById('hosp-rec-card').innerHTML = htmlRec;"""
footer_new = """    document.getElementById('hosp-rec-card').innerHTML = htmlRec;
    
    const dtAtualizacao = hospData.raw["TO_CHAR(DT_ATUALIZACAO,'DD/MM/YYYY')"] || '—';
    const dtNacional = hospData.raw["TO_CHAR(DT_ATUALIZACAO_ORIGEM,'DD/MM/YYYY')"] || '—';
    const datesHtml = `<div style="margin-top:20px; font-size:11px; color:var(--text-muted); text-align:right; border-top:1px solid var(--border-color); padding-top:10px;">
        Atualização na Base Local: <strong>${dtAtualizacao}</strong> | Última atualização Nacional: <strong>${dtNacional}</strong>
    </div>`;
    
    const oldDates = document.getElementById('hosp-dates-footer');
    if(oldDates) oldDates.remove();
    
    const divDates = document.createElement('div');
    divDates.id = 'hosp-dates-footer';
    divDates.innerHTML = datesHtml;
    document.getElementById('tab-hosp-info').appendChild(divDates);
"""

js = js.replace(footer_injector, footer_new)

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("JS GLPI FIXED")
