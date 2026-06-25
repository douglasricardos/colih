import sys
import re

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_search = """        <input type="text" id="hosp-search-input" placeholder="Nome do hospital ou clínica..." class="search-input"
          oninput="debounce(buscarHospitais, 350)()" onkeydown="if(event.key==='Enter') buscarHospitais()" />
        <button class="btn-primary" onclick="buscarHospitais()">Buscar</button>"""

new_search = """        <input type="text" id="hosp-search-input" placeholder="Nome do hospital, bairro..." class="search-input"
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

if old_search in html:
    html = html.replace(old_search, new_search)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML FIXED")


with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_card = """      <div class="info-grid">
      <div class="info-item"><label>Nome Completo</label><span>${hospData.nome || '—'}</span></div>
      <div class="info-item"><label>Código CNES</label><span><a href="${linkCnes}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">${cnesId} ↗</a></span></div>
      <div class="info-item"><label>Natureza Jurídica</label><span>${natJur}</span></div>
      <div class="info-item"><label>Mantenedora</label><span>${mantenedora}</span></div>
      <div class="info-item"><label>Responsável Técnico</label><span style="color:var(--accent-cyan)">${dir}</span></div>
      <div class="info-item"><label>Endereço Completo</label><span>${enderecoCompleto}</span></div>
      <div class="info-item"><label>Município</label><span>${hospData.municipio || '—'}</span></div>
      <div class="info-item"><label>Telefone</label><span>${tel}</span></div>
      <div class="info-item"><label>E-mail</label><span>${email}</span></div>
      <div class="info-item"><label>Latitude / Longitude</label><span>${latlon}</span></div>
    </div>"""

new_card = """      <div class="info-grid">
      <div class="info-item"><label>Nome Completo</label><span>${hospData.nome || '—'}</span></div>
      <div class="info-item"><label>Código CNES</label><span><a href="${linkCnes}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">${cnesId} ↗</a></span></div>
      <div class="info-item"><label>Atende SUS?</label><span style="font-weight:bold; color: ${hospData._isSus ? 'var(--accent-green)' : 'var(--text-secondary)'}">${hospData._isSus ? 'Sim' : 'Não / Particular'}</span></div>
      <div class="info-item"><label>Pronto Atend. / 24h?</label><span style="font-weight:bold; color: ${hospData._isPA ? 'var(--accent-purple)' : 'var(--text-secondary)'}">${hospData._isPA ? 'Sim' : 'Não'}</span></div>
      <div class="info-item"><label>Total de Leitos</label><span style="font-weight:bold;">${hospData._totalLeitos}</span></div>
      <div class="info-item"><label>Bairro</label><span style="color:var(--accent-cyan)">${bairro}</span></div>
      <div class="info-item"><label>Cidade</label><span>${hospData.municipio || '—'}</span></div>
      <div class="info-item"><label>Natureza Jurídica</label><span>${natJur}</span></div>
      <div class="info-item"><label>Responsável Técnico</label><span style="color:var(--accent-cyan)">${dir}</span></div>
      <div class="info-item"><label>Endereço Completo</label><span>${enderecoCompleto}</span></div>
      <div class="info-item"><label>Telefone</label><span>${tel}</span></div>
      <div class="info-item"><label>Mantenedora</label><span>${mantenedora}</span></div>
    </div>"""

old_prepare = """  const cep = raw.CO_CEP ? ` - CEP: ${raw.CO_CEP}` : '';
  const enderecoCompleto = raw.NO_LOGRADOURO ? `${logr}, ${num}${compl} - ${bairro}${cep}` : logr;"""

new_prepare = """  const cep = raw.CO_CEP ? ` - CEP: ${raw.CO_CEP}` : '';
  const enderecoCompleto = raw.NO_LOGRADOURO ? `${logr}, ${num}${compl} - ${bairro}${cep}` : logr;
  
  // Computations
  let totalLeitos = 0;
  if (hospData.leitos && hospData.leitos.length > 0) {
      totalLeitos = hospData.leitos.reduce((sum, l) => sum + parseInt(l.quantidade || 0, 10), 0);
  }
  hospData._totalLeitos = totalLeitos;
  
  let isSus = false;
  if (raw.CO_CLIENTELA === "01" || raw.CO_CLIENTELA === "02" || raw.CO_CLIENTELA === "1" || raw.CO_CLIENTELA === "2" || (raw.ST_CONTRATO_FORMALIZADO && raw.ST_CONTRATO_FORMALIZADO === 'S')) {
      isSus = true;
  }
  hospData._isSus = isSus;
  
  let isPA = false;
  if (raw.TP_UNIDADE === "20" || raw.TP_UNIDADE === "21" || raw.TP_UNIDADE === "73" || raw.TP_ESTAB_SEMPRE_ABERTO === "S") {
      isPA = true;
  }
  hospData._isPA = isPA;"""

old_search_logic = """  const res = [];
  let added = 0;
  for (let cnes in window._hospCache) {
    if (added >= 40) break;
    const h = window._hospCache[cnes];
    if (h.nome.toLowerCase().includes(query) || cnes.includes(query)) {
      res.push(h);
      added++;
    }
  }"""

new_search_logic = """  const susFilter = document.getElementById('hosp-sus-filter') ? document.getElementById('hosp-sus-filter').value : "";
  const paFilter = document.getElementById('hosp-pa-filter') ? document.getElementById('hosp-pa-filter').value : "";
  
  const res = [];
  let added = 0;
  for (let cnes in window._hospCache) {
    if (added >= 100) break; // Increased limit for better filtering
    const h = window._hospCache[cnes];
    const raw = h.raw || {};
    
    let isSus = false;
    if (raw.CO_CLIENTELA === "01" || raw.CO_CLIENTELA === "02" || raw.CO_CLIENTELA === "1" || raw.CO_CLIENTELA === "2" || raw.ST_CONTRATO_FORMALIZADO === 'S') isSus = true;
    let isPA = false;
    if (raw.TP_UNIDADE === "20" || raw.TP_UNIDADE === "21" || raw.TP_UNIDADE === "73" || raw.TP_ESTAB_SEMPRE_ABERTO === "S") isPA = true;
    
    let passSus = true;
    if (susFilter === 'S' && !isSus) passSus = false;
    if (susFilter === 'N' && isSus) passSus = false;
    
    let passPA = true;
    if (paFilter === 'S' && !isPA) passPA = false;
    
    let bairroMatch = raw.NO_BAIRRO ? raw.NO_BAIRRO.toLowerCase().includes(query) : false;
    
    if (passSus && passPA) {
        if (!query || h.nome.toLowerCase().includes(query) || cnes.includes(query) || bairroMatch) {
          res.push(h);
          added++;
        }
    }
  }"""

if old_card in js and old_prepare in js and old_search_logic in js:
    js = js.replace(old_prepare, new_prepare)
    js = js.replace(old_card, new_card)
    js = js.replace(old_search_logic, new_search_logic)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("JS FIXED")
else:
    print("JS BLOCKS NOT FOUND")
