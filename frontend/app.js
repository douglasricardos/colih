/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   COLIH Captação — app.js
   Lógica principal do frontend SPA
   â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */

const API = 'http://localhost:8000/api';

// Estado global
const state = {
  usuarioAtivo: localStorage.getItem('colih_usuario') || '',
  pipelineData: [],
  pipelineFiltered: [],
  medicoSelecionado: null,
  editandoCns: null,
  especialidades: [],
  infoCache: null,
};

/* ─── Utilitários ─────────────────────────────────────────────── */
function debounce(fn, delay) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

async function fetchAPI(path, opts = {}) {
  try {
    const res = await fetch(API + path, { headers: { 'Content-Type': 'application/json' }, cache: 'no-store', ...opts });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Erro na requisição' }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  } catch (e) {
    if (e.message.includes('Failed to fetch')) {
      showToast('âŒ Backend offline. Verifique se o servidor está rodando.', 'error');
    }
    throw e;
  }
}

function showToast(msg, tipo = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast show ${tipo}`;
  setTimeout(() => t.classList.remove('show'), 3500);
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('pt-BR') + ' ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function statusLabel(status) {
  const m = {
    novo:       ['🔵', 'Novo'],
    em_contato: ['🟡', 'Em Contato'],
    aguardando: ['🟠', 'Aguardando'],
    reuniao:    ['🟣', 'Reunião Agendada'],
    cooperador: ['🟢', 'Cooperador ✅'],
    recusou:    ['🔴', 'Recusou'],
  };
  const [icon, label] = m[status] || ['⚪', status || 'N/A'];
  return `<span class="status-badge status-${status || 'na'}">${icon} ${label}</span>`;
}

function tipoInteracaoLabel(tipo) {
  const m = { ligacao: '📞 Ligação', whatsapp: '💬 WhatsApp', email: '📧 Email', visita: '¥ Visita', outro: '🔹 Outro' };
  return m[tipo] || tipo;
}

function fonteChip(fonte) {
  if (!fonte) return '';
  const comp = fonte.competencia ? ` · Competência ${fonte.competencia.slice(0,4)}/${fonte.competencia.slice(4)}` : '';
  const data = fonte.data_atualizacao_fmt ? ` · Atualizado em ${fonte.data_atualizacao_fmt}` : '';
  return `Fonte: <strong>${fonte.nome || 'DATASUS/CNES'}</strong>${comp}${data}`;
}

/* ─── Tabs ────────────────────────────────────────────────────── */
function openTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.menu-item').forEach(b => b.classList.remove('active'));
  const tab = document.getElementById(`tab-${name}`);
  if (tab) tab.classList.add('active');
  if (btn) btn.classList.add('active');
  
  if (name === 'pipeline') carregarPipeline();
  if (name === 'stats') carregarEstatisticas();
  if (name === 'medicos') buscarMedicos();
  if (name === 'regioes') carregarRegioes();
  
  // COLIH Data
  if (name === 'colih-medicos' || name === 'colih-membros') {
      loadColihData().then(() => {
          if (name === 'colih-medicos') renderColihMedicos();
          if (name === 'colih-membros') renderColihMembros();
      });
  }
  
  // Config Data
  if (name === 'config-hlc') loadHlcDict();
  if (name === 'config-cnes') loadConfigEscopo();
}

function switchInnerTab(id, btn) {
  document.querySelectorAll('.inner-tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.inner-tab').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}

/* ─── Modal ───────────────────────────────────────────────────── */
function abrirModal(id) { document.getElementById(id).classList.add('open'); }
function fecharModal(id) { document.getElementById(id).classList.remove('open'); }

/* ─── Usuários ────────────────────────────────────────────────── */
async function carregarUsuarios() {}

function setUsuarioAtivo(val) {
  state.usuarioAtivo = val;
  localStorage.setItem('colih_usuario', val);
}

/* ─── Info do Cache (Header) ─────────────────────────────────── */
async function carregarInfo() {
  const info = await fetchAPI('/info').catch(() => null);
  if (!info) return;
  state.infoCache = info;

  const fonte = info.fonte || {};
  const elFonte = document.getElementById('fonte-nome');
  if (elFonte) elFonte.textContent = fonte.nome || 'DATASUS/CNES';
  
  document.getElementById('data-atualizacao').textContent = fonte.data_atualizacao_fmt || 'N/D';
  document.getElementById('competencia-valor').textContent = fonte.competencia
    ? `${fonte.competencia.slice(0,4)}/${fonte.competencia.slice(4)}`
    : 'N/D';
  document.getElementById('total-medicos-valor').textContent = (info.totais?.medicos || 0).toLocaleString('pt-BR');
  document.getElementById('colih-membros-count').textContent = info.totais?.membros || 0;
  document.getElementById('colih-coop-count').textContent = info.totais?.cooperadores || 0;
  const colihData = document.getElementById('colihDataUltima');
  if(colihData) colihData.textContent = new Date().toLocaleDateString('pt-BR');

  // Badge pipeline na aba
  document.getElementById('pipeline-count').textContent = info.pipeline?.total || 0;
}

/* ─── Especialidades (select) ────────────────────────────────── */
async function carregarEspecialidades() {
  const data = await fetchAPI('/especialidades').catch(() => ({ especialidades: [] }));
  state.especialidades = data.especialidades || [];
}

// ─── SUS CUSTOM DROPDOWN LOGIC ───
function renderDropdownListMedEsp() {
    const box = document.getElementById('med-esp-list-box');
    const input = document.getElementById('med-esp-input');
    const term = input.value.toLowerCase();
    
    // Add "Todas as especialidades" as the first option
    let html = `<div class="dropdown-list-item" onclick="selecionarMedEsp('', 'Todas as especialidades')" style="font-weight:bold; color:var(--accent-blue);">Todas as especialidades</div>`;
    
    const filtered = state.especialidades.filter(e => e.especialidade.toLowerCase().includes(term));
    if (filtered.length === 0) {
        html += `<div style="padding:10px; font-size:12px; color:var(--text-muted);">Nenhum resultado</div>`;
    } else {
        html += filtered.map(e => `<div class="dropdown-list-item" onclick="selecionarMedEsp('${e.especialidade}', '${e.especialidade}')">${e.especialidade} <span style="font-size:11px; color:var(--text-muted);">(${e.total})</span></div>`).join('');
    }
    box.innerHTML = html;
    box.style.display = 'block';
}

function abrirDropdownMedEsp() { renderDropdownListMedEsp(); }
function filtrarDropdownMedEsp() { renderDropdownListMedEsp(); }
function selecionarMedEsp(val, label) {
    document.getElementById('med-esp-select').value = val;
    document.getElementById('med-esp-input').value = val === '' ? '' : label;
    document.getElementById('med-esp-list-box').style.display = 'none';
    buscarMedicos(); // Auto trigger search
}

document.addEventListener('click', function(e) {
    if(!e.target.closest('#dropdown-med-esp')) {
        const b = document.getElementById('med-esp-list-box');
        if(b) b.style.display = 'none';
    }
    if(!e.target.closest('#dropdown-med-hosp')) {
        const b2 = document.getElementById('med-hosp-list-box');
        if(b2) b2.style.display = 'none';
    }
});

let allHospitalsCache = [];
async function carregarHospitaisCache() {
    try {
        const res = await fetchAPI('/hospitais?limit=1000');
        if (res && res.estabelecimentos) {
            allHospitalsCache = res.estabelecimentos.map(h => h.nome).sort();
        }
    } catch (e) { console.error('Erro carregando cache hospitais', e); }
}

function renderDropdownListMedHosp() {
    const box = document.getElementById('med-hosp-list-box');
    const input = document.getElementById('med-hosp-input');
    const term = input.value.toLowerCase();
    
    let html = `<div class="dropdown-list-item" onclick="selecionarMedHosp('', 'Todos os hospitais')" style="font-weight:bold; color:var(--accent-blue);">Todos os hospitais</div>`;
    
    const filtered = allHospitalsCache.filter(h => h.toLowerCase().includes(term)).slice(0, 50); // limit to 50
    if (filtered.length === 0) {
        html += `<div style="padding:10px; font-size:12px; color:var(--text-muted);">Nenhum resultado</div>`;
    } else {
        html += filtered.map(h => `<div class="dropdown-list-item" onclick="selecionarMedHosp('${h.replace(/'/g, "\\'")}', '${h.replace(/'/g, "\\'")}')">${h}</div>`).join('');
    }
    box.innerHTML = html;
    box.style.display = 'block';
}

function abrirDropdownMedHosp() { renderDropdownListMedHosp(); }
function filtrarDropdownMedHosp() { renderDropdownListMedHosp(); }
function selecionarMedHosp(val, label) {
    document.getElementById('med-hosp-input').value = val === '' ? '' : label;
    document.getElementById('med-hosp-list-box').style.display = 'none';
    buscarMedicos(); // Auto trigger search
}

// Call to load
setTimeout(carregarHospitaisCache, 1000);

/* ─── ABA HOSPITAIS ─────────────────────────────────────────── */
window.updateFiltersUI = function() {
    // filter-complexidade is always visible, apoio só para hospitais
    const tipo = document.getElementById('filter-tipo').value;
    const apoioSelect = document.getElementById('filter-apoio');
    
    if(tipo === '' || tipo.includes('HOSPITAL') || tipo.includes('PRONTO')) {
        apoioSelect.style.display = 'block';
    } else {
        apoioSelect.style.display = 'none';
        apoioSelect.value = '';
    }
};

window.initDistritosFilter = async function() {
    const data = await fetchAPI('/hospitais/valores?field=distrito').catch(() => null);
    if(data && data.valores) {
        const select = document.getElementById('filter-distrito');
        data.valores.forEach(v => {
            const opt = document.createElement('option');
            opt.value = v;
            opt.textContent = v;
            select.appendChild(opt);
        });
        new TomSelect("#filter-distrito", {
            create: false,
            sortField: { field: "text", direction: "asc" },
            onChange: function() { buscarHospitais(); }
        });
    }
};
window.initDistritosFilter();

window._tmoCustomData = {};
async function carregarTmoCustom() {
    window._tmoCustomData = await fetchAPI('/tmo').catch(() => ({}));
}
carregarTmoCustom();

// Lógica do Mapa
let map = null;
let markers = [];
window.isMapVisible = false;
window.hospDataCache = {};

window.toggleMap = function() {
    window.isMapVisible = !window.isMapVisible;
    const mapContainer = document.getElementById('map-container');
    const listContainer = document.getElementById('hosp-results');
    const btn = document.getElementById('btn-toggle-map');
    
    if(window.isMapVisible) {
        mapContainer.style.display = 'block';
        listContainer.style.display = 'none';
        btn.innerHTML = '📋 Lista';
        if(!map) initMap();
        setTimeout(() => {
            map.invalidateSize();
            if(window.currentResults) updateMapMarkers(window.currentResults);
        }, 200);
    } else {
        mapContainer.style.display = 'none';
        listContainer.style.display = 'block';
        btn.innerHTML = 'Œ Mapa';
    }
}

const DISTRICT_COLORS = {
    "barra/rio vermelho": "#ef4444", "boca do rio": "#f97316",
    "cabuíla/beiru": "#eab308", "cajazeiras": "#84cc16",
    "centro histórico": "#22c55e", "itapagipe": "#06b6d4",
    "itapuã": "#3b82f6", "liberdade": "#6366f1",
    "pau da lima": "#a855f7", "são caetano/valéria": "#d946ef",
    "subúrbio ferroviário": "#f43f5e", "brotas": "#0ea5e9"
};

function initMap() {
    map = L.map('map-container').setView([-12.9714, -38.5014], 12);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
    }).addTo(map);
    
    // Legenda baseada no DOM
    const legend = L.control({position: 'bottomright'});
    legend.onAdd = function (map) {
        const div = L.DomUtil.create('div', 'info legend');
        div.id = 'map-legend-container';
        div.style.backgroundColor = 'white';
        div.style.padding = '10px';
        div.style.borderRadius = '5px';
        div.style.boxShadow = '0 1px 5px rgba(0,0,0,0.4)';
        div.style.fontSize = '11px';
        div.style.lineHeight = '20px';
        div.style.color = '#333';
        div.style.maxHeight = '200px';
        div.style.overflowY = 'auto';
        div.innerHTML = 'Carregando...';
        return div;
    };
    legend.addTo(map);
}

function updateMapMarkers(estabelecimentos) {
    if(!map) return;
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    let bounds = [];
    const fallbackColors = ['#f43f5e', '#a855f7', '#0ea5e9', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#3b82f6'];
    const activeGroups = {};
    let colorIndex = 0;

    estabelecimentos.forEach(h => {
        const id = h.cnes || h.id;
        window.hospDataCache[id] = h;
        if(h._lat && h._lng) {
            let color = "#6b7280";
            let groupName = "Outros / N/A";
            
            if (h.municipio === 'Salvador') {
                const d = h._distrito ? h._distrito.toLowerCase().trim() : '';
                color = DISTRICT_COLORS[d] || "#6b7280";
                groupName = d ? 'Salvador - DS ' + d.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : 'Salvador - DS N/A';
            } else {
                groupName = 'Município - ' + (h.municipio || 'N/A');
                if (!activeGroups[groupName]) {
                    color = fallbackColors[colorIndex % fallbackColors.length];
                    colorIndex++;
                } else {
                    color = activeGroups[groupName].color;
                }
            }

            if (!activeGroups[groupName]) {
                activeGroups[groupName] = { color: color, count: 0
};
            }
            activeGroups[groupName].count++;
            
            const markerHtml = `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 4px rgba(0,0,0,0.4);"></div>`;
            const icon = L.divIcon({ html: markerHtml, className: '', iconSize: [14, 14], iconAnchor: [7, 7] });
            
            const m = L.marker([h._lat, h._lng], {icon}).addTo(map);
            const labelDistritoOuMunicipio = h.municipio === 'Salvador' ? h._distrito : h.municipio;
            m.bindPopup(`<b>${h.nome}</b><br/><span style="font-size:11px;color:#666">${h.tipo || 'Instituição de Saúde'}</span><br/><span style="font-size:11px;color:${color};font-weight:bold">${labelDistritoOuMunicipio}</span><br/><br/><button onclick="window.abrirDetalheHospitalById('${id}')" style="background:var(--accent-purple);color:white;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:10px;">Ver Detalhes</button>`);
            
            bounds.push([h._lat, h._lng]);
            markers.push(m);
        }
    });

    // Update legend
    const legendDiv = document.getElementById('map-legend-container');
    if (legendDiv) {
        let labels = ['<strong style="display:block; margin-bottom:4px;">Legenda</strong>'];
        Object.keys(activeGroups).sort().forEach(group => {
            const data = activeGroups[group];
            labels.push(
                `<i style="background:${data.color}; width: 12px; height: 12px; display: inline-block; border-radius: 50%; margin-right: 5px; vertical-align:middle;"></i> <span style="vertical-align:middle; font-size:10px;">${group} (${data.count})</span>`
            );
        });
        legendDiv.innerHTML = labels.join('<br>');
    }
    
    if(bounds.length > 0) map.fitBounds(bounds, {padding: [50, 50], maxZoom: 15});
}

window.abrirDetalheHospitalById = function(id) {
    const h = window.hospDataCache[id];
    if(h) abrirDetalheHospital(h.cnes || h.id, h);
};

function carregarConfiguracoes() {
  const salvos = localStorage.getItem('colih_equip_termos');
  if (salvos) {
    window.EQUIPAMENTOS_APOIO_TERMOS = JSON.parse(salvos);
  } else {
    window.EQUIPAMENTOS_APOIO_TERMOS = ["recuperador", "cell saver", "recuperação de sangue", "autotransfusão", "circulacao extracorporea", "aferese"];
  }
  
  const ta = document.getElementById('config-equip-termos');
  if (ta) ta.value = window.EQUIPAMENTOS_APOIO_TERMOS.join(', ');
}
// Inicializações na carga
carregarConfiguracoes();
window.updateFiltersUI();

function salvarConfiguracoes() {
  const ta = document.getElementById('config-equip-termos');
  if (!ta) return;
  const termos = ta.value.split(',').map(s => s.trim().toLowerCase()).filter(s => s);
  window.EQUIPAMENTOS_APOIO_TERMOS = termos;
  localStorage.setItem('colih_equip_termos', JSON.stringify(termos));
  alert('Configurações salvas com sucesso!');
  if (document.getElementById('tab-hospitais').classList.contains('active')) {
    buscarHospitais();
  }
}

async function carregarGeoConfig() {
  try {
    const cfg = await fetchAPI('/sync-config');
    const badge = document.getElementById('geo-config-badge');
    if (badge) badge.textContent = cfg.descricao || 'Bahia';
    const sel = document.getElementById('geo-uf-select');
    if (sel && cfg.uf) sel.value = cfg.uf;
    if (cfg.municipios_especificos && cfg.municipios_especificos.length > 0) {
      const radioC = document.querySelector('input[name="geo-modo"][value="cidades"]');
      if (radioC) { radioC.checked = true; toggleGeoModo(); }
      const inp = document.getElementById('geo-cidades-input');
      if (inp) inp.value = cfg.municipios_especificos.join(', ');
    }
  } catch(e) { console.warn('Erro ao carregar geo config:', e); }
}

function toggleGeoModo() {
  const modo = document.querySelector('input[name="geo-modo"]:checked')?.value;
  const area = document.getElementById('geo-cidades-area');
  if (area) area.style.display = modo === 'cidades' ? 'block' : 'none';
}

async function salvarGeoConfig() {
  const uf = document.getElementById('geo-uf-select')?.value || 'BA';
  const modo = document.querySelector('input[name="geo-modo"]:checked')?.value;
  let municipios = [];
  if (modo === 'cidades') {
    const inp = document.getElementById('geo-cidades-input')?.value || '';
    municipios = inp.split(',').map(s => s.trim()).filter(s => s && /^\d+$/.test(s));
  }
  try {
    await fetch(`${API}/sync-config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uf, municipios_especificos: municipios })
    });
    const msg = document.getElementById('geo-save-msg');
    if (msg) { msg.style.display = 'inline'; setTimeout(() => msg.style.display = 'none', 5000); }
    carregarGeoConfig();
  } catch(e) { alert('Erro ao salvar: ' + e.message); }
}



async function buscarHospitais() {
  const container = document.getElementById('hosp-results');
  const nome = document.getElementById('filter-nome').value.trim();
  const tipo = document.getElementById('filter-tipo').value;
  const distrito = document.getElementById('filter-distrito').value;
  
  const complexidade = document.getElementById('filter-complexidade').value;
  const apoio = document.getElementById('filter-apoio').value;
  
  const el = document.getElementById('hosp-results');
  el.innerHTML = '<div class="loading-state">Buscando...</div>';
  document.getElementById('hosp-detail').style.display = 'none';

  let qs = `limit=100`;
  const tmo = document.getElementById('filter-tmo') ? document.getElementById('filter-tmo').value : '';
  const pbm = document.getElementById('filter-pbm') ? document.getElementById('filter-pbm').value : '';

  if(nome) qs += `&nome=${encodeURIComponent(nome)}`;
  if(tipo) qs += `&tipo=${encodeURIComponent(tipo)}`;
  if(tmo) qs += `&tmo=${encodeURIComponent(tmo)}`;
  if(pbm) qs += `&pbm=${encodeURIComponent(pbm)}`;
  if(distrito) qs += `&distrito=${encodeURIComponent(distrito)}`;
  if(complexidade) qs += `&complexidade=${encodeURIComponent(complexidade)}`;
  if(apoio) {
      qs += `&apoio_colih=${encodeURIComponent(apoio)}`;
      qs += `&apoio_termos=${encodeURIComponent(window.EQUIPAMENTOS_APOIO_TERMOS.join(','))}`;
  }
  const data = await fetchAPI(`/hospitais?${qs}`).catch(() => null);
  if (!data) { el.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️ </div><p>Erro ao buscar. Verifique o servidor.</p></div>'; return; }

  // Barra de fonte
  const fonteBar = document.getElementById('hosp-fonte-bar');
  fonteBar.style.display = 'flex';
  document.getElementById('hosp-fonte-text').innerHTML = fonteChip(data.fonte);

  if (!data.estabelecimentos || !data.estabelecimentos.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">🏥</div><p>Nenhuma instituição de saúde encontrada.</p></div>';
    window.currentResults = [];
    if(window.isMapVisible) updateMapMarkers([]);
    return;
  }
  
  window.currentResults = data.estabelecimentos;
  if(map || window.isMapVisible) updateMapMarkers(window.currentResults);

  el.innerHTML = `
    <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;">${data.total} estabelecimentos encontrados</p>
    <div class="hosps-grid">
      ${data.estabelecimentos.map(h => {
        // Popula o cache aqui também (no só no mapa)
        const id = h.cnes || h.id;
        window.hospDataCache[id] = h;
        const bairro = h.raw && h.raw.NO_BAIRRO ? h.raw.NO_BAIRRO : '';
        const mapsLink = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent((h.endereco || '') + ' ' + (h.municipio || 'Salvador') + ' ' + bairro)}`;
        
        let equipsHtml = '';
        let countApoio = 0;
        let hasCellSaver = false;
        if (h.equipamentos && h.equipamentos.length > 0) {
            const apoios = h.equipamentos.filter(eq => {
                const eqNome = eq.nome || eq.descricao || 'Equipamento';
                return window.EQUIPAMENTOS_APOIO_TERMOS.some(t => eqNome.toLowerCase().includes(t));
            });
            countApoio = apoios.length;
            if (countApoio > 0) hasCellSaver = true;
            
            if (countApoio > 0) {
              const eqList = apoios.map(eq => {
                  const eqNome = eq.nome || eq.descricao || 'Equipamento';
                  return `<div style="font-size:11px; color:#ef4444; font-weight:bold; border-bottom:1px solid var(--border-color); padding:4px 0;">
                      <span style="white-space:normal; line-height:1.4;" title="${eqNome}">🩸 ${eqNome}</span>
                  </div>`;
              }).join('');
              equipsHtml = `<div style="margin-top:8px; max-height:120px; overflow-y:auto; padding-right:4px; background:rgba(0,0,0,0.02); border-radius:4px; padding:6px;">${eqList}</div>`;
            }
        }

        let conveniosTags = '';
        if (h.convenios && h.convenios.length > 0) {
            const conveniosFiltrados = h.convenios.filter(c => !c.toUpperCase().includes('PLANO DE SAÚDE PÚBLICO') && !c.toUpperCase().includes('PLANO DE SAUDE PUBLICO'));
            conveniosTags = conveniosFiltrados.map(c => `<span style="background:var(--bg-body); border:1px solid var(--border-color); color:var(--text-primary); padding:4px 8px; border-radius:6px; font-size:11px; font-weight:600; box-shadow:0 1px 2px rgba(0,0,0,0.05);">${c}</span>`).join(' ');
        }
        
        // Complexidade badge
        const complexColor = h._complexidade === 'Alta Complexidade' ? '#7c3aed' 
            : h._complexidade === 'Média-Alta Complexidade' ? '#ef4444'
            : h._complexidade === 'Média Complexidade' ? '#3b82f6'
            : '#6b7280';
        
        // Subcomplexidades: mostrar só o subtipo, sem repetir 'Alta Complexidade'
        const altaComplexTags = (h._altaComplexidade || []).map(cat => {
            // Remove prefixo 'Alta Complexidade' ou 'Habilitacao em ' para mostrar só o subtipo
            const label = cat.replace(/^Alta Complexidade\s*[–-]?\s*/i, '').replace(/^Habilitação em\s*/i, '').replace(/^Habilitacao em\s*/i, '').trim();
            return `<span style="background:rgba(124,58,237,0.1); border:1px solid rgba(124,58,237,0.4); color:#a78bfa; padding:2px 8px; border-radius:16px; font-size:10px; font-weight:700;">${label || cat}</span>`;
        }).join(' ');

        return `
        <div class="hosp-card" style="display:flex; flex-direction:column; padding:16px; border:1px solid var(--border-color); border-left: 4px solid ${complexColor}; border-radius:8px; background:var(--bg-card); position:relative; cursor:pointer;" onclick="window.abrirDetalheHospitalById('${h.id || h.cnes}')">
          
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
            <h3 style="font-size:16px; font-weight:700; color:var(--text-primary); margin:0;">${h.nome || 'Sem nome'}</h3>
          </div>
          
          <div style="font-size:11px; color:var(--text-secondary); margin-bottom:8px; text-transform:uppercase; letter-spacing:0.5px;">${h.tipo || 'ESTABELECIMENTO DE SAÚDE'}</div>
          
          <div style="margin-bottom:8px;">
            ${h.municipio === 'Salvador' 
              ? (h._distrito ? `<div style="font-weight:700; color:var(--accent-blue); margin-bottom:4px; font-size:12px;">📍 Distrito Sanitário: ${h._distrito}</div>` : '') 
              : `<div style="font-weight:700; color:var(--accent-purple); margin-bottom:4px; font-size:12px;"> Município: ${h.municipio}</div>`
            }
            <a href="${mapsLink}" target="_blank" onclick="event.stopPropagation()" style="color:var(--text-secondary); text-decoration:none; display:flex; align-items:center; gap:4px; font-weight:500; font-size:12px;">— ${h.endereco || ''}${bairro ? ' - ' + bairro : ''} ↗</a>
          </div>
          
          <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:8px; align-items:center;">
            <span style="background:${complexColor}; color:white; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:700;">${h._complexidade || 'N/A'}</span>
            ${h._totalLeitos > 0 ? `<span style="background:var(--bg-body); border:1px solid var(--border-color); color:var(--text-secondary); padding:4px 8px; border-radius:4px; font-size:11px; font-weight:700;"> 🛏️  ${h._totalLeitos} Leitos</span>` : ''}
            ${h._isPA ? '<span style="background:#f59e0b; color:white; padding:4px 8px; border-radius:4px; font-weight:700; font-size:11px;">🚑 Pronto Atendimento (PA)</span>' : ''}
            ${h._isSus ? '<span style="background:var(--accent-cyan); color:var(--bg-body); padding:4px 8px; border-radius:4px; font-weight:700; font-size:11px;">SUS</span>' : ''}
            ${(h.tmo_custom || (window._tmoCustomData && (window._tmoCustomData[h.cnes] || window._tmoCustomData[h.id])) || (h.servicosEspecializados || []).concat(h.classificacoesServicos || []).some(s => typeof s === 'string' ? s.toUpperCase() === 'MEDULA OSSEA' : s.nome && s.nome.toUpperCase() === 'MEDULA OSSEA')) ? '<span style="background:#ef4444; color:white; padding:4px 8px; border-radius:4px; font-weight:700; font-size:11px;">TMO</span>' : ''}
            ${h._pbm ? `<span style="background:#10b981; color:white; padding:4px 8px; border-radius:4px; font-weight:700; font-size:11px;">🩸 PBM</span>` : ''}
          </div>
          
          ${altaComplexTags ? `<div style="display:flex; gap:4px; flex-wrap:wrap; margin-bottom:8px;">${altaComplexTags}</div>` : ''}

          <div style="font-size:11px; font-weight:700; color:var(--text-secondary); margin-bottom:6px;">Planos / Convênios Atendidos:</div>
          <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:16px;">
            ${conveniosTags || '<span style="font-size:11px; color:var(--text-muted);">No informados</span>'}
          </div>

          <div style="margin-top:auto;">
            ${hasCellSaver ? `<div style="background:#fef2f2; border:1px solid #f87171; color:#b91c1c; padding:6px 8px; border-radius:4px; font-size:11px; font-weight:700; margin-bottom:8px; text-align:center;">⚠️ EQUIPAMENTOS DE APOIO  COLIH DISPONÍVEIS (${countApoio})</div>` : ''}
            ${equipsHtml}
          </div>
          
        </div>
        `;
      }).join('')}
    </div>
    ${data.total > 100 ? `<div style="text-align:center; padding:16px; font-size:13px; color:var(--text-muted); border-top:1px solid var(--border-color); margin-top:16px; background:var(--bg-card); border-radius:8px;">
      Exibindo os primeiros <strong>${data.estabelecimentos.length}</strong> resultados de um total de <strong>${data.total}</strong>. Utilize os filtros para refinar a busca.
    </div>` : `<div style="text-align:center; padding:16px; font-size:13px; color:var(--text-muted); border-top:1px solid var(--border-color); margin-top:16px; background:var(--bg-card); border-radius:8px;">
      Exibindo <strong>${data.estabelecimentos.length}</strong> resultados.
    </div>`}
  `;
  return data.estabelecimentos;
return window.currentResults;
}

async function abrirDetalheHospital(cnesId, hospData) {
  if (hospData && hospData.nome) {
    const safeName = hospData.nome.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    history.pushState({cnesId: cnesId, type: 'hospital'}, '', '/instituicoes/' + safeName);
  }
  document.getElementById('hosp-results').innerHTML = '';
  document.getElementById('hosp-fonte-bar').style.display = 'none';
  const detail = document.getElementById('hosp-detail');
  detail.style.display = 'block';

  document.getElementById('hosp-detail-title').innerHTML = `
    <h2 style="font-size:18px;font-weight:800;">${hospData.nome || cnesId}</h2>
    <p style="color:var(--text-secondary);font-size:13px;">CNES: ${cnesId} · ${hospData.municipio || 'Salvador'}</p>
  `;

  const linkCnes = `https://cnes.datasus.gov.br/pages/estabelecimentos/ficha/index.jsp?coUnidade=${cnesId}`;
  window._currentHospLinkCnes = linkCnes;

  let espsHtml = '';
  const especialidadesFiltradas = (hospData.especialidades || []).filter(e => e && !e.includes('CBO'));
  if (especialidadesFiltradas.length > 0) {
    espsHtml = especialidadesFiltradas.map(e => `<span class="status-badge" style="background:var(--accent-purple); color:white; font-size:12px; padding:6px 12px; border-radius:15px; font-weight:600; cursor:pointer;" onclick="filtrarMedicosPorEspecialidade('${e.replace(/'/g,"'").replace(/"/g,"&quot;")}')">${e}</span>`).join('');
  } else {
    espsHtml = '<p style="color:var(--text-muted); font-size:13px; width:100%;">Nenhuma especialidade mapeada para este hospital.</p>';
  }

  const raw = hospData.raw || {};
  let dir = raw.NOME_DIRETOR_CLINICO || raw.NO_DIRETOR || raw.NOME_DIRETORCLN || hospData.responsavel || '—';
  if (dir !== '—' && /^[d.-]+$/.test(dir)) dir = '—';
  if (dir === '—' && raw.REG_DIRETORCLN) dir = `CRM: ${raw.REG_DIRETORCLN} (Nome no localizado)`;
  const mantenedora = raw.NO_RAZAO_SOCIAL ? `${raw.NO_RAZAO_SOCIAL} (CNPJ: ${raw.NU_CNPJ_MANTENEDORA || '—'})` : '—';
  const natJur = raw.DS_NATUREZA_JUR || raw.CO_NATUREZA_JUR || '—';
  
  const logr = raw.NO_LOGRADOURO || hospData.endereco || '—';
  const num = raw.NU_ENDERECO || 'S/N';
  const compl = raw.NO_COMPLEMENTO ? ` - ${raw.NO_COMPLEMENTO}` : '';
  const bairro = raw.NO_BAIRRO || '';
  const cep = raw.CO_CEP ? ` - CEP: ${raw.CO_CEP}` : '';
  const enderecoCompleto = raw.NO_LOGRADOURO ? `${logr}, ${num}${compl} - ${bairro}${cep}` : logr;
  
  const email = raw.NO_EMAIL || '—';
  const tel = raw.NU_TELEFONE || '—';
  const lat = raw.NU_LATITUDE;
  const lon = raw.NU_LONGITUDE;
  const latlon = (lat && lon) ? `<a href="https://maps.google.com/?q=${lat},${lon}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">${lat}, ${lon} ↗</a>` : 'No informado';
  const dtAtualizacao = raw["TO_CHAR(DT_ATUALIZACAO,'DD/MM/YYYY')"] || '—';



  document.getElementById('hosp-info-card').innerHTML = `
    <div class="info-grid">
      <div class="info-item"><label>Nome Completo</label><span>${hospData.nome || '—'}</span></div>
      <div class="info-item"><label>Código CNES</label><span><a href="${linkCnes}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">${cnesId} ↗</a></span></div>
      <div class="info-item"><label>Macrorregião</label><span>${hospData._macrorregiao || 'N/A'}</span></div>
      ${hospData.municipio === 'Salvador' ? `<div class="info-item"><label>Distrito Sanitário</label><span style="font-weight:bold;">${hospData._distrito || 'N/A'}</span></div>` : ''}
      <div class="info-item"><label>Atende SUS?</label><span style="font-weight:bold; color: ${hospData._isSus ? 'var(--accent-green)' : 'var(--text-secondary)'}">${hospData._isSus ? 'Sim' : 'No / Particular'}</span></div>
      <div class="info-item"><label>Pronto Atend. / 24h?</label><span style="font-weight:bold; color: ${hospData._isPA ? 'var(--accent-purple)' : 'var(--text-secondary)'}">${hospData._isPA ? 'Sim' : 'No'}</span></div>
      <div class="info-item"><label>Total de Leitos</label><span style="font-weight:bold;">${hospData._totalLeitos}</span></div>
      <div class="info-item"><label>Bairro</label><span style="color:var(--accent-cyan)">${bairro}</span></div>
      <div class="info-item"><label>Cidade</label><span>${hospData.municipio || '—'}</span></div>
      <div class="info-item"><label>Natureza Jurídica</label><span>${natJur}</span></div>
      <div class="info-item"><label>Responsável Técnico</label><span style="color:var(--accent-cyan)">${dir}</span></div>
      <div class="info-item"><label>Endereço Completo</label><span>${enderecoCompleto}</span></div>
      <div class="info-item"><label>Telefone</label><span>${tel}</span></div>
      <div class="info-item"><label>Mantenedora</label><span>${mantenedora}</span></div>
      <div class="info-item"><label>ÚÚltima Atualização Nacional</label><span>${hospData._dtAtualizacaoNacional || 'N/A'}</span></div>
      <div class="info-item"><label>ÚÚltima Atualização Regional</label><span>${hospData._dtAtualizacaoRegional || 'N/A'}</span></div>
    </div>
    ${(() => {
        if (window._tmoCustomData && window._tmoCustomData[cnesId]) {
            const linkInfo = window._tmoCustomData[cnesId];
            const hasDoctors = linkInfo.doctors && linkInfo.doctors.length > 0;
            return `
            <div style="margin-top: 16px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 16px;">
                <div style="font-size: 14px; font-weight: bold; color: #ef4444; margin-bottom: 8px; text-align: center;">
                    🔥 Centro de Transplante de Medula Óssea
                </div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 16px; text-align: center;">
                    A relação de médicos TMO para este hospital é gerenciada customizadamente.
                </div>
                
                ${hasDoctors ? `
                <div style="background: white; border: 1px solid var(--border); border-radius: 6px; padding: 12px; margin-bottom: 16px;">
                    <div style="font-size: 12px; font-weight: bold; color: var(--text-primary); margin-bottom: 8px;">Equipe Médica Conhecida (TMO):</div>
                    <ul style="margin: 0; padding-left: 16px; font-size: 12px; color: var(--text-secondary); line-height: 1.6;">
                        ${linkInfo.doctors.map(doc => `<li>${doc.name} ${doc.cns ? `<a href="javascript:void(0)" onclick="openTab('medicos', document.getElementById('tab-btn-medicos')); abrirDetalheMedico('${doc.cns}'); return false;" style="color:var(--accent-cyan);text-decoration:underline; font-weight:bold; margin-left:8px;">👤 Mais Informações</a>` : (doc.link ? `<a href="${doc.link}" target="_blank" style="color:var(--accent-cyan);text-decoration:none;">🔗 Perfil Externo</a>` : '')}</li>`).join('')}
                    </ul>
                </div>
                ` : `
                <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 12px; text-align: center; font-style: italic;">
                    * Nenhum médico cadastrado na equipe TMO ainda.
                </div>
                `}

                <div style="text-align: center; display: flex; flex-direction: column; gap: 8px; align-items: center;">
                    ${linkInfo.url ? `
                    <a href="${linkInfo.url}" target="_blank" style="display: inline-block; background: #ef4444; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold; box-shadow: 0 2px 4px rgba(239,68,68,0.3); transition: transform 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        🔗 ${linkInfo.label || 'Site do Hospital'}
                    </a>` : ''}
                    <button onclick="abrirModalAddMedicoTmo('${cnesId}')" style="display: inline-block; background: var(--bg-body); border: 1px dashed #ef4444; color: #ef4444; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; transition: all 0.2s;" onmouseover="this.style.background='#ef4444'; this.style.color='white';" onmouseout="this.style.background='var(--bg-body)'; this.style.color='#ef4444';">
                        ➕ Adicionar Médico/Link
                    </button>
                </div>
            </div>
            `;
        } else {
            return `
            <div style="margin-top: 16px; text-align: center;">
                 <button onclick="abrirModalAddMedicoTmo('${cnesId}')" style="display: inline-block; background: var(--bg-body); border: 1px dashed var(--text-muted); color: var(--text-secondary); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 11px; transition: all 0.2s;" onmouseover="this.style.borderColor='#ef4444'; this.style.color='#ef4444';" onmouseout="this.style.borderColor='var(--text-muted)'; this.style.color='var(--text-secondary)';">
                     ➕ Forçar como Centro de TMO
                 </button>
            </div>`;
        }
    })()}

    <div style="margin-top:15px; padding-top:12px; border-top:1px solid var(--border); font-size:11px; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center;">
      <span><strong>Transparência de Dados:</strong> Todos os detalhes extraídos nativamente da tabela <code>tbEstabelecimento</code> via Extrato CSV DATASUS mensal.</span>
      <span>ÚÚltima atualização no CNES: ${dtAtualizacao}</span>
    </div>
  `;

  let offlineAdvanced = '';
  const advData = hospData;
  let cellSaverBadge = '';
  
  if (advData.equipamentos && advData.equipamentos.length) {
      const isCellSaver = (n) => {
          const str = (n || '').toLowerCase();
          return window.EQUIPAMENTOS_APOIO_TERMOS.some(t => str.includes(t));
      };
      
      const apoios = advData.equipamentos.filter(x => isCellSaver(x.nome || x.descricao));
      if (apoios.length > 0) {
          // Extrair nomes limpos e únicos para a legenda
          const nomesUnicos = [...new Set(apoios.map(x => x.nome || x.descricao))];
          const nomesStr = nomesUnicos.join(', ');
          cellSaverBadge = `<div style="background:#ef4444; color:#ffffff; padding:12px; border-radius:6px; font-size:13px; font-weight:bold; margin-bottom:15px; display:flex; align-items:center; gap:10px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);">
              <span style="font-size:18px;">🩸</span> <span>ALERTA COLIH: Este hospital possui equipamento(s) compatível(is) com a Recuperação Intraoperatória (${nomesStr})</span>
          </div>`;
      }
      
      // Ordenar colocando apoios no topo
      advData.equipamentos.sort((a, b) => {
          const aAp = isCellSaver(a.nome || a.descricao);
          const bAp = isCellSaver(b.nome || b.descricao);
          if (aAp && !bAp) return -1;
          if (!aAp && bAp) return 1;
          return 0;
      });
      
      advData.equipamentos.forEach(x => {
          if (isCellSaver(x.nome || x.descricao)) {
              x._highlight = true;
          }
      });
  }
  
  document.getElementById('hosp-rec-card').innerHTML = cellSaverBadge;
  
  // 1. Atendimento Prestado
  if (advData.atendimentoPrestado && advData.atendimentoPrestado.length) {
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:13px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Atendimento Prestado</div>
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${advData.atendimentoPrestado.map(x => typeof x === 'object' ? `<span class="status-badge" style="font-size:11px;">${x.tipo || x}</span>` : `<span class="status-badge" style="font-size:11px;">${x}</span>`).join('')}
          </div>
      </div>`;
  }
  
  // 1.5 PBM (Gerenciamento do Uso de Sangue)
  offlineAdvanced += `
    <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
        <div style="font-size:13px; font-weight:600; color:#f97316; margin-bottom:8px;">🩸 Gerenciamento de Sangue do Paciente (PBM)</div>
        <div style="display:flex; gap:8px;">
            <button onclick="window.togglePBM('${cnesId}', ${hospData._pbm ? 'true' : 'false'})" style="background:${hospData._pbm ? '#10b981' : 'var(--bg-body)'}; color:${hospData._pbm ? 'white' : 'var(--text-primary)'}; border:1px solid ${hospData._pbm ? '#10b981' : 'var(--border-color)'}; padding:4px 8px; border-radius:4px; font-weight:600; font-size:11px; cursor:pointer;">
                ${hospData._pbm ? '✅ PBM Implantado (Clique para remover)' : 'Marcar como PBM Implantado'}
            </button>
            ${hospData._pbm_link ? `<a href="${hospData._pbm_link}" target="_blank" style="background:#065f46; color:white; padding:4px 8px; border-radius:4px; font-weight:600; font-size:11px; text-decoration:none; display:flex; align-items:center;"> Ver Referência</a>` : ''}
            ${hospData._pbm ? `<button onclick="window.editPBMLink('${cnesId}')" style="background:var(--bg-body); color:var(--accent-blue); border:1px solid var(--accent-blue); padding:4px 8px; border-radius:4px; font-weight:600; font-size:11px; cursor:pointer;">✏️ Alterar Link</button>` : ''}
        </div>
    </div>
  `;


  // 2. Servios Especializados  com Alta Complexidade destacada
  if (advData.servicosEspecializados && advData.servicosEspecializados.length) {
      // Termos de Alta Complexidade para destacar
      const TERMOS_ALTA = ['TRANSPLANTE','CARDIOVASCULAR','CARDIO','ONCOLOGIA','CANCER','QUIMIOTERAPIA','RADIOTERAPIA','NEUROLOGIA','NEUROCIRURGIA','ORTOPEDIA','TRAUMATOLOGIA','HEMOTERAPIA','HEMATOLOGIA','HEMODIALISE','DIALISE','NEONATOLOGIA','PERINATAL'];
      
      let hasTransplante = false;
      const servicosComMarca = advData.servicosEspecializados.map(x => {
          const nome = typeof x === 'object' ? (x.tipo || String(x)) : String(x);
          if (nome.toUpperCase().includes('TRANSPLANTE')) hasTransplante = true;
          const isAlta = TERMOS_ALTA.some(t => nome.toUpperCase().includes(t));
          return { nome, isAlta };
      })
      .filter(s => !s.nome.toUpperCase().includes('TRANSPLANTE')) // Separar transplante da lista principal
      .sort((a,b) => b.isAlta - a.isAlta); // Alta complexidade primeiro
      
      const altaCount = servicosComMarca.filter(s => s.isAlta).length + (hasTransplante ? 1 : 0);
      
      let transplanteHtml = '';
      if (hasTransplante) {
          // Filtrar classificações vinculadas a transplante / doação / órgãos
          const tmoTerms = ['MEDULA', 'RIM', 'FIGADO', 'CORNEA', 'ESCLERA', 'RETIRADA', 'TRANSPLANT', 'ORGAO', 'TECIDO', 'DOACAO', 'CAPTACAO', 'CORACAO', 'PULMAO', 'PANCREAS', 'OSSEA'];
          const tiposTransplante = (advData.classificacoesServicos || []).map(x => typeof x === 'object' ? (x.nome || String(x)) : String(x))
              .filter(c => tmoTerms.some(t => c.toUpperCase().includes(t)));
              
          transplanteHtml = `
          <div style="margin-bottom: 16px; background: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 12px; border-left: 3px solid #ef4444;">
              <div style="font-size:12px; font-weight:800; color:#ef4444; margin-bottom: 8px; display:flex; align-items:center;">
                  ❤️ TRANSPLANTES
              </div>
              <div style="display:flex; flex-wrap:wrap; gap:6px;">
                  ${tiposTransplante.length > 0 ? tiposTransplante.map(t => {
                      const isMedula = t.toUpperCase().includes('MEDULA OSSEA');
                      if (isMedula) {
                          return `<span onclick="filtrarMedicosPorEspecialidade('${t}')" style="cursor:pointer; background:#ef4444; color:white; padding:4px 10px; border-radius:16px; font-size:11px; font-weight:800; box-shadow: 0 2px 4px rgba(239,68,68,0.3); transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">🔥 ${t}</span>`;
                      }
                      return `<span onclick="filtrarMedicosPorEspecialidade('${t}')" style="cursor:pointer; background:var(--bg-body); border:1px solid rgba(239,68,68,0.4); color:#ef4444; padding:4px 10px; border-radius:16px; font-size:11px; font-weight:700; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">${t}</span>`;
                  }).join('') : '<span style="color:var(--text-tertiary); font-size:11px; font-style:italic;">Tipos no especificados no CNES</span>'}
              </div>
          </div>
          `;
      }
      
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:16px; border-radius:8px; border:1px solid var(--border-color); border-left:4px solid #7c3aed; margin-bottom:10px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
              <div style="font-size:13px; font-weight:700; color:#7c3aed;">🏥 Serviços Especializados</div>
              ${altaCount > 0 ? `<span style="background:#7c3aed; color:white; padding:3px 10px; border-radius:16px; font-size:11px; font-weight:800;">${altaCount} de Alta Complexidade</span>` : ''}
          </div>
          ${transplanteHtml}
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${servicosComMarca.map(s => s.isAlta 
                  ? `<span style="background:rgba(124,58,237,0.15); border:1px solid rgba(124,58,237,0.5); color:#7c3aed; padding:4px 10px; border-radius:16px; font-size:11px; font-weight:800;">â­ ${s.nome}</span>`
                  : `<span style="background:var(--bg-body); border:1px solid var(--border-color); color:var(--text-secondary); padding:4px 10px; border-radius:16px; font-size:11px; font-weight:600;">${s.nome}</span>`
              ).join('')}
          </div>
      </div>`;
  }

  // 3. Comissões e Comitês
  if (advData.comissoes && advData.comissoes.length) {
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:13px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Comissões e Comitês</div>
          <ul style="margin:0; padding-left:15px; font-size:12px; color:var(--text-secondary);">
              ${advData.comissoes.map(x => typeof x === 'object' ? `<li>${x.tipo || x}</li>` : `<li>${x}</li>`).join('')}
          </ul>
      </div>`;
  }
  
  // 4. Leitos Hospitalares
  if (advData.leitos && advData.leitos.length) {
    offlineAdvanced += `
    <details style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px; cursor:pointer;" open>
        <summary style="font-size:13px; font-weight:600; color:var(--accent-purple); outline:none; user-select:none;">Leitos Hospitalares <span style="font-size:11px; font-weight:normal; color:var(--text-muted); float:right; margin-top:2px;">(Expandir/Recolher)</span></summary>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:12px; margin-top:12px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.05);">
            ${advData.leitos.map(x => `<div><strong style="color:var(--text-secondary)">${x.nome}</strong>: ${x.quantidade}</div>`).join('')}
        </div>
    </details>`;
  }

  // 5. Equipamentos
  if (advData.equipamentos && advData.equipamentos.length) {
    offlineAdvanced += `
    <details style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px; cursor:pointer;" open>
        <summary style="font-size:13px; font-weight:600; color:var(--accent-purple); outline:none; user-select:none;">Equipamentos (${advData.equipamentos.length}) <span style="font-size:11px; font-weight:normal; color:var(--text-muted); float:right; margin-top:2px;">(Expandir/Recolher)</span></summary>
        <div style="display:grid; grid-template-columns: 1fr; gap:8px; font-size:12px; margin-top:12px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.05);">
            ${advData.equipamentos.map(x => `
                <div style="${x._highlight ? 'color:#ef4444; font-weight:bold; background:rgba(239, 68, 68, 0.1); padding:8px; border-radius:4px;' : 'padding:6px 0; border-bottom:1px solid var(--border-color);'} display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <span style="flex:1; min-width:200px;">${x._highlight ? '🩸 ' : '⚙️ '}${x.nome || x.descricao}</span>
                    <span style="font-size:11px; color:var(--text-secondary); text-align:right;">(Existente: ${x.existente||x.quantidade||0} | Em Uso: ${x.em_uso||0} | Atende SUS: ${x.sus||'N/A'})</span>
                </div>
            `).join('')}
        </div>
    </details>`;
  }
  
  document.getElementById('hosp-rec-card').innerHTML += offlineAdvanced;

  document.getElementById('prof-table-wrap').innerHTML = '<div class="loading-state">Carregando médicos...</div>';
  const data = await fetchAPI(`/hospitais/${cnesId}`).catch(() => null);

  if (!data) { document.getElementById('prof-table-wrap').innerHTML = '<div class="empty-state"><p>Erro ao carregar profissionais.</p></div>'; return; }

  document.getElementById('prof-fonte-text').innerHTML = fonteChip(data.fonte);
  document.getElementById('prof-count').textContent = `${data.total_medicos} médicos`;

  window._hospMedicos = data.medicos || [];
  renderizarProfissionais(window._hospMedicos);

  if (window._hospMedicos.length > 0) {
    const contagem = {};
    window._hospMedicos.forEach(m => {
      let esps = [];
      if (m.especialidade_hlc9) {
         esps.push(m.especialidade_hlc9);
      } else if (m.especialidade) {
         esps = m.especialidade.split(' / ').map(e => e.trim());
      }
      esps.forEach(e => {
        if (e && !e.includes('CBO')) {
           contagem[e] = (contagem[e] || 0) + 1;
        }
      });
    });
    
    let contagemHtml = '';
    const espsSorted = Object.keys(contagem).sort((a,b) => contagem[b] - contagem[a]);
    if (espsSorted.length > 0) {
      contagemHtml = espsSorted.map(e => `<span class="status-badge" style="background:var(--accent-purple); color:white; font-size:13px; padding:8px 14px; border-radius:8px; font-weight:600; display:inline-flex; align-items:center; gap:6px; box-shadow:0 2px 4px rgba(0,0,0,0.05); cursor:pointer;" onclick="filtrarMedicosPorEspecialidade('${e.replace(/'/g,"'").replace(/"/g,"&quot;")}')">${e} <span style="background:rgba(255,255,255,0.25); padding:2px 6px; border-radius:12px; font-size:11px;">${contagem[e]}</span></span>`).join('');
    } else {
      contagemHtml = '<p style="color:var(--text-muted); font-size:13px; width:100%;">Nenhuma especialidade mapeada para este hospital.</p>';
    }
    document.getElementById('hosp-esps-card').innerHTML = contagemHtml;
  } else {
    document.getElementById('hosp-esps-card').innerHTML = espsHtml;
  }
}

function fecharDetalheHospital() {
  document.getElementById('hosp-detail').style.display = 'none';
  document.getElementById('hosp-results').innerHTML = '';
}

function filtrarProfissionais() {
  const q = document.getElementById('prof-filter-input').value.toLowerCase();
  const filtrados = q
    ? (window._hospMedicos || []).filter(m =>
        (m.especialidade || '').toLowerCase().includes(q) || 
        (m.nome || '').toLowerCase().includes(q) ||
        (m.especialidade_hlc9 || '').toLowerCase().includes(q))
    : (window._hospMedicos || []);
  document.getElementById('prof-count').textContent = `${filtrados.length} médicos`;
  renderizarProfissionais(filtrados);
}

window.filtrarMedicosPorEspecialidade = function(esp) {
  let busca = esp.toUpperCase();
  const mapaTermos = {
      'MEDULA': 'Oncolog', // Traduz para Oncologista (TMO)
      'ONCOLOGIA': 'Oncolog',
      'CORNEA': 'Oftalmolog',
      'ESCLERA': 'Oftalmolog',
      'RIM': 'Nefrolog',
      'FIGADO': 'Gastro',
      'CORACAO': 'Cardiolog',
      'PULMAO': 'Pneumolog'
  };
  
  for (const [key, value] of Object.entries(mapaTermos)) {
      if (busca.includes(key)) {
          busca = value;
          break;
      }
  }

  document.getElementById('prof-filter-input').value = busca;
  filtrarProfissionais();
  
  const btn = document.querySelector("button[onclick*='tab-hosp-prof']");
  if (btn) {
      switchTab('tab-hosp-prof', btn);
  }
  
  document.getElementById('prof-filter-input').scrollIntoView({behavior: 'smooth', block: 'center'});
};

function renderizarProfissionais(medicos) {
  if (!medicos.length) {
    document.getElementById('prof-table-wrap').innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div><p>Nenhum médico encontrado com esse filtro.</p></div>';
    return;
  }
  document.getElementById('prof-table-wrap').innerHTML = `
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Nome</th>
          <th>CBO</th>
          <th>Especialidade</th>
          <th>CNS</th>
          <th>Pipeline</th>
          <th>Ações</th>
        </tr></thead>
        <tbody>
          ${medicos.map(m => {
            const hlc9 = m.especialidade_hlc9 ? `<br><span style="color:var(--accent-purple); font-size:11px; font-weight:600;">HLC-9: ${m.especialidade_hlc9}</span>` : '';
            return `
            <tr>
              <td style="font-weight:600">${m.nome || '—'}</td>
              <td class="td-muted" style="font-family:monospace; font-size:12px;">${m.cbo || '—'}</td>
              <td class="td-muted" style="line-height:1.4;">${m.especialidade || '—'}${hlc9}</td>
              <td class="td-muted" style="font-size:11px;">
                <a href="${window._currentHospLinkCnes}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;" title="Ver hospital no CNES">${m.cns || '—'} 🔗</a>
              </td>
              <td>${m.no_pipeline ? statusLabel(m.status_pipeline) : '<span class="status-badge status-na">—</span>'}</td>
              <td class="td-actions">
                <button class="btn-secondary btn-sm" onclick="abrirDetalheMedicoFromHosp(${JSON.stringify(m).replace(/"/g,'&quot;')})">Mais Informações</button>
                ${m.no_pipeline
                  ? `<span class="badge" style="background:var(--bg-success); color:#fff; font-size:11px;"><i data-lucide="check-circle" style="width:12px; height:12px; display:inline-block; vertical-align:text-bottom;"></i> No Pipeline</span>`
                  : `<button class="btn-primary btn-sm" onclick="abrirModalPipeline(${JSON.stringify(m).replace(/"/g,'&quot;')}, '')">+ Pipeline</button>`}
              </td>
            </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

/* ─── ABA MÉDICOS ────────────────────────────────────────────── */
async function buscarMedicos() {
  const nome = document.getElementById('med-nome-input').value.trim();
  const esp = document.getElementById('med-esp-select').value;
  const hosp = document.getElementById('med-hosp-input')?.value.trim();
  const sus = document.getElementById('med-sus-select')?.value;

  const el = document.getElementById('med-results');
  el.innerHTML = '<div class="loading-state">Buscando...</div>';
  document.getElementById('med-detail').style.display = 'none';

  const params = new URLSearchParams({ limit: 80 });
  if (nome) params.set('nome', nome);
  if (esp) params.set('especialidade', esp);
  if (hosp) params.set('hospital', hosp);
  if (sus) params.set('atende_sus', sus);

  const data = await fetchAPI(`/medicos?${params}`).catch(() => null);
  if (!data) { el.innerHTML = '<div class="empty-state"><p>Erro ao buscar.</p></div>'; return; }

  const fonteBar = document.getElementById('med-fonte-bar');
  fonteBar.style.display = 'flex';
  document.getElementById('med-fonte-text').innerHTML = fonteChip(data.fonte)
    + (data.fonte?.aviso ? ` <em style="color:var(--text-muted)"> · ${data.fonte.aviso}</em>` : '');

  if (!data.medicos.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div><p>Nenhum médico encontrado.</p></div>';
    return;
  }

  el.innerHTML = `
    <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;">${data.total} médico(s) encontrado(s)</p>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Nome</th><th>Especialidade</th><th>Instituições</th><th>Pipeline</th><th>Ações</th>
        </tr></thead>
        <tbody>
          ${data.medicos.map(m => `
            <tr style="${m.colih ? 'background: rgba(16, 185, 129, 0.05);' : ''}">
              <td style="font-weight:600; ${m.colih ? 'color:#10b981;' : ''}">
                ${m.colih ? '<span title="Cooperador COLIH" style="margin-right:4px;">🤝</span>' : ''}${m.nome || '—'}
                ${m.colih && m.colih.membro_resp ? `<div style="font-size:11px; color:var(--text-muted); margin-top:2px;">Resp: ${m.colih.membro_resp}</div>` : ''}
              </td>
              <td class="td-muted">${m.especialidade || '—'}</td>
              <td class="td-muted">
                <div style="margin-bottom:4px;">${(m.vinculos || []).filter(v => v.ativo).length} ativo(s) / ${(m.vinculos || []).length} total</div>
                ${m.atende_sus === 'Sim' ? `<span title="Hospitais SUS:\n${(m.hospitais_sus||[]).join('\n')}" style="display:inline-block; font-size:10px; background:rgba(34, 197, 94, 0.1); color:#22c55e; padding:2px 6px; border-radius:4px; cursor:help; border:1px solid rgba(34, 197, 94, 0.2); font-weight:600;">SUS: Sim</span>` : ''}
              </td>
              <td>${m.no_pipeline ? statusLabel(m.status_pipeline) : '<span class="status-badge status-na">—</span>'}</td>
              <td class="td-actions">
                <button class="btn-secondary btn-sm" onclick="abrirDetalheMedico('${m.cns}')">Mais Informações</button>
                  ${m.colih 
                    ? `<span class="badge" style="background:#10b981; color:#fff; font-size:11px; padding:4px 8px; border-radius:4px; font-weight: 600;">🤝 Cooperador</span>`
                    : m.no_pipeline 
                      ? `<span class="badge" style="background:var(--bg-success); color:#fff; font-size:11px; padding:4px 8px; border-radius:4px;"><i data-lucide="check-circle" style="width:12px; height:12px; display:inline-block; vertical-align:text-bottom;"></i> No Pipeline</span>`
                      : `<button class="btn-primary btn-sm" onclick=\'abrirModalPipeline(${JSON.stringify(m).replace(/"/g,"&quot;").replace(/\'/g,"&apos;")}, "${m.vinculos && m.vinculos[0] ? m.vinculos[0].estabelecimento : ""}")\'>Pipeline</button>`
                  }</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
    ${data.total > 80 ? `<div style="text-align:center; padding:16px; font-size:13px; color:var(--text-muted); border-top:1px solid var(--border-color); margin-top:16px; background:var(--bg-card); border-radius:8px;">
      Exibindo os primeiros <strong>${data.medicos.length}</strong> resultados de um total de <strong>${data.total}</strong>. Utilize os filtros para refinar a busca.
    </div>` : `<div style="text-align:center; padding:16px; font-size:13px; color:var(--text-muted); border-top:1px solid var(--border-color); margin-top:16px; background:var(--bg-card); border-radius:8px;">
      Exibindo <strong>${data.medicos.length}</strong> resultados.
    </div>`}
  `;
  return data.medicos;
  }

window.abrirMedicoDoHospital = function(cns) {
  const btn = document.querySelector('.tab-btn[onclick*="medicos"][onclick*="openTab"]') || document.querySelector('.tab-btn[onclick*="medicos"]');
  if(btn) {
      btn.click();
  } else {
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      document.getElementById('tab-medicos').classList.add('active');
  }
  // Allow DOM to transition
  setTimeout(() => abrirDetalheMedico(cns), 100);
};

async function abrirDetalheMedico(cns) {
  document.getElementById('med-results').innerHTML = '';
  document.getElementById('med-fonte-bar').style.display = 'none';
  const searchBars = document.querySelectorAll('#tab-medicos .search-bar');
  searchBars.forEach(bar => bar.style.display = 'none');
  const detail = document.getElementById('med-detail');
  detail.style.display = 'block';

  document.getElementById('med-detail-title').innerHTML = '<div class="loading-state">Carregando dados do médico...</div>';
  document.getElementById('med-cnes-card').innerHTML = '';
  document.getElementById('med-cfm-card').innerHTML = '';
  document.getElementById('med-curriculo-card').innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-muted); font-size:13px;">🔄 Carregando currículo...</div>';
  document.getElementById('vinculos-table-wrap').innerHTML = '';
  document.getElementById('vinc-fonte-chip').innerHTML = '';
  document.getElementById('captacao-actions-wrap').innerHTML = '';

  const [m, curriculo] = await Promise.all([
    fetchAPI(`/medicos/${cns}`).catch(() => null),
    fetchAPI(`/medicos/${cns}/curriculo`).catch(() => null),
  ]);
  if (!m) return;

  state.medicoSelecionado = m;
  if (m && m.nome) {
    const safeName = m.nome.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    history.pushState({cns: cns, type: 'medico'}, '', '/medicos/' + safeName);
  }
  renderizarDetalheMedico(m);
  renderCurriculoCard(m, curriculo);
}

function abrirDetalheMedicoFromHosp(m) {
  openTab('medicos', document.getElementById('tab-btn-medicos'));
  state.medicoSelecionado = m;

  document.getElementById('med-results').innerHTML = '';
  document.getElementById('med-fonte-bar').style.display = 'none';
  const detail = document.getElementById('med-detail');
  detail.style.display = 'block';
  renderizarDetalheMedico(m);
  // Carrega currículo em background
  if (m.cns) {
    document.getElementById('med-curriculo-card').innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-muted); font-size:13px;">🔄 Carregando currículo...</div>';
    fetchAPI(`/medicos/${m.cns}/curriculo`).then(c => renderCurriculoCard(m, c)).catch(() => renderCurriculoCard(m, null));
  }
}

function fecharDetalheMedico() {
  document.getElementById('med-detail').style.display = 'none';
  const searchBars = document.querySelectorAll('#tab-medicos .search-bar');
  searchBars.forEach(bar => bar.style.display = 'flex');
  document.getElementById('med-results').innerHTML = '';
  state.medicoSelecionado = null;
}

function renderCurriculoCard(m, curriculo) {
  const el = document.getElementById('med-curriculo-card');
  if (!el) return;

  const crm = m.crm || (curriculo?.crm_cnes) || '';
  const crmTipo = m.crm_tipo || 'CRM';
  const crmUf = m.crm_uf || (curriculo?.data?.crm_uf) || '';
  const links = curriculo?.links || curriculo?.data?.links || {};
  const doc = curriculo?.data?.doctoralia || {};
  const lattes = curriculo?.data?.lattes || {};
  const status = curriculo?.status || 'pendente';

  // CRM badge
  const crmBadge = crm
    ? `<span style="background:var(--accent-cyan);color:var(--bg-body);padding:4px 12px;border-radius:6px;font-size:14px;font-weight:800;">${crmTipo} ${crm}</span>`
    : `<span style="color:var(--text-muted);font-size:13px;font-style:italic;">Não encontrado no DATASUS — verifique no CFM</span>`;

  // Doctoralia block
  let docBlock = '';
  if (doc.status === 'encontrado') {
    const rating = doc.avaliacao ? `â˜… ${doc.avaliacao} (${doc.total_avaliacoes || 0} avaliações)` : '';
    const esps = (doc.especialidades_doctoralia || []).join(', ') || '—';
    const consultorios = (doc.consultorios || []).map(c =>
      `<div style="font-size:12px;color:var(--text-secondary);margin-bottom:2px;"> <strong>${c.nome || ''}</strong> â€¢ ${c.endereco || ''}, ${c.cidade || ''} ${c.telefone ? 'Â· ' + c.telefone : ''}</div>`
    ).join('');
    const convenios = (doc.convenios || []).filter(Boolean).slice(0, 6).join(', ');
    const crmDoc = doc.crm_doctoralia ? `<div><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;">CRM (Doctoralia)</label><div style="font-size:13px;font-weight:700;color:var(--accent-green);">${doc.crm_doctoralia}</div></div>` : '';
    docBlock = `
      <div style="border-top:1px solid var(--border-color);margin-top:16px;padding-top:16px;">
        <div style="font-size:12px;font-weight:800;color:var(--accent-purple);text-transform:uppercase;margin-bottom:10px;">🩺 Doctoralia</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
          ${crmDoc}
          ${doc.rqe ? `<div><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;">RQE</label><div style="font-size:13px;font-weight:600;">${doc.rqe}</div></div>` : ''}
          <div style="grid-column:1/-1;"><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;">Especialidades</label><div style="font-size:13px;">${esps}</div></div>
          ${rating ? `<div style="grid-column:1/-1;font-size:13px;color:var(--accent-yellow,#f59e0b);">${rating}</div>` : ''}
        </div>
        ${consultorios ? `<div style="margin-bottom:10px;"><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;display:block;margin-bottom:6px;">Consultórios</label>${consultorios}</div>` : ''}
        ${convenios ? `<div><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;display:block;margin-bottom:4px;">Convênios</label><div style="font-size:12px;color:var(--text-secondary);">${convenios}</div></div>` : ''}
        <a href="${doc.doctoralia_url || links.doctoralia || '#'}" target="_blank" style="display:inline-block;margin-top:12px;font-size:12px;color:var(--accent-cyan);text-decoration:none;font-weight:700;">Ver perfil completo na Doctoralia ↗</a>
      </div>`;
  }

  // Lattes block
  let lattesBlock = '';
  if (lattes.status === 'encontrado') {
    lattesBlock = `
      <div style="border-top:1px solid var(--border-color);margin-top:16px;padding-top:16px;">
        <div style="font-size:12px;font-weight:800;color:var(--accent-blue);text-transform:uppercase;margin-bottom:8px;">🎓 Plataforma Lattes (CNPq)</div>
        <div style="font-size:13px;margin-bottom:6px;">👤 ${lattes.nome_lattes || m.nome}</div>
        <a href="${lattes.lattes_url}" target="_blank" style="font-size:12px;color:var(--accent-cyan);text-decoration:none;font-weight:700;">Abrir Currículo Lattes ↗</a>
      </div>`;
  }

  // Links de busca manual
  const btnStyle = `style="display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none;border:1px solid var(--border-color);color:var(--text-primary);background:var(--bg-body);cursor:pointer;"`;
  const linksHtml = `
    <div style="border-top:1px solid var(--border-color);margin-top:16px;padding-top:16px;">
      <div style="font-size:12px;font-weight:700;color:var(--text-muted);margin-bottom:10px;">🔗 VERIFICAR MANUALMENTE</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">
        ${links.cfm ? `<a href="${links.cfm}" target="_blank" ${btnStyle}> CFM Portal</a>` : ''}
        ${links.cfm_crm ? `<a href="${links.cfm_crm}" target="_blank" ${btnStyle}>🔢 CFM por CRM</a>` : ''}
        ${links.doctoralia ? `<a href="${links.doctoralia}" target="_blank" ${btnStyle}>🩺 Doctoralia</a>` : ''}
        ${links.escavador ? `<a href="${links.escavador}" target="_blank" ${btnStyle}>â–¡ Escavador</a>` : ''}
        ${links.lattes ? `<a href="${links.lattes}" target="_blank" ${btnStyle}>🎓 Lattes</a>` : ''}
        ${links.google_medico ? `<a href="${links.google_medico}" target="_blank" ${btnStyle}>🔍 Google</a>` : ''}
      </div>
      ${status === 'pendente' ? `
        <button onclick="enriquecerMedico('${m.cns}')" style="margin-top:12px;padding:6px 14px;background:var(--accent-purple);color:white;border:none;border-radius:6px;font-size:12px;font-weight:700;cursor:pointer;" id="btn-enriquecer-${m.cns}">
          ⚡ Buscar dados automaticamente (Doctoralia + Lattes)
        </button>` : `
        <button onclick="enriquecerMedico('${m.cns}')" style="margin-top:12px;padding:6px 14px;background:rgba(255,255,255,0.1);color:var(--text-secondary);border:1px dashed var(--border-color);border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;" id="btn-enriquecer-${m.cns}">
          🔄 Tentar buscar dados novamente
        </button>`}
    </div>`;

  el.innerHTML = `
    <h3 style="margin:0 0 16px 0;font-size:16px;font-weight:800;color:var(--text-primary);border-bottom:1px dashed var(--border-color);padding-bottom:12px;">
      📚 Currículo & Registro
    </h3>
    <div>
      <label style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;display:block;margin-bottom:8px;">Registro Profissional (DATASUS)</label>
      ${crmBadge}
    </div>
    ${docBlock}
    ${lattesBlock}
    ${linksHtml}
  `;
}

window.enriquecerMedico = async function(cns) {
  const btn = document.getElementById(`btn-enriquecer-${cns}`);
  if (btn) { btn.disabled = true; btn.textContent = 'â ³ Buscando...'; }
  try {
    await fetch(`${API}/medicos/${cns}/enriquecer`, { method: 'POST' });
    if (btn) btn.textContent = '✅ Iniciado! Aguarde ~30s e recarregue.';
    // Recarrega o card após 35 segundos
    setTimeout(() => abrirDetalheMedico(cns), 35000);
  } catch(e) {
    if (btn) { btn.disabled = false; btn.textContent = '⚡ Tentar novamente'; }
  }
};

function renderizarDetalheMedico(m) {
  const fonte = m.fonte || {};
  const vinculos = m.vinculos || [];
  const noP = m.pipeline;

  let isTmoDoctor = false;
  if (window._tmoCustomData) {
      for (const [cnesId, info] of Object.entries(window._tmoCustomData)) {
          if (info.doctors && info.doctors.some(d => d.cnes_name === m.nome || d.name === m.nome)) {
              isTmoDoctor = true;
              break;
          }
      }
  }

  // Tratamento dos vínculos e hospitais da COLIH
  let hospitaisColih = [];
  if (m.colih && m.colih.hospitais) {
      // Divide por vírgula ou E e limpa
      hospitaisColih = m.colih.hospitais.replace(/ e /gi, ',').split(',').map(s => s.trim()).filter(Boolean);
  }
  
  let vinculosProcessados = vinculos.map(v => {
      let isColih = false;
      let estNome = (v.estabelecimento || '').toLowerCase();
      // Checa se algum hospital colih bate com este estabelecimento
      if (estNome) {
          const match = hospitaisColih.find(hc => estNome.includes(hc.toLowerCase()) || hc.toLowerCase().includes(estNome));
          if (match) {
              isColih = true;
              // Remove da lista para não duplicar
              hospitaisColih = hospitaisColih.filter(h => h !== match);
          }
      }
      return { ...v, isColih };
  });

  // Adiciona os que sobraram da COLIH que não estavam no CNES
  hospitaisColih.forEach(hc => {
      vinculosProcessados.push({
          estabelecimento: hc,
          municipio: '—',
          tipo_unidade: 'Anotado pela COLIH',
          ativo: true,
          isColih: true,
          apenasColih: true
      });
  });

  // Título
  document.getElementById('med-detail-title').innerHTML = `
    <h2 style="font-size:18px;font-weight:800;display:flex;align-items:center;gap:8px;">
        ${m.nome || '—'}
        ${isTmoDoctor ? '<span style="background:#ef4444;color:white;padding:2px 8px;border-radius:12px;font-size:10px;font-weight:bold;text-transform:uppercase;box-shadow:0 2px 4px rgba(239,68,68,0.3);">🔥 Equipe de TMO</span>' : ''}
        ${m.colih ? '<span style="background:#10b981;color:white;padding:2px 8px;border-radius:12px;font-size:10px;font-weight:bold;text-transform:uppercase;box-shadow:0 2px 4px rgba(16,185,129,0.3);">🤝 COLIH</span>' : ''}
    </h2>
    <p style="color:var(--text-secondary);font-size:13px;">${m.especialidade || '—'} · CNS: ${m.cns || '—'}</p>
  `;

  // Telefones COLIH
  let telHtml = '';
  if (m.colih && (m.colih.telefone || m.colih.celular)) {
      telHtml = `<div class="info-item" style="display:flex; flex-direction:column;"><label style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px;">Telefones (COLIH)</label><span style="font-size:14px; font-weight:600; color:var(--accent-purple);">${m.colih.telefone || ''} ${m.colih.celular || ''}</span></div>`;
  }

  // Card CNES
  document.getElementById('med-cnes-card').innerHTML = `
    <h3 style="margin:0 0 16px 0; font-size:18px; font-weight:800; color:var(--text-primary); border-bottom:1px dashed var(--border-color); padding-bottom:12px; display:flex; align-items:center; gap:8px;">
       Dados CNES
    </h3>
    <div class="info-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px;">
      <div class="info-item" style="display:flex; flex-direction:column;"><label style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px;">Nome</label><span style="font-size:14px; font-weight:600;">${m.nome || '—'}</span></div>
      <div class="info-item" style="display:flex; flex-direction:column;"><label style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px;">Especialidade</label><span style="font-size:14px; font-weight:600;">${m.especialidade || '—'}</span></div>
      <div class="info-item" style="display:flex; flex-direction:column;"><label style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px;">CBO</label><span style="font-size:14px; font-weight:600;">${m.cbo || '—'}</span></div>
      <div class="info-item" style="display:flex; flex-direction:column;"><label style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px;">CNS</label><span style="font-size:14px; font-weight:600;">${m.cns || '—'}</span></div>
      ${telHtml}
      <div class="info-item" style="display:flex; flex-direction:column; grid-column: 1 / -1;"><label style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px;">Instituições Ativas</label><span style="font-size:14px; font-weight:600; color:var(--accent-cyan);">${vinculos.filter(v=>v.ativo).length} estabelecimentos no CNES</span></div>
    </div>
    <div style="margin-top:auto; padding-top:16px; border-top:1px solid var(--border-color); font-size:11px; color:var(--text-muted); line-height:1.6;">
      <div style="display:flex; justify-content:space-between;">
        <span><strong>Fonte:</strong> ${fonte.nome || 'DATASUS/CNES'} · Competência: ${fonte.competencia ? `${fonte.competencia.slice(0,4)}/${fonte.competencia.slice(4)}` : '—'}</span>
        <span><strong>Atualizado:</strong> ${fonte.data_atualizacao_fmt || '—'}</span>
      </div>
    </div>
  `;

  // Card CFM
  const crm = m.crm || noP?.crm;
  document.getElementById('med-cfm-card').innerHTML = `
    <h3 style="margin:0 0 16px 0; font-size:18px; font-weight:800; color:var(--text-primary); border-bottom:1px dashed var(--border-color); padding-bottom:12px; display:flex; align-items:center; gap:8px;">
      🔑 Dados CFM
    </h3>
    ${crm ? `
      <div class="info-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
        <div class="info-item" style="display:flex; flex-direction:column;"><label style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px;">CRM</label><span style="font-size:16px; font-weight:800; color:#fff; background:var(--accent-cyan); padding:4px 10px; border-radius:6px; display:inline-block; width:fit-content;">${crm} ${m.crm_uf || 'BA'}</span></div>
        <div class="info-item" style="display:flex; flex-direction:column;"><label style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px;">Situação</label><span style="font-size:14px; font-weight:600; color:${noP?.crm_situacao === 'Regular' ? '#10b981' : (noP?.crm_situacao ? '#ef4444' : 'var(--text-muted)')};">${noP?.crm_situacao || 'Não informada'}</span></div>
      </div>
      <p style="font-size:11px; color:var(--text-muted); margin-top:24px; padding:12px; background:rgba(255,255,255,0.02); border-radius:8px; border:1px solid rgba(255,255,255,0.05);"><i class="fas fa-info-circle"></i> O CRM pode estar vindo do CNES, Currículo Lattes ou Doctoralia.</p>
    ` : `
      <div style="text-align:center; padding:32px 20px; color:var(--text-muted); background:var(--bg-body); border-radius:12px; border:1px dashed var(--border-color);">
        <div style="font-size:32px; margin-bottom:12px; opacity:0.5;">🔍</div>
        <p style="font-size:13px; font-weight:500; line-height:1.5;">O CRM deste médico não está disponível na base CNES.</p>
        <p style="font-size:12px; margin-top:12px;">Consulte no <a href="https://portal.cfm.org.br/busca-medicos/?nome=${encodeURIComponent(m.nome||'')}" target="_blank" style="color:var(--accent-cyan); font-weight:700; text-decoration:none; padding:4px 8px; background:rgba(0,255,136,0.1); border-radius:4px;">Portal CFM</a> e registre no pipeline.</p>
      </div>
      <div style="font-size:10px; color:var(--text-muted); margin-top:16px; text-align:center; opacity:0.6;">Fonte de consulta: portal.cfm.org.br</div>
    `}
  `;

  // Vínculos
  document.getElementById('vinc-fonte-chip').innerHTML = fonteChip(fonte);
  document.getElementById('vinculos-table-wrap').innerHTML = vinculosProcessados.length ? `
    <div class="table-wrap">
      <table>
        <thead><tr><th>Estabelecimento</th><th>Município</th><th>Tipo</th><th>Status</th></tr></thead>
        <tbody>
          ${vinculosProcessados.map(v => `
            <tr>
              <td style="font-weight:600; display:flex; flex-direction:column; gap:4px;">
                ${v.estabelecimento || '—'}
                ${v.isColih ? '<span style="font-size:10px; font-weight:700; color:#10b981; background:rgba(16,185,129,0.1); padding:2px 6px; border-radius:4px; width:fit-content;">✅ Validado COLIH</span>' : ''}
                ${v.apenasColih ? '<span style="font-size:10px; font-weight:700; color:var(--accent-purple); background:rgba(167,139,250,0.1); padding:2px 6px; border-radius:4px; width:fit-content;">📌 Apenas na COLIH (sem CNES)</span>' : ''}
              </td>
              <td class="td-muted">${v.municipio || '—'}</td>
              <td class="td-muted">${v.tipo_unidade || '—'}</td>
              <td>${v.apenasColih ? '<span class="ativo-badge ativo">● Informado</span>' : `<span class="ativo-badge ${v.ativo ? 'ativo' : 'inativo'}">${v.ativo ? '● Ativo' : '○ Inativo'}</span>`}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  ` : '<div class="empty-state"><p>Nenhum vínculo encontrado.</p></div>';

  // Ações de captação
  const wrap = document.getElementById('captacao-actions-wrap');
  if (m.colih && m.colih.observacoes) {
    wrap.innerHTML = `
      <div style="width:100%; text-align:left; font-size:13px; line-height:1.5; padding: 12px; background: rgba(16, 185, 129, 0.05); border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
        <div style="font-weight:600; color:#10b981; font-size:14px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
          🤝 Observações Extras (COLIH)
        </div>
        <div style="color:var(--text-muted);">${m.colih.observacoes}</div>
      </div>
    `;
  } else if (noP) {
    wrap.innerHTML = `
      <span class="action-label">✅ Já está no pipeline</span>
      ${statusLabel(noP.status)}
      <button class="btn-secondary" onclick="abrirModalEditar('${m.cns}')">⚙️ Gerenciar</button>
    `;
  } else if (!m.colih) {
    wrap.innerHTML = `
      <span class="action-label">💡 Adicione este médico ao pipeline para iniciar a captação</span>
      <button class="btn-primary" onclick="abrirModalPipeline(${JSON.stringify(m).replace(/"/g,'&quot;')}, '${(vinculos[0]?.estabelecimento||'').replace(/'/g,"\'")}')">
        ➕ Adicionar ao Pipeline
      </button>
    `;
  } else {
      wrap.innerHTML = ''; // Cooperador sem observações não precisa de nada embaixo.
  }
}

/* ─── WhatsApp ─────────────────────────────────────────────── */
function abrirWhatsApp() {
  const contato = document.getElementById('edit-contato').value.trim();
  const nome = document.getElementById('med-edit-header')?.textContent?.trim() || 'Dr(a).';
  if (!contato) { showToast('⚠️  Informe o telefone primeiro', 'error'); return; }
  const tel = contato.replace(/\D/g, '');
  const msg = encodeURIComponent(
    `Olá, Dr(a). ${nome}! Sou membro da COLIH Salvador (Corpo Humanitário de Socorro Voluntário). ` +
    `Gostaria de apresentar nossa missão e verificar a possibilidade de colaboração voluntária. ` +
    `Podemos conversar sobre isso? Muito obrigado!`
  );
  const num = tel.startsWith('55') ? tel : `55${tel}`;
  window.open(`https://wa.me/${num}?text=${msg}`, '_blank');
}

/* ─── Modal Pipeline (adicionar) ─────────────────────────────── */
function abrirModalPipeline(medico, hospitalPrincipal) {
  document.getElementById('pip-nome').value = medico.nome || '';
  document.getElementById('pip-especialidade').value = medico.especialidade || medico.cbo || '';
  
  const selectHosp = document.getElementById('pip-hospital');
  selectHosp.innerHTML = '';
  
  // Adicionar vinculos do medico
  if(medico.vinculos && medico.vinculos.length > 0) {
      medico.vinculos.forEach(v => {
          if(v.estabelecimento) {
              const opt = document.createElement('option');
              opt.value = v.estabelecimento;
              opt.textContent = v.estabelecimento;
              selectHosp.appendChild(opt);
          }
      });
  }
  
  // Se veio hospitalPrincipal nos params e não tá na lista, a gente põe
  if(hospitalPrincipal) {
      let achou = false;
      for(let i=0; i<selectHosp.options.length; i++) {
          if(selectHosp.options[i].value === hospitalPrincipal) achou = true;
      }
      if(!achou) {
          const opt = document.createElement('option');
          opt.value = hospitalPrincipal;
          opt.textContent = hospitalPrincipal;
          selectHosp.appendChild(opt);
          selectHosp.value = hospitalPrincipal;
      }
  }
  
  // Opção Outro
  const optOutro = document.createElement('option');
  optOutro.value = 'outro';
  optOutro.textContent = 'Outro (Buscar no CNES)...';
  selectHosp.appendChild(optOutro);
  
  verificarHospitalOutro(); // reset state
  
  document.getElementById('pip-cns').value = medico.cns || '';
  document.getElementById('pip-cnes').value = medico.vinculos?.[0]?.cnes || medico.cnes_principal || '';
  document.getElementById('pip-contato').value = '';
  document.getElementById('pip-notas').value = '';
  document.getElementById('pip-responsavel').value = state.usuarioAtivo || '';
  abrirModal('modal-pipeline');
}

async function confirmarPipeline() {
  const cns = document.getElementById('pip-cns').value;
  const body = {
    cns,
    nome: document.getElementById('pip-nome').value,
    especialidade: document.getElementById('pip-especialidade').value,
    vinculo_principal: document.getElementById('pip-hospital').value,
    cnes_principal: document.getElementById('pip-cnes').value,
    responsavel: document.getElementById('pip-responsavel').value,
    contato: document.getElementById('pip-contato').value,
    notas: document.getElementById('pip-notas').value,
  };

  await fetchAPI('/pipeline', { method: 'POST', body: JSON.stringify(body) });
  showToast(`✅ ${body.nome} adicionado ao pipeline!`);
  fecharModal('modal-pipeline');
  await carregarInfo();
  if (state.medicoSelecionado?.cns === cns) abrirDetalheMedico(cns);
}

/* ─── Modal Editar Pipeline ──────────────────────────────────── */
async function abrirModalEditar(cns) {
  state.editandoCns = cns;
  const pipeline = await fetchAPI('/pipeline').catch(() => ({ pipeline: [] }));
  const entrada = pipeline.pipeline.find(p => p.cns === cns);
  if (!entrada) { showToast('Médico não encontrado no pipeline', 'error'); return; }

  // Header
  document.getElementById('edit-med-header').innerHTML = `
    <div>
      <div style="font-size:15px;font-weight:700;">${entrada.nome}</div>
      <div style="font-size:12px;color:var(--text-muted)">${entrada.especialidade || '—'} · CNS ${cns}</div>
    </div>
    <div style="margin-left:auto">${statusLabel(entrada.status)}</div>
  `;

  // Preencher campos
  document.getElementById('edit-cns').value = cns;
  document.getElementById('edit-status').value = entrada.status || 'novo';
  document.getElementById('edit-contato').value = entrada.contato || '';
  document.getElementById('edit-notas').value = entrada.notas || '';
  document.getElementById('edit-crm').value = entrada.crm || '';
  document.getElementById('edit-crm-situacao').value = entrada.crm_situacao || '';
  document.getElementById('edit-responsavel').value = entrada.responsavel || '';

  // Link CFM
  document.getElementById('cfm-search-link').href =
    `https://portal.cfm.org.br/busca-medicos/?nome=${encodeURIComponent(entrada.nome || '')}`;

  // Interações
  renderizarInteracoes(entrada.interacoes || []);

  // Resetar inner tabs
  switchInnerTab('tab-status', document.querySelector('.inner-tab'));
  abrirModal('modal-editar');
}

function renderizarInteracoes(interacoes) {
  const el = document.getElementById('interacoes-lista');
  if (!interacoes.length) {
    el.innerHTML = '<div class="empty-state" style="padding:16px"><p style="font-size:12px">Nenhuma interação registrada ainda.</p></div>';
    return;
  }
  el.innerHTML = [...interacoes].reverse().map(i => `
    <div class="interacao-item">
      <div class="interacao-header">
        <span class="interacao-tipo">${tipoInteracaoLabel(i.tipo)}</span>
        ${i.responsavel ? `<span style="font-size:11px;color:var(--text-muted)">por ${i.responsavel}</span>` : ''}
        <span class="interacao-data">${i.data_fmt || formatDate(i.data)}</span>
      </div>
      <div class="interacao-desc">${i.descricao}</div>
      ${i.resultado ? `<div class="interacao-resultado">→ ${i.resultado}</div>` : ''}
    </div>
  `).join('');
}

async function salvarInteracao() {
  const cns = document.getElementById('edit-cns').value;
  const body = {
    tipo: document.getElementById('int-tipo').value,
    descricao: document.getElementById('int-descricao').value.trim(),
    resultado: document.getElementById('int-resultado').value.trim(),
    responsavel: state.usuarioAtivo,
  };
  if (!body.descricao) { showToast('Descreva a interação', 'error'); return; }

  await fetchAPI(`/pipeline/${cns}/interacao`, { method: 'POST', body: JSON.stringify(body) });
  showToast('✅ Interação registrada!');
  document.getElementById('int-descricao').value = '';
  document.getElementById('int-resultado').value = '';

  // Recarregar interações
  const pipeline = await fetchAPI('/pipeline').catch(() => ({ pipeline: [] }));
  const entrada = pipeline.pipeline.find(p => p.cns === cns);
  renderizarInteracoes(entrada?.interacoes || []);
}

async function salvarEdicaoPipeline() {
  const cns = document.getElementById('edit-cns').value;
  const body = {
    status: document.getElementById('edit-status').value,
    contato: document.getElementById('edit-contato').value,
    notas: document.getElementById('edit-notas').value,
    crm: document.getElementById('edit-crm').value,
    crm_situacao: document.getElementById('edit-crm-situacao').value,
    responsavel: document.getElementById('edit-responsavel').value,
  };
  await fetchAPI(`/pipeline/${cns}`, { method: 'PUT', body: JSON.stringify(body) });
  showToast('✅ Pipeline atualizado!');
  fecharModal('modal-editar');
  carregarPipeline();
  await carregarInfo();
}

async function removerDoPipeline() {
  const cns = document.getElementById('edit-cns').value;
  if (!confirm('Remover este médico do pipeline?')) return;
  await fetchAPI(`/pipeline/${cns}`, { method: 'DELETE' });
  showToast('❌ Removido do pipeline');
  fecharModal('modal-editar');
  carregarPipeline();
  await carregarInfo();
}

/* ─── ABA PIPELINE ───────────────────────────────────────────── */
async function carregarPipeline() {
  const status = document.getElementById('pipe-status-filter').value;
  const resp = document.getElementById('pipe-resp-filter').value;
  const sus = document.getElementById('pipe-sus-filter') ? document.getElementById('pipe-sus-filter').value : '';

  const params = new URLSearchParams();
  if (status) params.set('status', status);
  if (resp) params.set('responsavel', resp);
  if (sus) params.set('atende_sus', sus);

  const data = await fetchAPI(`/pipeline?${params}`).catch(() => ({ pipeline: [], fonte: {} }));
  state.pipelineData = data.pipeline || [];
  state.pipelineFiltered = [...state.pipelineData];

  // Barra de fonte
  const fonteBar = document.getElementById('pipe-fonte-bar');
  fonteBar.style.display = 'flex';
  document.getElementById('pipe-fonte-text').innerHTML = fonteChip(data.fonte)
    + ' · <em style="color:var(--text-muted)">Pipeline salvo localmente no servidor</em>';

  // Summary cards
  const counts = {};
  const statusOrdem = ['novo', 'em_contato', 'aguardando', 'reuniao', 'cooperador', 'recusou'];
  state.pipelineData.forEach(p => { counts[p.status] = (counts[p.status] || 0) + 1; });

  const statusNames = { novo:'Novos', em_contato:'Em Contato', aguardando:'Aguardando', reuniao:'Reunião', cooperador:'Cooperadores', recusou:'Recusaram' };
  const statusColors = { novo:'#3b82f6', em_contato:'#eab308', aguardando:'#f97316', reuniao:'#a855f7', cooperador:'#22c55e', recusou:'#ef4444' };

  document.getElementById('status-summary').innerHTML = statusOrdem.map(s => `
    <div class="summary-card" onclick="filtrarPorStatus('${s}')">
      <div class="summary-num" style="color:${statusColors[s]}">${counts[s] || 0}</div>
      <div class="summary-label">${statusNames[s]}</div>
    </div>
  `).join('');

  document.getElementById('pipeline-count').textContent = state.pipelineData.length;
  renderizarPipeline(state.pipelineFiltered);
}

function filtrarPipelineLocal() {
  const q = document.getElementById('pipe-search').value.toLowerCase();
  state.pipelineFiltered = q
    ? state.pipelineData.filter(p => p.nome?.toLowerCase().includes(q) || p.especialidade?.toLowerCase().includes(q))
    : [...state.pipelineData];
  renderizarPipeline(state.pipelineFiltered);
}

/* ─── REGIÕES SUS ──────────────────────────────────── */
async function carregarRegioes() {
  const container = document.getElementById('regioes-container');
  if (container.innerHTML.trim() !== '') return; // Já carregou

  document.getElementById('regioes-loading').style.display = 'block';
  
  try {
    const response = await fetchAPI('/regioes');
    document.getElementById('regioes-loading').style.display = 'none';
    
    // Agrupar por macrorregião
    const macros = {};
    response.regioes.forEach(regiao => {
      const macro = regiao.macrorregiao.toUpperCase();
      if (!macros[macro]) macros[macro] = [];
      macros[macro].push(regiao);
    });
    
    let html = '';
    
    for (const [macro, regioes] of Object.entries(macros)) {
      html += `
        <div style="grid-column: 1 / -1; margin-top: 32px; padding-bottom: 12px; border-bottom: 2px solid var(--accent-cyan);">
          <h2 style="margin: 0; font-size: 20px; font-weight: 800; color: var(--accent-cyan); display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-map"></i> MACRORREGIÃO: ${macro}
          </h2>
        </div>
      `;
      
      regioes.forEach(regiao => {
        const bairrosHtml = regiao.bairros.map(b => `<div class="bairro-tag">${b}</div>`).join('');
        html += `
          <div class="info-card region-card" style="display:flex; flex-direction:column; justify-content:space-between;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom:1px dashed var(--border-color); padding-bottom:16px; margin-bottom:16px;">
              <div>
                <h2 style="margin:0 0 4px 0; font-size:18px; font-weight:800; color:var(--text-primary); display:flex; align-items:center; gap:6px;">
                   DS: ${regiao.distrito_sanitario}
                </h2>
              </div>
              <div style="background:var(--bg-body); border:1px solid var(--border-color); padding:4px 10px; border-radius:8px; font-size:11px; font-weight:800; color:var(--text-secondary);">
                ${regiao.bairros.length} BAIRROS
              </div>
            </div>
            <div style="flex-grow:1;">
              <p style="font-size:13px; color:var(--text-secondary); margin:0; font-weight:600;">Bairros Abrangidos:</p>
              <div class="bairros-grid" style="display:flex; flex-wrap:wrap; gap:8px; margin-top:12px;">
                ${bairrosHtml}
              </div>
            </div>
          </div>
        `;
      });
    }
    
    // Adicionar estilos inline que estavam na antiga pagina
    if (!document.getElementById('regiao-style')) {
      const style = document.createElement('style');
      style.id = 'regiao-style';
      style.textContent = `
        .bairro-tag { background:var(--bg-body); border:1px solid var(--border-color); padding:6px 12px; border-radius:16px; font-size:12px; font-weight:700; color:var(--text-secondary); transition:all 0.2s; }
        .bairro-tag:hover { background:var(--accent-cyan); color:#fff; border-color:var(--accent-cyan); }
        .region-card { transition: transform 0.3s ease, border-color 0.3s ease; border: 1px solid var(--border-color); }
        .region-card:hover { transform: translateY(-3px); border-color: var(--accent-cyan); }
      `;
      document.head.appendChild(style);
      
      container.style.display = 'grid';
      container.style.gridTemplateColumns = 'repeat(auto-fill, minmax(350px, 1fr))';
      container.style.gap = '24px';
    }
    
    container.innerHTML = html;
  } catch (error) {
    document.getElementById('regioes-loading').innerHTML = '<span style="color:var(--status-falha);">Erro ao carregar dados.</span>';
    console.error(error);
  }
}

// Init inicial — carrega status da sincronização imediatamente
fetchSyncStatus();

function filtrarPorStatus(s) {
  document.getElementById('pipe-status-filter').value = s;
  carregarPipeline();
}

function renderizarPipeline(lista) {
  const el = document.getElementById('pipeline-table-wrap');
  if (!lista.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><p>Nenhum médico no pipeline.</p></div>';
    return;
  }

  el.innerHTML = `
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Nome</th>
          <th>Especialidade</th>
          <th>Hospital</th>
          <th>Status</th>
          <th>Responsável</th>
          <th>Contato</th>
          <th>Últ. Contato</th>
          <th>Interações</th>
          <th>Ações</th>
        </tr></thead>
        <tbody>
          ${lista.map(p => `
            <tr>
              <td style="font-weight:600">${p.nome || '—'}</td>
              <td class="td-muted">${p.especialidade || '—'}</td>
<td class="td-muted" style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                <div title="${p.vinculo_principal||''}">${p.vinculo_principal || '—'}</div>
                ${p.atende_sus === 'Sim' ? `<span title="Hospitais SUS:\n${(p.hospitais_sus||[]).join('\n')}" style="display:inline-block; margin-top:4px; font-size:10px; background:rgba(34, 197, 94, 0.1); color:#22c55e; padding:2px 6px; border-radius:4px; cursor:help; border:1px solid rgba(34, 197, 94, 0.2); font-weight:600;">SUS: Sim</span>` : ''}
              </td>\n              <td>${statusLabel(p.status)}</td>
              <td class="td-muted">${p.responsavel || '—'}</td>
              <td>
                ${p.contato
                  ? `<div style="display:flex;gap:6px;align-items:center;">
                      <span style="font-size:12px">${p.contato}</span>
                      <button class="btn-whatsapp" style="padding:4px 8px;font-size:11px"
                        onclick="abrirWhatsAppDireto('${p.contato}','${(p.nome||'').replace(/'/g,"'")}')">
                        💬
                      </button>
                    </div>`
                  : '<span class="td-muted">—</span>'}
              </td>
              <td class="td-muted" style="font-size:11px">${p.data_ultimo_contato ? formatDate(p.data_ultimo_contato) : '—'}</td>
              <td style="text-align:center">${(p.interacoes||[]).length}</td>
              <td class="td-actions">
                <button class="btn-secondary btn-sm" onclick="abrirModalEditar('${p.cns}')">✏️ Gerenciar</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function abrirWhatsAppDireto(contato, nome) {
  const tel = contato.replace(/\D/g, '');
  const msg = encodeURIComponent(
    `Olá, Dr(a). ${nome}! Sou membro da COLIH Salvador. Gostaria de conversar sobre uma possibilidade de colaboração voluntária. Podemos falar?`
  );
  const num = tel.startsWith('55') ? tel : `55${tel}`;
  window.open(`https://wa.me/${num}?text=${msg}`, '_blank');
}

/* ─── Exportar CSV ───────────────────────────────────────────── */
function exportarCSV() {
  const data = state.pipelineFiltered;
  if (!data.length) { showToast('Pipeline vazio', 'error'); return; }

  const headers = ['Nome','Especialidade','Hospital','Status','Responsável','Contato','CRM','Notas','Últ. Contato','Data Adição'];
  const rows = data.map(p => [
    p.nome || '',
    p.especialidade || '',
    p.vinculo_principal || '',
    p.status || '',
    p.responsavel || '',
    p.contato || '',
    p.crm || '',
    (p.notas || '').replace(/\n/g, ' '),
    p.data_ultimo_contato ? formatDate(p.data_ultimo_contato) : '',
    p.data_adicao ? formatDate(p.data_adicao) : '',
  ]);

  const csv = [headers, ...rows].map(r => r.map(c => `"${c}"`).join(',')).join('\n');
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url;
  a.download = `colih_pipeline_${new Date().toISOString().slice(0,10)}.csv`;
  a.click(); URL.revokeObjectURL(url);
  showToast('⬇️ CSV exportado!');
}

/* 📊 ABA ESTATÍSTICAS */
async function carregarEstatisticas() {
    renderDashboardGamificacao();
}

/* ─── Init ──────────────────────────────────────────────────── */
async function init() {
  if(window.lucide) window.lucide.createIcons();
  await carregarPipeline();
  await carregarInfo();
  await carregarUsuarios();
  await carregarEspecialidades();
}

document.addEventListener('DOMContentLoaded', init);

// ==========================================
// STATUS DO SERVIDOR E SINCRONIZAÇÃO
// ==========================================

async function fetchSyncStatus() {
    try {
        const res = await fetch(`${API}/status`);
        if (!res.ok) throw new Error("Erro ao buscar status");
        
        const status = await res.json();
        const dot = document.getElementById("cnesStatusDot");
        const details = document.getElementById("syncStatusDetails");
        const text = document.getElementById("modal-cnes-status");
        const compactText = document.getElementById("cnesStatusCompact");
        
        let headerColor = "#aaa";
        let headerText = "Lendo base do MS...";
        
        if (status.status_geral === "verificando") {
            headerColor = "#ffaa00"; // Laranja
            headerText = "Lendo base do MS...";
            
            let etaStr = "";
            if (status.eta) {
                etaStr = " (ETA: " + status.eta + ")";
            }

            if (status.progresso !== undefined && status.progresso !== null) {
                headerText += ` (${status.progresso}%)`;
                text.innerHTML = `Sincronizando: <span style="color:#ffaa00; font-weight:bold;">${status.progresso}%</span> <span style="color:#aaa; font-size:12px;">${etaStr}</span>`; if(compactText) compactText.innerText = `${status.progresso}%`;
            } else {
                text.innerText = "Lendo base do MS..."; if(compactText) compactText.innerText = "Lendo...";
            }
        } else if (status.status_geral === "sucesso") {
            headerColor = "#00ff88"; // Verde
            headerText = `Base Atualizada (${status.data_fmt})`;
            text.innerText = `Atualizado`;
            if(compactText) {
                compactText.textContent = "Online";
                compactText.style.color = "#00ff88";
            }
            if(dot) {
                dot.style.background = "#00ff88";
                dot.style.boxShadow = "0 0 5px #00ff88";
            }
            const dt = document.getElementById("cnesDataUltima");
            if(dt) dt.textContent = status.data_fmt || "desconhecido";
        } else {
            headerColor = "#ff3366"; // Vermelho
            headerText = "Falha Total na Sincronização";
            text.innerText = "Erro de Sync"; if(compactText) compactText.innerText = "Erro";
        }
        
        dot.style.background = headerColor;
        dot.style.boxShadow = `0 0 8px ${headerColor}`;

        let html = `
            <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <strong>Última Tentativa:</strong> ${status.data_fmt || 'Nunca'}<br>
                <strong>Competência (Governo):</strong> ${status.competencia || 'Desconhecida'}
                ${status.url_fonte ? `<br><strong>Fonte:</strong> <a href="${status.url_fonte}" target="_blank" style="color: #4da6ff; text-decoration: none; word-break: break-all;">${status.url_fonte}</a>` : ''}
            </div>`;
            
        if (status.status_geral === "verificando" && status.progresso !== undefined && status.progresso !== null) {
            let modalEta = "";
            if (status.eta) {
                modalEta = `<span style="margin-left:10px; font-size:12px; color:#aaa;">(Restam: ${status.eta})</span>`;
            }
            html += `
            <div style="margin-bottom: 15px; padding: 15px; background: rgba(255,170,0,0.05); border-radius: 8px; border: 1px solid rgba(255,170,0,0.2);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <strong style="color: #ccc; font-size: 0.95rem;"><i class="fas fa-database"></i> Lendo base do MS...</strong>
                    <strong style="color: #ffaa00; font-size: 1rem;">${status.progresso}%${modalEta}</strong>
                </div>
                <div style="width: 100%; height: 10px; background: rgba(255,255,255,0.05); border-radius: 5px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);">
                    <div style="width: ${status.progresso}%; height: 100%; background: linear-gradient(90deg, #f59e0b, #fbbf24); transition: width 0.3s ease; border-radius: 5px;"></div>
                </div>
                <div style="margin-top: 12px; font-family: monospace; font-size: 0.85rem; color: #aaa; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 6px; white-space: pre-wrap; word-break: break-all;">${status.detalhes || "Conectando aos servidores..."}</div>
            </div>`;
        }
            
        html += `
            <strong>Status dos Servidores do Governo:</strong>
            <div style="margin-top: 10px; display: flex; flex-direction: column; gap: 10px;">
        `;
        
        if (status.planos && status.planos.length > 0) {
            status.planos.forEach(p => {
                let icon = '<i class="fas fa-clock" style="color:#666"></i>';
                let pColor = "#aaa";
                let erroHtml = '';
                
                if (p.status === "processando") {
                    icon = '<i class="fas fa-circle-notch fa-spin" style="color:#ffaa00"></i>';
                    pColor = "#ffaa00";
                } else if (p.status === "sucesso") {
                    icon = '<i class="fas fa-check-circle" style="color:#00ff88"></i>';
                    pColor = "#00ff88";
                } else if (p.status === "falha") {
                    icon = '<i class="fas fa-times-circle" style="color:#ff3366"></i>';
                    pColor = "#ff3366";
                    if (p.erro) erroHtml = `<div style="font-size: 0.8rem; color: #ff3366; margin-left: 24px; margin-top: 2px;">${p.erro}</div>`;
                }
                
                html += `
                    <div style="background: rgba(255,255,255,0.05); padding: 10px 15px; border-radius: 6px; border-left: 3px solid ${pColor};">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            ${icon} <strong style="color: ${pColor}">${p.nome}</strong>
                        </div>
                        ${erroHtml}
                    </div>
                `;
            });
        }
        
        html += `</div>`;
        
        if (status.status_geral === "falha_total" && status.erro_geral) {
            html += `
                <div style="margin-top: 15px; padding: 10px; background: rgba(255,51,102,0.1); border: 1px solid rgba(255,51,102,0.3); border-radius: 6px; color: #ff3366;">
                    <strong><i class="fas fa-exclamation-triangle"></i> Falha Geral:</strong> ${status.erro_geral}
                </div>
            `;
        }
        
        if (status.proxima_tentativa) {
            html += `
                <div style="margin-top: 15px; font-size: 0.9rem; color: #aaa; text-align: center;">
                    <i class="fas fa-history"></i> Próxima tentativa automática: <strong>${status.proxima_tentativa}</strong>
                </div>
            `;
        }
        
        details.innerHTML = html;
        return status;
        
    } catch (e) {
        console.error("Erro status:", e);
        if(document.getElementById("modal-cnes-status")) document.getElementById("modal-cnes-status").innerText = "Indisponível";
        if(document.getElementById("cnesStatusCompact")) document.getElementById("cnesStatusCompact").innerText = "Offline";
        return null;
    }
}

let syncPollInterval = null;

async function forceSyncUpdate() {
    const btn = document.getElementById("btnForceSync");
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Iniciando...';
    
    try {
        const res = await fetch(`${API}/sync`, { method: 'POST' });
        if (res.ok) {
            showToast("Sincronização iniciada. Acompanhe o progresso em tempo real.", "success");
            
            btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Processando...';
            if (syncPollInterval) clearInterval(syncPollInterval);
            
            syncPollInterval = setInterval(async () => {
                const status = await fetchSyncStatus();
                if (status && status.status_geral !== "verificando") {
                    clearInterval(syncPollInterval);
                    syncPollInterval = setInterval(fetchSyncStatus, 60000);
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-sync-alt"></i> Forçar Atualização';
                    
                    // Se deu sucesso, fecha o popup automaticamente e recarrega os dados
                    if (status.status_geral === "sucesso") {
                    // Update CNES UI
                    compactText.textContent = "Online";
                    compactText.style.color = "#00ff88";
                    dot.style.background = "#00ff88";
                    dot.style.boxShadow = "0 0 5px #00ff88";
                    const dt = document.getElementById("cnesDataUltima");
                    if(dt) dt.textContent = "Atualizado em " + (status.data_fmt || "desconhecido");

                    setTimeout(() => {
                        document.getElementById('syncStatusModal').style.display = 'none';
                            carregarInfo();
                            buscarHospitais(); // Auto-carrega hospitais
                            buscarMedicos(); // Auto-carrega medicos
                        }, 1500);
                    }
                }
            }, 1500);
            
        } else {
            throw new Error();
        }
    } catch (e) {
        showToast("Erro ao iniciar sincronização", "error");
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Forçar Atualização';
    }
}

async function importarZipLocal() {
    const caminho = document.getElementById('importZipPath').value.trim();
    if (!caminho) {
        showToast('Cole o caminho do arquivo ZIP primeiro!', 'error');
        return;
    }
    try {
        const res = await fetch(`${API}/sync/importar-zip`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ caminho })
        });
        const data = await res.json();
        if (data.ok === false) { showToast(`Erro: ${data.erro}`, 'error'); return; }
        showToast('Processando o ZIP — acompanhe o status!', 'success');
        document.getElementById('importZipPanel').style.display = 'none';
        if (syncPollInterval) clearInterval(syncPollInterval);
        syncPollInterval = setInterval(async () => {
            const status = await fetchSyncStatus();
            if (status && status.status_geral !== 'verificando') {
                clearInterval(syncPollInterval);
                syncPollInterval = setInterval(fetchSyncStatus, 60000);
                if (status.status_geral === 'sucesso') {
                    // Update CNES UI
                    const compactText = document.getElementById("cnesStatusCompact");
                    const dot = document.getElementById("cnesStatusDot");
                    if(compactText) {
                        compactText.textContent = "Online";
                        compactText.style.color = "#00ff88";
                    }
                    if(dot) {
                        dot.style.background = "#00ff88";
                        dot.style.boxShadow = "0 0 5px #00ff88";
                    }
                    const dt = document.getElementById("cnesDataUltima");
                    if(dt) dt.textContent = "Atualizado em " + (status.data_fmt || "desconhecido");

                    setTimeout(() => {
                        document.getElementById('syncStatusModal').style.display = 'none';
                        carregarInfo(); buscarHospitais(); buscarMedicos();
                    }, 1500);
                }
            }
        }, 2000);
    } catch (e) { showToast('Erro ao conectar com o servidor', 'error'); }
}


document.addEventListener("DOMContentLoaded", () => {
    carregarUsuarios();
    carregarInfo();
    carregarEspecialidades();
    carregarMapeamento();
    carregarGeoConfig();
    fetchSyncStatus();
    syncPollInterval = setInterval(fetchSyncStatus, 60000);
    
    // Auto buscar listas
    setTimeout(() => {
        buscarHospitais();
        buscarMedicos();
    }, 500);
});

window.switchTab = function(tabId, btn) {
  // Remove active from all buttons and tabs inside the modal
  const modal = btn.closest('.detail-body');
  if (!modal) return;
  modal.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  modal.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  
  // Add active to selected
  btn.classList.add('active');
  const targetTab = document.getElementById(tabId);
  if (targetTab) targetTab.classList.add('active');
};

async function carregarMapeamento() {
  const container = document.getElementById('mapeamento-lista');
  if (!container) return;
  
  try {
    const data = await fetchAPI('/mapeamento');
    if (!data || Object.keys(data).length === 0) {
      container.innerHTML = '<div style="grid-column: span 2; text-align:center; color:var(--text-muted)">Nenhum mapeamento encontrado.</div>';
      return;
    }
    
    // Sort keys alphabetically
    const keys = Object.keys(data).sort();
    
    let html = '';
    for (const k of keys) {
      html += `
        <div style="background:var(--bg-card); padding:10px; border-radius:6px; border:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
          <span style="font-weight:600; font-size:13px; color:var(--text-primary)">${k}</span>
          <span style="color:var(--text-muted); font-size:12px;">→</span>
          <span style="background:var(--accent-purple); color:white; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:bold;">${data[k]}</span>
        </div>
      `;
    }
    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = '<div style="grid-column: span 2; text-align:center; color:var(--text-danger)">Erro ao carregar dicionário.</div>';
  }
}

function filtrarMedicosPorEspecialidade(especialidade) {
  if (!window._hospMedicos) return;
  const btn = document.querySelector(`button[onclick="switchTab('tab-hosp-prof', this)"]`);
  if (btn) openTab('hosp-prof', btn);
  const inputFiltro = document.getElementById('hosp-prof-filter');
  if (inputFiltro) {
      inputFiltro.value = especialidade;
      const event = new Event('input');
      inputFiltro.dispatchEvent(event);
  }
}

window.editPBMLink = async function(cnesId) {
    const link = prompt("Insira a nova URL do PBM:");
    if (link === null) return;
    try {
        const res = await fetch(`${window.API || '/api'}/hospitais/${cnesId}/pbm`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({pbm: true, link: link})
        });
        if(res.ok) {
            alert('Link do PBM atualizado!');
            buscarHospitais().then((results) => {
                const updated = results.find(h => (h.cnes || h.id) === cnesId);
                if (updated) abrirDetalheHospital(cnesId, updated);
            });
        }
    } catch(e) {
        console.error(e);
        alert('Erro ao atualizar PBM.');
    }
};

window.togglePBM = async function(cnesId, currentStatus) {
    const newStatus = !currentStatus;
    let link = "";
    if (newStatus) {
        link = prompt("Insira a URL da notícia ou site oficial que comprova a implantação do PBM (opcional):", "");
        if (link === null) return; // User cancelled
    }
    try {
        const res = await fetch(`/api/hospitais/${cnesId}/pbm`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({pbm: newStatus, link: link || ""})
        });
        if(res.ok) {
            alert(newStatus ? 'PBM marcado como Implantado!' : 'PBM desmarcado.');
            buscarHospitais().then((results) => {
                const updated = results.find(h => (h.cnes || h.id) === cnesId);
                if (updated) abrirDetalheHospital(cnesId, updated);
            });
        }
    } catch(e) {
        console.error(e);
        alert('Erro ao atualizar PBM.');
    }
};


window.abrirModalAddMedicoTmo = function(cnesId) {
    if (!window._hospMedicos || window._hospMedicos.length === 0) {
        alert('Carregue a aba de médicos primeiro para ter as opções disponíveis.');
        return;
    }
    
    let modal = document.getElementById('modal-tmo-add');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-tmo-add';
        modal.className = 'modal';
        modal.innerHTML = `
        <div class="modal-content" style="max-width: 400px; padding: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px;">
                <h3 style="margin:0; font-size:16px; color:#ef4444;">Adicionar Equipe TMO</h3>
                <span style="cursor:pointer; font-size:20px; color:#aaa;" onclick="document.getElementById('modal-tmo-add').classList.remove('open')">&times;</span>
            </div>
            <p style="font-size:12px; color:var(--text-secondary); margin-bottom:15px;">Selecione um médico que possui vínculo na base CNES para este hospital e insira opcionalmente o link do perfil dele.</p>
            
            <label style="font-size:12px; font-weight:bold; margin-bottom:4px; display:block;">Médico (Base CNES):</label>
            <select id="tmo-add-medico-select" style="width:100%; padding:8px; border:1px solid var(--border); border-radius:4px; margin-bottom:12px; font-size:12px; background:var(--bg-body); color:var(--text-primary);"></select>
            
            <label style="font-size:12px; font-weight:bold; margin-bottom:4px; display:block;">Link do Perfil (Site Oficial / Escavador):</label>
            <input type="text" id="tmo-add-link" placeholder="https://..." style="width:100%; padding:8px; border:1px solid var(--border); border-radius:4px; margin-bottom:16px; font-size:12px; background:var(--bg-body); color:var(--text-primary);">
            
            <button id="btn-save-tmo" style="width:100%; padding:10px; background:#ef4444; color:white; border:none; border-radius:6px; cursor:pointer; font-weight:bold; font-size:14px;">💾 Salvar na Equipe TMO</button>
        </div>
        `;
        document.body.appendChild(modal);
    }
    
    const sel = document.getElementById('tmo-add-medico-select');
    sel.innerHTML = '<option value="">-- Selecione o Médico --</option>';
    
    const sortedMedicos = [...window._hospMedicos].sort((a,b) => a.nome.localeCompare(b.nome));
    sortedMedicos.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.nome;
        opt.textContent = m.nome;
        sel.appendChild(opt);
    });
    
    document.getElementById('tmo-add-link').value = '';
    
    document.getElementById('btn-save-tmo').onclick = async function() {
        const docName = sel.value;
        const link = document.getElementById('tmo-add-link').value;
        
        if (!docName) {
            alert('Por favor, selecione um médico.');
            return;
        }
        
        this.disabled = true;
        this.textContent = 'Salvando...';
        
        try {
            const res = await fetch('/api/tmo/' + cnesId + '/medico', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: docName, link: link})
            });
            if (res.ok) {
                await carregarTmoCustom();
                alert('Médico adicionado à equipe TMO com sucesso!');
                document.getElementById('modal-tmo-add').classList.remove('open');
                if (document.getElementById('tab-hosp-info').classList.contains('active')) {
                    fecharModal('modal-hospital');
                }
            } else {
                throw new Error('Erro no backend');
            }
        } catch (e) {
            console.error(e);
            alert('Erro ao salvar.');
        } finally {
            this.disabled = false;
            this.textContent = '💾 Salvar na Equipe TMO';
        }
    };
    
    modal.classList.add('open');
};

// SPA Routing Initialization
window.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    if (path.startsWith('/instituicoes/')) {
        const namePart = path.split('/instituicoes/')[1];
        if (namePart) {
            // Find hospital by name
            openTab('hospitais', document.getElementById('tab-btn-hospitais'));
            document.getElementById('filter-nome').value = namePart.replace(/-/g, ' ');
            buscarHospitais().then((results) => {
                const firstResult = results && results[0];
                if (firstResult) abrirDetalheHospital(firstResult.cnes || firstResult.id, firstResult);
            });
        }
    } else if (path.startsWith('/medicos/')) {
        const namePart = path.split('/medicos/')[1];
        if (namePart) {
            openTab('medicos', document.getElementById('tab-btn-medicos'));
            document.getElementById('med-nome-input').value = namePart.replace(/-/g, ' ');
            buscarMedicos().then((results) => {
                const firstResult = results && results[0];
                if (firstResult) {
                    abrirDetalheMedico(firstResult.cns);
                }
            });
        }
    }
});

window.addEventListener('popstate', (e) => {
    if (e.state) {
        if (e.state.type === 'hospital') {
            openTab('hospitais', document.getElementById('tab-btn-hospitais'));
            // Try to re-open if data exists
            const hosp = state.hospitaisExibidos?.find(h => h.cnes === e.state.cnesId);
            if(hosp) abrirDetalheHospital(hosp.cnes, hosp);
        } else if (e.state.type === 'medico') {
            openTab('medicos', document.getElementById('tab-btn-medicos'));
            abrirDetalheMedico(e.state.cns);
        }
    } else {
        // Root path
        fecharDetalheMedico();
    }
});


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
    popularFiltrosColih();
    renderDashboardGamificacao();
  } catch (e) {
    console.error('Erro ao carregar COLIH', e);
  }
}

function renderColihMedicos() {
    const term = (document.getElementById('busca-colih-medico')?.value || '').toLowerCase();
    const espFiltro = (document.getElementById('filtro-colih-especialidade')?.value || '').toLowerCase();
    const visitaFiltro = (document.getElementById('filtro-colih-visita')?.value || '');
    
    const grid = document.getElementById('colih-medicos-grid');
    if (!grid) return;
    
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
    
    const filtered = colihMedicosCache.filter(m => {
        const esp1 = (m.especialidade_1_colih || '').toLowerCase();
        const esp2 = (m.especialidade_2_colih || '').toLowerCase();
        const esp3 = (m.especialidade_3_colih || '').toLowerCase();
        const esp4 = (m.especialidade_4_colih || '').toLowerCase();
        
        const textMatch = (m.nome || '').toLowerCase().includes(term) || 
                          esp1.includes(term) || esp2.includes(term) || 
                          esp3.includes(term) || esp4.includes(term);
                          
        const espMatch = !espFiltro || esp1 === espFiltro || esp2 === espFiltro || 
                         esp3 === espFiltro || esp4 === espFiltro;
        
        let visitMatch = true;
        let isDefasado = false;
        
        if (m.ultima_visita) {
            const visitDate = new Date(m.ultima_visita.replace(' ', 'T'));
            if (!isNaN(visitDate)) {
                if (visitDate < sixMonthsAgo) isDefasado = true;
            } else {
                isDefasado = true; // Data inválida considera antigo
            }
        } else {
            isDefasado = true; // Sem data considera antigo
        }
        m._isDefasado = isDefasado;
        
        if (visitaFiltro === 'recentes') visitMatch = !isDefasado;
        if (visitaFiltro === 'antigos') visitMatch = isDefasado;
        
        return textMatch && espMatch && visitMatch;
    });
    
    const countEl = document.getElementById('colih-medicos-count');
    if(countEl) countEl.innerText = `${filtered.length} médico(s) encontrado(s)`;
    
    grid.innerHTML = filtered.map(m => {
        const borderCol = m._isDefasado ? '#ef4444' : '#10b981';
        const bgCol = m._isDefasado ? 'rgba(239,68,68,0.05)' : 'var(--bg-card)';
        
        return `
        <div class="medico-card" style="border-left: 4px solid ${borderCol}; padding: 16px; background: ${bgCol}; border-radius: 8px; border-right: 1px solid var(--border-color); border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="font-weight:700; font-size:16px; color:var(--text-primary); margin-bottom:4px;">${m.nome}</div>
            <div style="font-size:13px; color:var(--text-muted); margin-bottom:8px;">${m.especialidade_1_colih || ''} ${m.especialidade_2_colih ? ' / ' + m.especialidade_2_colih : ''}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Colaboração:</strong> ${m.colaboracao || '-'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Membro Resp:</strong> ${m.membro_resp || '-'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Celular:</strong> ${m.celular || '-'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Atende SUS:</strong> ${m.atende_sus || '-'}</div>
            <div style="font-size:12px; color:${m._isDefasado ? '#ef4444' : 'var(--text-muted)'}; margin-top:8px; font-weight:${m._isDefasado ? 'bold' : 'normal'};"><em>Última visita: ${m.ultima_visita || 'Nunca'} ${m._isDefasado ? ' (Mais de 6 meses)' : ''}</em></div>
        </div>
    `}).join('');
}


function renderColihMembros() {
    const container = document.getElementById('colih-membros-list');
    const source = colihMembrosCache || [];
    
    const term = (document.getElementById('busca-colih-membro')?.value || '').toLowerCase();
    const regiaoFiltro = (document.getElementById('filtro-colih-regiao')?.value || '').toLowerCase();
    const geoFiltro = (document.getElementById('filtro-colih-geo')?.value || '');
    
    const grid = document.getElementById('colih-membros-grid');
    if (!grid) return;
    
    // Add Coordinates Alert
    let pendingCoords = 0;
    const pendingNames = [];
    source.forEach(m => {
        if (!m.lat || !m.lon || isNaN(m.lat) || isNaN(m.lon) || (m.lat === 0 && m.lon === 0)) {
            pendingCoords++;
            if (pendingNames.length < 15) pendingNames.push(m.nome);
        }
    });
    
    let alertHtml = '';
    if (pendingCoords > 0) {
        const others = pendingCoords > 15 ? `... e mais ${pendingCoords - 15} membros` : '';
        alertHtml = `
        <div style="background:rgba(245,158,11,0.1); border-left:4px solid #f59e0b; padding:12px; border-radius:4px; margin-bottom:16px;">
            <div style="display:flex; align-items:center; color:#b45309; font-weight:700; margin-bottom:4px;">
                <i data-lucide="alert-triangle" style="margin-right:8px; width:16px; height:16px;"></i> ${pendingCoords} Membros com Coordenadas Pendentes
            </div>
            <div style="font-size:12px; color:#92400e; margin-left:24px;">
                Os seguintes membros precisam ter seus endereços atualizados no sistema e coordenadas salvas (lat/lng) para aparecerem no mapa: <br/>
                <strong>${pendingNames.join(', ')}${others}</strong>
            </div>
        </div>`;
    }
    
    const filtered = source.filter(m => {
        const textMatch = (m.nome || '').toLowerCase().includes(term) || (m.funcao || '').toLowerCase().includes(term);
        const regiaoMatch = !regiaoFiltro || (m.regiao || '').toLowerCase() === regiaoFiltro;
        
        const hasCoords = m.lat && m.lon;
        let geoMatch = true;
        if (geoFiltro === 'validada') geoMatch = hasCoords;
        if (geoFiltro === 'pendente') geoMatch = !hasCoords;
        
        return textMatch && regiaoMatch && geoMatch;
    });
    const countEl = document.getElementById('colih-membros-results-count');
    if (countEl) countEl.innerText = `${filtered.length} membro(s) encontrado(s)`;
    
    if (alertHtml) {
        alertHtml = `<div style="grid-column: 1 / -1;">${alertHtml}</div>`;
    }
    
    grid.innerHTML = alertHtml + filtered.map(m => {
        const hasCoords = m.lat && m.lon;
        const borderStyle = hasCoords ? 'border-left: 4px solid #3b82f6;' : 'border-left: 4px solid #ef4444; background: rgba(239,68,68,0.05);';
            let telHtml = '-';
            if (m.telefone) {
                const numOnly = m.telefone.replace(/\D/g, '');
                telHtml = `<a href="https://wa.me/55${numOnly}" target="_blank" style="color:#10b981; text-decoration:none; display:inline-flex; align-items:center; gap:4px;" title="Chamar no WhatsApp">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                    ${m.telefone}
                </a>`;
            }
            
            return `
        <div class="medico-card" style="${borderStyle} padding: 16px; border-radius: 8px; border-right: 1px solid var(--border-color); border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div style="font-weight:700; font-size:16px; color:var(--text-primary); margin-bottom:4px;">${m.nome}</div>
                    <div style="font-size:13px; color:var(--accent-blue); font-weight:600; margin-bottom:2px;">${m.funcao || 'Membro'}</div>
                    <div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">Região: ${m.regiao || 'Não definida'}</div>
                </div>
                <button onclick="abrirModalCoords(${m.id})" style="background:var(--bg-input); border:1px solid var(--border-color); color:var(--text-primary); padding:6px 10px; border-radius:6px; cursor:pointer; font-size:12px; display:flex; align-items:center; gap:4px;">
                    📍  Editar
                </button>
            </div>
            
            <div style="font-size:12px; margin-bottom:4px; display:flex; align-items:center; gap:4px;"><strong>Telefone:</strong> ${telHtml}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Hospital:</strong> ${m.hospital || '-'}</div>
            <div style="font-size:12px; margin-top:8px;">
                <strong>Geolocalização:</strong> 
                ${hasCoords ? '<span style="color:#10b981; font-weight:600;">Validada</span>' : '<span style="color:#ef4444; font-weight:bold;">Pendente</span>'}
            </div>
            <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">${m.endereco_atual || 'Sem endereço registrado'}</div>
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
    document.getElementById('syncColihPreviewArea').style.display = 'none';
    
    try {
        if(doCnes) {
            await fetchAPI('/sync', { method: 'POST' });
            alert('Sincronização CNES iniciada em segundo plano.');
        }
        
        if(doColih) {
            document.getElementById('btnForceSync').innerHTML = 'Gerando Preview COLIH...';
            const res = await fetchAPI('/colih/sync?action=preview', { method: 'POST' });
            if (res && res.preview_ready) {
                // Show Preview
                const diff = res.diff;
                let diffHtml = `<strong>Médicos:</strong> +${diff.docs_added.length}, -${diff.docs_removed.length}<br>`;
                diffHtml += `<strong>Membros:</strong> +${diff.mem_added.length}, -${diff.mem_removed.length}<br><br>`;
                
                if (diff.docs_added.length > 0) diffHtml += `<em>Médicos Adicionados:</em> ${diff.docs_added.join(', ')}<br>`;
                if (diff.docs_removed.length > 0) diffHtml += `<em>Médicos Removidos:</em> ${diff.docs_removed.join(', ')}<br>`;
                if (diff.mem_added.length > 0) diffHtml += `<em>Membros Adicionados:</em> ${diff.mem_added.join(', ')}<br>`;
                if (diff.mem_removed.length > 0) diffHtml += `<em>Membros Removidos:</em> ${diff.mem_removed.join(', ')}<br>`;
                
                if(diff.docs_added.length === 0 && diff.docs_removed.length === 0 && diff.mem_added.length === 0 && diff.mem_removed.length === 0) {
                    diffHtml += "Nenhuma alteração detectada. Você pode confirmar ou descartar.";
                }
                
                document.getElementById('syncColihDiff').innerHTML = diffHtml;
                document.getElementById('syncColihPreviewArea').style.display = 'block';
            } else {
                alert('Erro ao gerar preview COLIH: ' + (res.error || 'Desconhecido'));
            }
        }
        
        if (doCnes && !doColih) {
            document.getElementById('syncStatusModal').style.display = 'none';
        }
        
        carregarStatusSync();
    } catch(e) {
        alert('Erro ao iniciar sincronização.');
    } finally {
        document.getElementById('btnForceSync').disabled = false;
        document.getElementById('btnForceSync').innerHTML = '<i class="fas fa-sync-alt"></i> Forçar Sincronização';
    }
}

async function commitColihSync() {
    try {
        const btn = document.querySelector('#syncColihPreviewArea .btn-primary');
        btn.disabled = true;
        btn.innerHTML = "Aplicando...";
        const res = await fetchAPI('/colih/sync?action=commit', { method: 'POST' });
        if(res && res.success) {
            alert(res.message || 'Aplicado com sucesso');
            document.getElementById('syncStatusModal').style.display = 'none';
            document.getElementById('syncColihPreviewArea').style.display = 'none';
        } else {
            alert('Erro ao aplicar: ' + (res.error || ''));
        }
        btn.disabled = false;
        btn.innerHTML = "Confirmar e Aplicar COLIH";
    } catch(e) {
        alert('Erro ao confirmar.');
    }
}

async function discardColihSync() {
    try {
        await fetchAPI('/colih/sync?action=discard', { method: 'POST' });
        document.getElementById('syncColihPreviewArea').style.display = 'none';
    } catch(e) {}
}


let hlcDict = {};
async function loadHlcDict() {
    try {
        const res = await fetchAPI('/config/hlc-dict');
        hlcDict = res || {};
        renderHlcDict();
    } catch(e) { console.error('Erro load HLC dict', e); }
}


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
            renderHlcDict();
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
    hlcAlvos.forEach(t => groups[t] = []);
    
    Object.entries(hlcDict).forEach(([k, v]) => {
        // Fallback to grouping by 'v' even if it's not in hlcAlvos (just in case)
        if(!groups[v]) groups[v] = [];
        groups[v].push(k);
    });
    // Sort groups alphabetically
    const sortedTargets = Object.keys(groups).sort((a,b) => a.localeCompare(b));
    
    container.innerHTML = sortedTargets.map(target => {
        const children = groups[target].sort();
        let childrenHtml = `<div style="font-size:12px; color:var(--text-muted); padding:8px 12px; font-style:italic;">Nenhuma especialidade do CNES mapeada.</div>`;
        if (children.length > 0) {
            childrenHtml = children.map(c => `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; border-bottom:1px solid var(--border-color); font-size:13px; color:var(--text-secondary); background:var(--bg-input); border-radius:4px; margin-bottom:4px;">
                <span>↳ ${c}</span>
                <div style="display:flex; gap:6px;">
                    <button class="btn-secondary btn-sm" onclick="editarHlcDict('${c}')" style="padding:2px 6px; font-size:11px;">✏️</button>
                    <button class="btn-secondary btn-sm" onclick="removerHlcDict('${c}')" style="padding:2px 6px; font-size:11px; color:#ef4444;">❌</button>
                </div>
            </div>
            `).join('');
        }
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
    
    // Render unmapped CNES specialties
    if (cnesEspecialidadesFull && cnesEspecialidadesFull.length > 0) {
        const unmapped = cnesEspecialidadesFull.filter(cnes => {
            return !Object.keys(hlcDict).some(k => k.toUpperCase() === cnes.toUpperCase());
        });
        
        const countEl = document.getElementById('unmapped-cnes-count');
        const listEl = document.getElementById('unmapped-cnes-list');
        if (countEl && listEl) {
            countEl.innerText = unmapped.length;
            listEl.innerHTML = unmapped.map(u => `
                <span style="background:var(--bg-input); padding:4px 8px; border-radius:4px; border:1px solid var(--border-color); font-size:11px; color:var(--text-secondary); cursor:pointer;" onclick="document.getElementById('hlc-key-input').value='${u}'; document.getElementById('hlc-key-input').focus();" title="Clique para mapear">
                    ${u}
                </span>
            `).join('');
        }
    }
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


// ─── DASHBOARD GAMIFICAÇÃO HLC ────────────────────────────────────────────────
window.abrirRecrutamentoSUS = function(hospital, alvo) {
    const tabBtn = document.querySelector('.menu-item[onclick*="medicos"]');
    if (tabBtn) window.openTab('medicos', tabBtn);
    
    const hospInput = document.getElementById('med-hosp-input');
    if (hospInput) hospInput.value = hospital;
    
    const espInput = document.getElementById('med-esp-input');
    const espSelect = document.getElementById('med-esp-select');
    if (espInput) espInput.value = alvo;
    if (espSelect) espSelect.value = alvo;
    
    buscarMedicos();
};

async function renderDashboardGamificacao() {
    try {
        const [dictRes, colihMed, hospRes, susStats] = await Promise.all([
            fetchAPI('/config/hlc-dict').catch(() => ({})),
            fetchAPI('/colih/medicos').catch(() => []),
            fetchAPI('/hospitais?limit=1000').catch(() => ({ hospitais: [] })),
            fetchAPI('/config/hlc-stats').catch(() => ({}))
        ]);
        
        const hlcDict = dictRes || {};
        const colihDocs = colihMed || [];
        
        // Use all 28 official HLC targets from hlcAlvos defined globally
        const targetSpecialties = window.hlcAlvos || [
            "Anestesiologia", "Cirurgia bucomaxilofacial", "Cirurgia cardíaca", "Coloproctologia",
            "Cirurgia de transplante", "Cirurgia de trauma", "Cirurgia geral", "Ortopedia",
            "Cirurgia torácica", "Cirurgia vascular", "Clínica médica", "Medicina intensiva",
            "Gastroenterologia", "Ginecologia", "Ginecologia oncológica", "Hematologia",
            "Medicina de emergência", "Medicina hospitalar", "Nefrologia", "Neonatologia",
            "Neurocirurgia", "Obstetrícia", "Oncologia clínica", "Otorrinolaringologia",
            "Pneumologia", "Radiologia intervencionista", "Tratamento de queimados", "Urologia"
        ];
        
        // Map doctors to HLC targets
        const coverageMap = {};
        targetSpecialties.forEach(t => coverageMap[t] = []);

        colihDocs.forEach(d => {
            const esp1 = (d.especialidade_1_colih || '').toUpperCase();
            const esp2 = (d.especialidade_2_colih || '').toUpperCase();
            const esp3 = (d.especialidade_3_colih || '').toUpperCase();
            const esp4 = (d.especialidade_4_colih || '').toUpperCase();
            
            const checkEsp = (esp) => {
                if (!esp) return;
                // 1. Direct match against targets
                const directMatch = targetSpecialties.find(t => t.toUpperCase() === esp);
                if (directMatch && !coverageMap[directMatch].find(doc => doc.id === d.id)) coverageMap[directMatch].push(d);
                
                // 2. Dictionary match
                if (hlcDict[esp] && coverageMap[hlcDict[esp]] && !coverageMap[hlcDict[esp]].find(doc => doc.id === d.id)) {
                    coverageMap[hlcDict[esp]].push(d);
                }
            };
            
            checkEsp(esp1);
            checkEsp(esp2);
            checkEsp(esp3);
            checkEsp(esp4);
        });
        
        const coveredTargets = targetSpecialties.filter(t => coverageMap[t].length > 0);
        const coveragePct = Math.round((coveredTargets.length / targetSpecialties.length) * 100);
        document.getElementById('dash-cobertura-pct').innerText = `${coveragePct}%`;
        document.getElementById('dash-total-coop').innerText = colihDocs.length;
        
        const missing = targetSpecialties.filter(t => coverageMap[t].length === 0);
        document.getElementById('dash-red-flags').innerText = missing.length;
        
        // Render Red Flags list
        const redListEl = document.getElementById('dash-red-list');
        redListEl.innerHTML = missing.map(m => `
            <span style="background: rgba(239, 68, 68, 0.1); color: #ef4444; padding: 4px 12px; border-radius: 16px; font-size: 13px; font-weight: 700; border: 1px solid #ef4444;">
                ${m}
            </span>
        `).join('');
        
        // Priority Coverage
        const priorityCoverage = targetSpecialties.filter(t => coverageMap[t].length >= 1 && coverageMap[t].length <= 3)
            .sort((a, b) => coverageMap[a].length - coverageMap[b].length);
        const priorityHtml = priorityCoverage.map(m => {
            const count = coverageMap[m].length;
            return `<span style="background: rgba(245, 158, 11, 0.1); color: #f59e0b; padding: 4px 12px; border-radius: 16px; font-size: 13px; font-weight: 700; border: 1px solid #f59e0b;">${m} (${count})</span>`;
        }).join('');

        // 0 SUS Docs Logic
        const zeroSusDocs = [];
        for (const [t, count] of Object.entries(susStats)) {
            if (count === 0 && targetSpecialties.includes(t)) zeroSusDocs.push(t);
        }
        zeroSusDocs.sort((a,b) => a.localeCompare(b));
        
        let zeroSusHtml = zeroSusDocs.length > 0 ? zeroSusDocs.map(k => `<span style="background:rgba(239,68,68,0.1); color:#ef4444; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:600; border:1px solid #ef4444;" title="Nenhum médico registrado no CNES para esta especialidade na região">⚠️  ${k}</span>`).join('') : '<span style="font-size:12px; color:var(--text-muted);">Nenhuma. Todas possuem médicos no SUS.</span>';

        const priorityEl = document.getElementById('dash-priority-list');
        if (priorityEl) {
            priorityEl.innerHTML = `
            <div style="margin-bottom:16px;">
                <h4 style="font-size:12px; color:#ef4444; margin-bottom:8px; display:flex; align-items:center; gap:6px;"><i data-lucide="alert-octagon" style="width:14px; height:14px;"></i> Sem Cobertura SUS (0 Médicos):</h4>
                <div style="display:flex; flex-wrap:wrap; gap:8px;">${zeroSusHtml}</div>
            </div>
            <div>
                <h4 style="font-size:12px; color:#f59e0b; margin-bottom:8px; display:flex; align-items:center; gap:6px;"><i data-lucide="alert-triangle" style="width:14px; height:14px;"></i> Cobertura COLIH Crítica (1 a 3 Cooperadores):</h4>
                <div style="display:flex; flex-wrap:wrap; gap:8px;">${priorityHtml}</div>
            </div>
            `;
            lucide.createIcons();
        }
        
        // Target Hospitals List
        if (!hospRes.estabelecimentos) return;
        
        const highComp = hospRes.estabelecimentos.filter(h => h._altaComplexidade && Array.isArray(h._altaComplexidade) && h._altaComplexidade.length > 0).slice(0, 15);
        const medComp = hospRes.estabelecimentos.filter(h => h._complexidade && h._complexidade.includes('Média') && !(h._altaComplexidade && h._altaComplexidade.length > 0)).slice(0, 10);
        
        const renderHospCards = (hospitals, containerId, isMedium) => {
            const targetsEl = document.getElementById(containerId);
            if (!targetsEl) return;
            targetsEl.innerHTML = hospitals.map(h => {
                let compList = (h._altaComplexidade && Array.isArray(h._altaComplexidade)) ? h._altaComplexidade.join(', ') : '';
                if (!compList && h._complexidade) compList = h._complexidade;
                compList = compList.replace(/Alta Complexidade (em |de )?/gi, '');
                
                // Covered Targets
                const hospTargets = new Set();
                (h.especialidades || []).forEach(espStr => {
                    const parts = espStr.split(' / ');
                    parts.forEach(p => {
                        const pUp = p.trim().toUpperCase();
                        if (hlcDict[pUp]) hospTargets.add(hlcDict[pUp]);
                    });
                });
                
                // Build coverage maps
                const coveredTargets = {};
                const otherColihDocs = [];
                const hospColihDocs = colihDocs.filter(d => {
                    const hStr = (d.hospitais || '').toLowerCase();
                    const hNome = (h.nome || '').toLowerCase();
                    if (!hStr) return false;
                    return hStr.includes(hNome) || (hNome.length > 8 && hNome.includes(hStr) && hStr.length > 8);
                });
                
                hospColihDocs.forEach(d => {
                    let mapped = false;
                    const checkEsp = (esp) => {
                        if (!esp) return;
                        const directMatch = targetSpecialties.find(t => t.toUpperCase() === esp.toUpperCase());
                        if (directMatch) {
                            if (!coveredTargets[directMatch]) coveredTargets[directMatch] = [];
                            if (!coveredTargets[directMatch].find(doc => doc.id === d.id)) coveredTargets[directMatch].push(d);
                            mapped = true;
                        }
                        if (hlcDict[esp.toUpperCase()]) {
                            const t = hlcDict[esp.toUpperCase()];
                            if (!coveredTargets[t]) coveredTargets[t] = [];
                            if (!coveredTargets[t].find(doc => doc.id === d.id)) coveredTargets[t].push(d);
                            mapped = true;
                        }
                    };
                    checkEsp(d.especialidade_1_colih);
                    checkEsp(d.especialidade_2_colih);
                    checkEsp(d.especialidade_3_colih);
                    checkEsp(d.especialidade_4_colih);
                    if (!mapped) otherColihDocs.push(d);
                });
                
                const coveredKeys = Object.keys(coveredTargets).sort();
                const missingTargets = Array.from(hospTargets).filter(t => !coveredTargets[t]).sort();
                
                // Build UI
                let coveredHtml = '';
                if (coveredKeys.length > 0 || otherColihDocs.length > 0) {
                    coveredHtml += `
                    <div style="margin-bottom:8px;">
                        <div style="font-size:11px; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Cobertura COLIH:</div>
                        <div style="display:flex; flex-wrap:wrap; gap:4px;">`;
                    
                    coveredKeys.forEach(t => {
                        const docs = coveredTargets[t].map(d => d.nome).join('&#10;');
                        coveredHtml += `<span title="${docs}" style="background:rgba(16,185,129,0.1); color:#10b981; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:600; border:1px solid #10b981; cursor:help;">✓ ${t} (${coveredTargets[t].length})</span>`;
                    });
                    
                    if (otherColihDocs.length > 0) {
                        const docs = otherColihDocs.map(d => d.nome + ' (' + (d.especialidade_1_colih || 'N/A') + ')').join('&#10;');
                        coveredHtml += `<span title="${docs}" style="background:rgba(107,114,128,0.1); color:#6b7280; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:600; border:1px solid #6b7280; cursor:help;">+ ${otherColihDocs.length} Outras Especialidades</span>`;
                    }
                    
                    coveredHtml += `
                        </div>
                    </div>`;
                } else {
                    coveredHtml = `
                    <div style="margin-bottom:8px;">
                        <div style="font-size:11px; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Cobertura COLIH:</div>
                        <span style="font-size:11px; color:#9ca3af; font-style:italic;">Nenhum membro registrado neste hospital.</span>
                    </div>`;
                }
                
                // Build UI for Missing (Red)
                let missingHtml = '';
                if (missingTargets.length > 0) {
                    missingHtml = `
                    <div style="margin-bottom:12px;">
                        <div style="font-size:11px; font-weight:700; color:var(--text-secondary); margin-bottom:4px;">Alvos de Recrutamento:</div>
                        <div style="display:flex; flex-wrap:wrap; gap:4px;">
                            ${missingTargets.map(t => `<span style="background:rgba(239,68,68,0.1); color:#ef4444; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:600; border:1px solid #ef4444; cursor:pointer;" onclick="window.abrirRecrutamentoSUS('${h.nome.replace(/'/g, "\\'")}', '${t}')" title="Buscar médicos desta especialidade no hospital">⚠️ ${t}</span>`).join('')}
                        </div>
                    </div>`;
                }
                
                return `
                <div style="background:var(--bg-card); padding:16px; border-radius:8px; border:1px solid var(--border-color); border-left:4px solid ${isMedium ? '#f59e0b' : '#ef4444'}; display:flex; flex-direction:column; height:100%;">
                    <div style="font-weight:700; font-size:14px; margin-bottom:4px; display:flex; align-items:flex-start; justify-content:space-between; gap:8px;">
                        <span>${h.nome}</span>
                        ${isMedium ? '<span style="background:#f59e0b; color:white; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; flex-shrink:0;">Média</span>' : '<span style="background:#ef4444; color:white; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; flex-shrink:0;">Alta</span>'}
                    </div>
                    <div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">${h.municipio || ''}</div>
                    
                    ${compList ? `<div style="font-size:11px; color:var(--text-secondary); margin-bottom:6px;"><strong>Habilitações:</strong> ${compList}</div>` : ''}
                    
                    ${coveredHtml}
                    ${missingHtml}

                    <div style="margin-top:auto; padding-top:8px;">
                        <button class="btn-secondary btn-sm" onclick="abrirDetalheHospital('${h.cnes}')">Ver Detalhes</button>
                    </div>
                </div>
            `}).join('');
            if (hospitals.length === 0) targetsEl.innerHTML = '<div style="color:var(--text-muted); font-size:13px;">Nenhum hospital encontrado.</div>';
        };
        
        renderHospCards(highComp, 'dash-targets-list', false);
        renderHospCards(medComp, 'dash-targets-med-list', true);
        
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




// ─── SIDEBAR TOGGLE LOGIC ──────────────────────────────────────────────────
function toggleGroup(groupId) {
    const groupDiv = document.getElementById('group-' + groupId);
    const li = groupDiv.previousElementSibling;
    const icon = li.querySelector('.lucide');
    if (!groupDiv || !icon) return;
    
    if (groupDiv.style.display === 'none') {
        groupDiv.style.display = 'block';
        icon.setAttribute('data-lucide', 'chevron-down');
    } else {
        groupDiv.style.display = 'none';
        icon.setAttribute('data-lucide', 'chevron-right');
    }
    
    // Create new SVG replacing the old one
    const newI = document.createElement('i');
    newI.setAttribute('data-lucide', icon.getAttribute('data-lucide'));
    newI.id = 'icon-' + groupId;
    li.replaceChild(newI, icon);
    if(window.lucide) window.lucide.createIcons();
}


// ─── COLIH AUXILIARY FUNCTIONS ───────────────────────────────────────────────

function popularFiltrosColih() {
    const especialidades = new Set();
    colihMedicosCache.forEach(m => {
        if(m.especialidade_1_colih) especialidades.add(m.especialidade_1_colih.trim());
        if(m.especialidade_2_colih) especialidades.add(m.especialidade_2_colih.trim());
        if(m.especialidade_3_colih) especialidades.add(m.especialidade_3_colih.trim());
        if(m.especialidade_4_colih) especialidades.add(m.especialidade_4_colih.trim());
    });
    
    const regioes = new Set();
    colihMembrosCache.forEach(m => {
        if(m.regiao) regioes.add(m.regiao.trim());
    });
    
    const selEsp = document.getElementById('filtro-colih-especialidade');
    if(selEsp) {
        selEsp.innerHTML = '<option value="">Todas as Especialidades</option>';
        Array.from(especialidades).sort().forEach(e => {
            selEsp.innerHTML += `<option value="${e}">${e}</option>`;
        });
    }
    
    const selReg = document.getElementById('filtro-colih-regiao');
    if(selReg) {
        selReg.innerHTML = '<option value="">Todos os Grupos (Regiões)</option>';
        Array.from(regioes).sort().forEach(r => {
            selReg.innerHTML += `<option value="${r}">${r}</option>`;
        });
    }
}

let coordsMembroAtual = null;

function abrirModalCoords(id) {
    const membro = colihMembrosCache.find(m => m.id === id);
    if(!membro) return;
    coordsMembroAtual = membro;
    
    document.getElementById('coord-membro-id').value = membro.id;
    document.getElementById('coord-membro-nome').value = membro.nome;
    document.getElementById('coord-lat').value = membro.lat || '';
    document.getElementById('coord-lon').value = membro.lon || '';
    document.getElementById('coord-endereco').value = membro.endereco_atual || '';
    
    document.getElementById('modal-coords').classList.add('open');
}

async function salvarCoordenadasMembro() {
    if(!coordsMembroAtual) return;
    
    const latRaw = document.getElementById('coord-lat').value;
    const lonRaw = document.getElementById('coord-lon').value;
    const endereco = document.getElementById('coord-endereco').value;
    
    const lat = latRaw ? parseFloat(latRaw) : null;
    const lon = lonRaw ? parseFloat(lonRaw) : null;
    
    const payload = {
        lat: lat,
        lon: lon,
        endereco_atual: endereco
    };
    
    try {
        const btn = document.querySelector('#modal-coords .btn-primary');
        const oldText = btn.innerText;
        btn.innerText = 'Salvando...';
        btn.disabled = true;
        
        const res = await fetchAPI(`/colih/membros/${coordsMembroAtual.id}/coords`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        btn.innerText = oldText;
        btn.disabled = false;
        
        if(res.success) {
            coordsMembroAtual.lat = lat;
            coordsMembroAtual.lon = lon;
            coordsMembroAtual.endereco_atual = endereco;
            fecharModal('modal-coords');
            renderColihMembros();
            alert('Coordenadas salvas com sucesso no banco de dados!');
        } else {
            alert('Erro ao salvar: ' + res.error);
        }
    } catch(e) {
        alert('Erro de rede ao salvar coordenadas.');
    }
}


popularDatalistCNES();


// ==========================================
// CÓDIGO DO NOVO PIPELINE DE VISITAS
// ==========================================

// Variáveis globais para o contexto da visita
let currentMedicoPipelineCNS = null;
let currentInstituicaoPipelineCNES = null;
let currentVisitaId = null;

// Função chamada quando se abre a modal do Pipeline
const originalOpenPipelineModal = window.openPipelineModal;
window.openPipelineModal = function(cns, nome, esp, cbo, vp, cp) {
    currentMedicoPipelineCNS = cns;
    // Se a função original existir, a chamamos (pode ser necessário lidar com isso se sobrescrever)
    if(typeof originalOpenPipelineModal === 'function') {
        originalOpenPipelineModal(cns, nome, esp, cbo, vp, cp);
    }
    
    // Carregar grupos e instituições no dropdown
    carregarDropdownGrupos();
    carregarDropdownInstituicoes();
};

function switchPipelineTab(tabId) {
  document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.ptab-content').forEach(c => c.style.display = 'none');
  
  if(tabId === 'info') {
    document.querySelector('.modal-tab:nth-child(1)').classList.add('active');
    document.getElementById('ptab-info').style.display = 'block';
  } else if(tabId === 'instituicao') {
    document.querySelector('.modal-tab:nth-child(2)').classList.add('active');
    document.getElementById('ptab-instituicao').style.display = 'block';
    // Carregar os dados que já existem
    carregarDadosInstituicaoPipeline();
  } else if(tabId === 'contatos') {
    document.querySelector('.modal-tab:nth-child(3)').classList.add('active');
    document.getElementById('ptab-contatos').style.display = 'block';
  }
}

async function carregarDropdownGrupos() {
    try {
        const res = await fetch(`${API}/grupos`);
        const data = await res.json();
        const select = document.getElementById('pip-inst-grupo');
        select.innerHTML = '<option value="">Selecione um grupo...</option>';
        data.grupos.forEach(g => {
            select.innerHTML += `<option value="${g.id}">${g.nome}</option>`;
        });
    } catch(e) { console.error("Erro ao carregar grupos", e); }
}

async function carregarDropdownInstituicoes() {
    try {
        const res = await fetch(`${API}/hospitais`);
        const data = await res.json();
        const select = document.getElementById('pip-instituicao-cnes');
        select.innerHTML = '<option value="">Selecione um local...</option>';
        data.data.forEach(h => {
            select.innerHTML += `<option value="${h.cnes}">${h.nomeFantasia || h.razaoSocial}</option>`;
        });
    } catch(e) { console.error("Erro ao carregar hospitais", e); }
}

async function carregarDadosInstituicaoPipeline() {
    const cnesSelect = document.getElementById('pip-instituicao-cnes');
    const cnes = cnesSelect.value;
    if(!cnes) return;
    
    try {
        const res = await fetch(`${API}/instituicoes-pipeline/${cnes}/${currentMedicoPipelineCNS}`);
        const data = await res.json();
        if(data && data.cnes) {
            document.getElementById('pip-inst-tel').value = data.telefone || '';
            document.getElementById('pip-inst-contato').value = data.contato_nome || '';
            document.getElementById('pip-inst-grupo').value = data.grupo_id || '';
            document.getElementById('pip-inst-notas').value = data.notas || '';
            
            if(data.grupo_id) {
                document.getElementById('btn-agendar-visita').style.display = 'inline-block';
            }
        }
    } catch(e) { console.error(e); }
}

document.getElementById('pip-instituicao-cnes').addEventListener('change', () => {
    carregarDadosInstituicaoPipeline();
});

async function salvarInstituicaoPipeline() {
    const cnesSelect = document.getElementById('pip-instituicao-cnes');
    const cnes = cnesSelect.value;
    if(!cnes) { alert("Selecione um local primeiro!"); return; }
    
    const payload = {
        telefone: document.getElementById('pip-inst-tel').value,
        contato_nome: document.getElementById('pip-inst-contato').value,
        grupo_id: document.getElementById('pip-inst-grupo').value,
        grupo_nome: document.getElementById('pip-inst-grupo').options[document.getElementById('pip-inst-grupo').selectedIndex].text,
        notas: document.getElementById('pip-inst-notas').value,
        nome: cnesSelect.options[cnesSelect.selectedIndex].text
    };
    
    try {
        const res = await fetch(`${API}/instituicoes-pipeline/${cnes}/${currentMedicoPipelineCNS}`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if(data.cnes) {
            alert("Salvo com sucesso!");
            if(payload.grupo_id) {
                document.getElementById('btn-agendar-visita').style.display = 'inline-block';
            }
        }
    } catch(e) { console.error(e); alert("Erro ao salvar"); }
}

function abrirModalAgendarVisita() {
    const grupo_id = document.getElementById('pip-inst-grupo').value;
    if(!grupo_id) { alert("Defina o Grupo antes de agendar!"); return; }
    document.getElementById('agendarVisitaModal').style.display = 'flex';
    // Load members
    fetch(`${API}/info`) // Usando algo existente ou idealmente um endpoint de membros do grupo
}

async function confirmarAgendamentoVisita() {
    const cnesSelect = document.getElementById('pip-instituicao-cnes');
    const grupoSelect = document.getElementById('pip-inst-grupo');
    
    const payload = {
        medico_cns: currentMedicoPipelineCNS,
        medico_nome: document.getElementById('pip-nome').innerText,
        instituicao_cnes: cnesSelect.value,
        instituicao_nome: cnesSelect.options[cnesSelect.selectedIndex].text,
        grupo_id: grupoSelect.value,
        grupo_nome: grupoSelect.options[grupoSelect.selectedIndex].text,
        data_agendada: document.getElementById('visita-data').value || new Date().toISOString().split('T')[0],
        janela_descricao: document.getElementById('visita-janela').value,
        criado_por: currentUser ? currentUser.nome : 'Sistema'
    };
    
    try {
        const res = await fetch(`${API}/visitas`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if(data.ok) {
            alert("Visita agendada e notificações em cascata iniciadas!");
            document.getElementById('agendarVisitaModal').style.display = 'none';
        }
    } catch(e) { alert("Erro ao agendar visita"); }
}

async function carregarCalendario() {
    try {
        const res = await fetch(`${API}/visitas/calendario`);
        const data = await res.json();
        const grid = document.getElementById('calendario-grid');
        grid.innerHTML = '';
        
        if(!data.visitas || data.visitas.length === 0) {
            grid.innerHTML = '<p>Nenhuma visita agendada encontrada.</p>';
            return;
        }
        
        data.visitas.forEach(v => {
            const card = document.createElement('div');
            card.className = 'card';
            card.style.padding = '16px';
            card.innerHTML = `
                <h3 style="margin:0 0 8px 0; font-size:16px;">${v.medico_nome}</h3>
                <p style="margin:4px 0; font-size:14px;"><i data-lucide="building"></i> ${v.instituicao_nome}</p>
                <p style="margin:4px 0; font-size:14px;"><i data-lucide="users"></i> Grupo: ${v.grupo_nome}</p>
                <p style="margin:4px 0; font-size:14px;"><i data-lucide="user"></i> Membro: ${v.membro_designado_nome || 'Aguardando Aceite...'}</p>
                <p style="margin:4px 0; font-size:14px;"><i data-lucide="calendar"></i> Data: ${new Date(v.data_agendada).toLocaleDateString()} ${v.janela_descricao || ''}</p>
                <div style="margin-top:12px;">
                    <span style="background:#e2e8f0; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:600;">Status: ${v.status}</span>
                </div>
                ${v.status === 'agendada' ? `<button class="btn btn-secondary" style="margin-top:12px; width:100%;" onclick="abrirModalResultado('${v.id}')">Lançar Resultado Pós-Visita</button>` : ''}
            `;
            grid.appendChild(card);
        });
        lucide.createIcons();
    } catch(e) { console.error(e); }
}

function abrirModalResultado(id) {
    currentVisitaId = id;
    document.getElementById('res-visita-id').value = id;
    document.getElementById('resultadoVisitaModal').style.display = 'flex';
}

function toggleVisitaMotivo() {
    const status = document.getElementById('res-status').value;
    document.getElementById('res-motivo-container').style.display = status === 'perdido' ? 'flex' : 'none';
}

async function salvarResultadoVisita() {
    const status = document.getElementById('res-status').value;
    const payload = {
        status: status,
        motivo: status === 'perdido' ? document.getElementById('res-motivo').value : null,
        falha_de: status === 'perdido' ? document.getElementById('res-falha').value : null,
        membro_continua: status === 'perdido' ? document.getElementById('res-membro-continua').value === 'true' : null
    };
    
    try {
        const res = await fetch(`${API}/visitas/${currentVisitaId}/resultado`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if(data.ok) {
            alert("Resultado salvo!");
            document.getElementById('resultadoVisitaModal').style.display = 'none';
            carregarCalendario();
        }
    } catch(e) { alert("Erro ao salvar resultado"); }
}

async function carregarConfigComunicacao() {
    try {
        const res = await fetch(`${API}/settings`);
        const data = await res.json();
        if(data) {
            document.getElementById('cfg-webhook-url').value = data.webhook_n8n_url || '';
            document.getElementById('cfg-evolution-instance').value = data.evolution_instance || '';
            document.getElementById('cfg-tpl-convite').value = data.template_mensagem_convite || '';
            document.getElementById('cfg-retencao-meses').value = data.retencao_historico_meses || '3';
        }
    } catch(e) {}
}

async function salvarConfigComunicacao() {
    const payload = {
        webhook_n8n_url: document.getElementById('cfg-webhook-url').value,
        evolution_instance: document.getElementById('cfg-evolution-instance').value,
        template_mensagem_convite: document.getElementById('cfg-tpl-convite').value,
        retencao_historico_meses: parseInt(document.getElementById('cfg-retencao-meses').value)
    };
    try {
        const res = await fetch(`${API}/settings`, {
            method: 'PUT', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if(data.ok) alert("Configurações salvas!");
    } catch(e) { alert("Erro ao salvar"); }
}

// Interceptar mudança de aba para carregar dados preguiçosamente
const oldOpenTab = window.openTab;
window.openTab = function(tabId, element) {
    oldOpenTab(tabId, element);
    if(tabId === 'calendario') {
        carregarCalendario();
    } else if(tabId === 'config-comunicacao') {
        carregarConfigComunicacao();
    }
};



const oldSwitchInnerTab = window.switchInnerTab;
window.switchInnerTab = function(tabId, el) {
    if(oldSwitchInnerTab) oldSwitchInnerTab(tabId, el);
    else {
        // Fallback manual se a original não existir no escopo global
        const modalBody = el.closest('.modal-body');
        modalBody.querySelectorAll('.inner-tab').forEach(t => t.classList.remove('active'));
        modalBody.querySelectorAll('.inner-tab-panel').forEach(p => p.classList.remove('active'));
        el.classList.add('active');
        document.getElementById(tabId).classList.add('active');
    }
    
    if(tabId === 'tab-visitas') {
        currentMedicoPipelineCNS = document.getElementById('edit-cns').value;
        currentInstituicaoPipelineCNES = null; // reseta
        carregarDropdownGrupos();
        carregarDropdownInstituicoes();
        // Wait a bit then load existing data
        setTimeout(() => carregarDadosInstituicaoPipeline(), 500);
    }
};



// ==========================================
// CÓDIGO DA GESTÃO DE USUÁRIOS
// ==========================================

async function carregarDropdownCongregacoes() {
    try {
        const res = await fetch(`${API}/congregacoes`);
        const data = await res.json();
        const select = document.getElementById('usr-congregacao');
        select.innerHTML = '<option value="">Selecione a congregação...</option>';
        data.congregacoes.forEach(c => {
            select.innerHTML += `<option value="${c.id}">${c.numero} - ${c.nome}</option>`;
        });
    } catch(e) { console.error("Erro ao carregar congregações", e); }
}

async function carregarUsuariosGrid() {
    try {
        const res = await fetch(`${API}/usuarios`);
        const data = await res.json();
        const grid = document.getElementById('usuarios-grid');
        grid.innerHTML = '';
        if(!data.usuarios || data.usuarios.length === 0) {
            grid.innerHTML = '<p>Nenhum usuário cadastrado.</p>';
            return;
        }
        data.usuarios.forEach(u => {
            grid.innerHTML += `
                <div class="card" style="padding:16px;">
                   <h3 style="margin:0 0 8px 0; font-size:16px;">${u.nome}</h3>
                   <p style="margin:4px 0; font-size:14px;"><i data-lucide="phone"></i> ${u.telefone || '—'}</p>
                   <p style="margin:4px 0; font-size:14px;"><i data-lucide="home"></i> ${u.congregacao_nome || '—'}</p>
                   <button class="btn btn-danger" style="margin-top:12px; width:100%;" onclick="deletarUsuario('${u.id}')">Excluir</button>
                </div>
            `;
        });
        lucide.createIcons();
    } catch(e) { console.error(e); }
}

async function salvarUsuario() {
    const nome = document.getElementById('usr-nome').value;
    const tel = document.getElementById('usr-tel').value;
    const cong = document.getElementById('usr-congregacao').value;
    
    if(!nome) { alert("Nome é obrigatório"); return; }
    
    try {
        const res = await fetch(`${API}/usuarios`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nome: nome, telefone: tel, congregacao_id: cong ? parseInt(cong) : null })
        });
        const data = await res.json();
        if(data.ok) {
            alert("Salvo com sucesso!");
            document.getElementById('usr-nome').value = '';
            document.getElementById('usr-tel').value = '';
            carregarUsuariosGrid();
        }
    } catch(e) { alert("Erro ao salvar usuário."); }
}

async function deletarUsuario(id) {
    if(!confirm("Certeza que deseja excluir este usuário?")) return;
    try {
        await fetch(`${API}/usuarios/${id}`, { method: 'DELETE' });
        carregarUsuariosGrid();
    } catch(e) { alert("Erro ao deletar"); }
}

// Hook tab loading
const oldOpenTabConfig = window.openTab;
window.openTab = function(tabId, element) {
    if(oldOpenTabConfig) oldOpenTabConfig(tabId, element);
    if(tabId === 'calendario') {
        carregarCalendario();
    } else if(tabId === 'config-comunicacao') {
        carregarConfigComunicacao();
    } else if(tabId === 'config-usuarios') {
        carregarDropdownCongregacoes();
        carregarUsuariosGrid();
    }
};



// ==========================================
// BUSCA AUXILIAR DE HOSPITAL NO PIPELINE
// ==========================================
function verificarHospitalOutro() {
    const val = document.getElementById('pip-hospital').value;
    const container = document.getElementById('pip-hospital-outro-container');
    if(val === 'outro') {
        container.style.display = 'block';
        initTomSelectHospital();
    } else {
        container.style.display = 'none';
    }
}


let pipHospitalTomSelect = null;
function initTomSelectHospital() {
    if(pipHospitalTomSelect) return;
    pipHospitalTomSelect = new TomSelect("#pip-hospital-busca-ts", {
        valueField: 'cnes',
        labelField: 'nomeFantasia',
        searchField: ['nomeFantasia', 'razaoSocial', 'cnes'],
        load: function(query, callback) {
            if(!query.length) return callback();
            fetch(`${API}/hospitais?nome=${encodeURIComponent(query)}&limit=10`)
                .then(r => r.json())
                .then(json => {
                    callback(json.estabelecimentos || []);
                }).catch(() => callback());
        },
        render: {
            option: function(item, escape) {
                return `<div>
                    <span style="font-weight:bold;">${escape(item.nomeFantasia || item.razaoSocial)}</span><br>
                    <span style="font-size:11px; color:#aaa;">CNES: ${escape(item.cnes)}</span>
                </div>`;
            },
            item: function(item, escape) {
                return `<div>${escape(item.nomeFantasia || item.razaoSocial)}</div>`;
            }
        },
        onChange: function(value) {
            if(!value) return;
            const item = pipHospitalTomSelect.options[value];
            if(item) {
                const selectHosp = document.getElementById('pip-hospital');
                const opt = document.createElement('option');
                const nomeHosp = item.nomeFantasia || item.razaoSocial;
                opt.value = nomeHosp;
                opt.textContent = nomeHosp;
                
                selectHosp.insertBefore(opt, selectHosp.lastElementChild);
                selectHosp.value = nomeHosp;
                document.getElementById('pip-cnes').value = item.cnes;
                
                document.getElementById('pip-hospital-outro-container').style.display = 'none';
                pipHospitalTomSelect.clear(true);
            }
        }
    });
}

