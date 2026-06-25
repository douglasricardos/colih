import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if 'async function abrirDetalheHospital(cnesId, hospData) {' in line:
        start_idx = i
    if 'function fecharDetalheHospital()' in line:
        end_idx = i

if start_idx == -1 or end_idx == -1:
    print("Could not find bounds")
    sys.exit(1)

new_func = """async function abrirDetalheHospital(cnesId, hospData) {
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
    espsHtml = especialidadesFiltradas.map(e => `<span class="status-badge" style="background:var(--accent-purple); color:white; font-size:12px; padding:6px 12px; border-radius:15px; font-weight:600; cursor:pointer;" onclick="filtrarMedicosPorEspecialidade('${e.replace(/'/g,"\\\\\\'").replace(/"/g,"&quot;")}')">${e}</span>`).join('');
  } else {
    espsHtml = '<p style="color:var(--text-muted); font-size:13px; width:100%;">Nenhuma especialidade mapeada para este hospital.</p>';
  }

  const raw = hospData.raw || {};
  let dir = raw.NOME_DIRETOR_CLINICO || raw.NO_DIRETOR || raw.NOME_DIRETORCLN || hospData.responsavel || '—';
  if (dir !== '—' && /^[\\d\\.\\-]+$/.test(dir)) dir = '—';
  const mantenedora = raw.NO_RAZAO_SOCIAL ? `${raw.NO_RAZAO_SOCIAL} (CNPJ: ${raw.NU_CNPJ_MANTENEDORA || '—'})` : '—';
  
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
  const latlon = (lat && lon) ? `<a href="https://maps.google.com/?q=${lat},${lon}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">${lat}, ${lon} ↗</a>` : 'Não informado';
  const dtAtualizacao = raw["TO_CHAR(DT_ATUALIZACAO,'DD/MM/YYYY')"] || '—';

  document.getElementById('hosp-info-card').innerHTML = `
    <div class="info-grid">
      <div class="info-item"><label>Nome Completo</label><span>${hospData.nome || '—'}</span></div>
      <div class="info-item"><label>Código CNES</label><span><a href="${linkCnes}" target="_blank" style="color:var(--accent-cyan); text-decoration:none;">${cnesId} ↗</a></span></div>
      <div class="info-item"><label>Mantenedora</label><span>${mantenedora}</span></div>
      <div class="info-item"><label>Responsável Técnico</label><span style="color:var(--accent-cyan)">${dir}</span></div>
      <div class="info-item"><label>Endereço Completo</label><span>${enderecoCompleto}</span></div>
      <div class="info-item"><label>Município</label><span>${hospData.municipio || '—'}</span></div>
      <div class="info-item"><label>Telefone</label><span>${tel}</span></div>
      <div class="info-item"><label>E-mail</label><span>${email}</span></div>
      <div class="info-item"><label>Latitude / Longitude</label><span>${latlon}</span></div>
    </div>
    <div style="margin-top:15px; padding-top:12px; border-top:1px solid var(--border); font-size:11px; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center;">
      <span><strong>Transparência de Dados:</strong> Todos os detalhes extraídos nativamente da tabela <code>tbEstabelecimento</code> via Extrato CSV DATASUS mensal.</span>
      <span>Última atualização no CNES: ${dtAtualizacao}</span>
    </div>
  `;

  let offlineAdvanced = '';
  const advData = hospData;
  
  if (advData.equipamentos && advData.equipamentos.length) {
    offlineAdvanced += \`
    <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
        <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Equipamentos</div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; font-size:11px;">
            \${advData.equipamentos.map(x => \`<div><strong style="color:var(--text-secondary)">\${x.nome}</strong>: \${x.quantidade}</div>\`).join('')}
        </div>
    </div>\`;
  }
  
  if (advData.leitos && advData.leitos.length) {
    offlineAdvanced += \`
    <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
        <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Leitos Hospitalares</div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; font-size:11px;">
            \${advData.leitos.map(x => \`<div><strong style="color:var(--text-secondary)">\${x.nome}</strong>: \${x.quantidade}</div>\`).join('')}
        </div>
    </div>\`;
  }
  
  if (advData.atendimentoPrestado && advData.atendimentoPrestado.length) {
      offlineAdvanced += \`
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Atendimento Prestado</div>
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
              \${advData.atendimentoPrestado.map(x => typeof x === 'object' ? \`<span class="status-badge" style="font-size:10px;">\${x.tipo || x}</span>\` : \`<span class="status-badge" style="font-size:10px;">\${x}</span>\`).join('')}
          </div>
      </div>\`;
  }

  if (advData.instalacoesFisicas && advData.instalacoesFisicas.length) {
      offlineAdvanced += \`
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Instalações Físicas para Assistência</div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; font-size:11px;">
              \${advData.instalacoesFisicas.map(x => typeof x === 'object' ? \`<div><strong style="color:var(--text-secondary)">\${x.tipo}</strong>: \${x.qt}</div>\` : \`<div><strong style="color:var(--text-secondary)">\${x}</strong></div>\`).join('')}
          </div>
      </div>\`;
  }
  
  if (advData.servicosEspecializados && advData.servicosEspecializados.length) {
      offlineAdvanced += \`
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Serviços Especializados</div>
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
              \${advData.servicosEspecializados.map(x => typeof x === 'object' ? \`<span class="status-badge" style="font-size:10px; background:rgba(0,0,0,0.2);">\${x.tipo || x}</span>\` : \`<span class="status-badge" style="font-size:10px; background:rgba(0,0,0,0.2);">\${x}</span>\`).join('')}
          </div>
      </div>\`;
  }

  if (advData.comissoes && advData.comissoes.length) {
      offlineAdvanced += \`
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Comissões e Comitês</div>
          <ul style="margin:0; padding-left:15px; font-size:11px; color:var(--text-secondary);">
              \${advData.comissoes.map(x => typeof x === 'object' ? \`<li>\${x.tipo || x}</li>\` : \`<li>\${x}</li>\`).join('')}
          </ul>
      </div>\`;
  }
  
  document.getElementById('hosp-rec-card').innerHTML = offlineAdvanced;

  // Carregar Proxy Live Assíncrono (Fall-back)
  document.getElementById('hosp-rec-card').innerHTML += '<div id="live-proxy-loading" class="loading-state" style="padding:10px; font-size:12px;">Puxando Nuvem Governamental...</div>';
  fetchAPI(\`/hospitais/\${cnesId}/live\`).then(live => {
    if (live && live.status === 'sucesso' && live.dados) {
      const d = live.dados;
      const loadingEl = document.getElementById('live-proxy-loading');
      if (loadingEl) loadingEl.remove();
      
      let extraHtml = \`
        <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px; display:flex; justify-content:space-between;">
              <span>Caracterização Avançada</span>
              <span style="font-size:10px; color:var(--text-muted); background:var(--bg-body); padding:2px 6px; border-radius:4px; border:1px solid var(--border-color);">\${live.origem === 'cache_local' ? '⚡ Local Cache' : '🌐 Scraping DATASUS'}</span>
          </div>
          <div class="info-grid">
            <div class="info-item"><label>Natureza Jurídica</label><span>\${d.natJuridica || '—'}</span></div>
            <div class="info-item"><label>Atividade Ensino</label><span>\${d.atividadeEnsino || '—'}</span></div>
            <div class="info-item"><label>Responsável Téc. (Live)</label><span style="color:var(--accent-cyan); font-weight:bold">\${d.diretorNome || '—'}</span></div>
            <div class="info-item"><label>Plantão 24h</label><span style="color:var(--accent-green); font-weight:bold;">\${d.tpSempreAberto === 'S' ? 'Sim' : 'Não'}</span></div>
          </div>
        </div>
      \`;
      document.getElementById('hosp-rec-card').innerHTML += extraHtml;
    } else {
      const loadingEl = document.getElementById('live-proxy-loading');
      if (loadingEl) loadingEl.innerHTML = '<div style="font-size:11px; color:var(--text-muted); padding:10px;">Caracterização governamental (Live) indisponível. Offline fallback em uso.</div>';
    }
  }).catch(err => {
    const loadingEl = document.getElementById('live-proxy-loading');
    if (loadingEl) loadingEl.innerHTML = '<div style="font-size:11px; color:var(--text-muted); padding:10px;">Falha ao obter recursos online.</div>';
  });

  document.getElementById('prof-table-wrap').innerHTML = '<div class="loading-state">Carregando médicos...</div>';
  const data = await fetchAPI(\`/hospitais/\${cnesId}\`).catch(() => null);

  if (!data) { document.getElementById('prof-table-wrap').innerHTML = '<div class="empty-state"><p>Erro ao carregar profissionais.</p></div>'; return; }

  document.getElementById('prof-fonte-text').innerHTML = fonteChip(data.fonte);
  document.getElementById('prof-count').textContent = \`\${data.total_medicos} médicos\`;

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
      contagemHtml = espsSorted.map(e => \`<span class="status-badge" style="background:var(--accent-purple); color:white; font-size:13px; padding:8px 14px; border-radius:8px; font-weight:600; display:inline-flex; align-items:center; gap:6px; box-shadow:0 2px 4px rgba(0,0,0,0.05); cursor:pointer;" onclick="filtrarMedicosPorEspecialidade('\${e.replace(/'/g,"\\\\\\'").replace(/"/g,"&quot;")}')">\${e} <span style="background:rgba(255,255,255,0.25); padding:2px 6px; border-radius:12px; font-size:11px;">\${contagem[e]}</span></span>\`).join('');
    } else {
      contagemHtml = '<p style="color:var(--text-muted); font-size:13px; width:100%;">Nenhuma especialidade mapeada para este hospital.</p>';
    }
    document.getElementById('hosp-esps-card').innerHTML = contagemHtml;
  }
}
"""

new_lines = lines[:start_idx] + [new_func + '\n'] + lines[end_idx:]

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS: Javascript module rewritten")
