import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """  let offlineAdvanced = '';
  const advData = hospData;
  
  if (advData.equipamentos && advData.equipamentos.length) {
    offlineAdvanced += `
    <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
        <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Equipamentos</div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; font-size:11px;">
            ${advData.equipamentos.map(x => `<div><strong style="color:var(--text-secondary)">${x.nome}</strong>: ${x.quantidade}</div>`).join('')}
        </div>
    </div>`;
  }
  
  if (advData.leitos && advData.leitos.length) {
    offlineAdvanced += `
    <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
        <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Leitos Hospitalares</div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; font-size:11px;">
            ${advData.leitos.map(x => `<div><strong style="color:var(--text-secondary)">${x.nome}</strong>: ${x.quantidade}</div>`).join('')}
        </div>
    </div>`;
  }
  
  if (advData.atendimentoPrestado && advData.atendimentoPrestado.length) {
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Atendimento Prestado</div>
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${advData.atendimentoPrestado.map(x => typeof x === 'object' ? `<span class="status-badge" style="font-size:10px;">${x.tipo || x}</span>` : `<span class="status-badge" style="font-size:10px;">${x}</span>`).join('')}
          </div>
      </div>`;
  }

  if (advData.instalacoesFisicas && advData.instalacoesFisicas.length) {
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Instalações Físicas para Assistência</div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; font-size:11px;">
              ${advData.instalacoesFisicas.map(x => typeof x === 'object' ? `<div><strong style="color:var(--text-secondary)">${x.tipo}</strong>: ${x.qt}</div>` : `<div><strong style="color:var(--text-secondary)">${x}</strong></div>`).join('')}
          </div>
      </div>`;
  }
  
  if (advData.servicosEspecializados && advData.servicosEspecializados.length) {
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Serviços Especializados</div>
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${advData.servicosEspecializados.map(x => typeof x === 'object' ? `<span class="status-badge" style="font-size:10px; background:rgba(0,0,0,0.2);">${x.tipo || x}</span>` : `<span class="status-badge" style="font-size:10px; background:rgba(0,0,0,0.2);">${x}</span>`).join('')}
          </div>
      </div>`;
  }

  if (advData.comissoes && advData.comissoes.length) {
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:12px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Comissões e Comitês</div>
          <ul style="margin:0; padding-left:15px; font-size:11px; color:var(--text-secondary);">
              ${advData.comissoes.map(x => typeof x === 'object' ? `<li>${x.tipo || x}</li>` : `<li>${x}</li>`).join('')}
          </ul>
      </div>`;
  }
  
  document.getElementById('hosp-rec-card').innerHTML = offlineAdvanced;"""

new_block = """  let offlineAdvanced = '';
  const advData = hospData;
  let cellSaverBadge = '';
  
  if (advData.equipamentos && advData.equipamentos.length) {
      const temCellSaver = advData.equipamentos.some(x => {
          const n = (x.nome || '').toLowerCase();
          return n.includes('circulacao extracorporea') || n.includes('aferese') || n.includes('hemoderivados');
      });
      if (temCellSaver) {
          cellSaverBadge = `<div style="background:var(--accent-red); color:white; padding:8px 12px; border-radius:6px; font-size:12px; font-weight:bold; margin-bottom:15px; display:flex; align-items:center; gap:8px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);">
              <span style="font-size:16px;">🩸</span> <span>ALERTA COLIH: Hospital possui equipamento compatível com Cell Saver / Recuperação Intraoperatória (Aférese / Circulação Extracorpórea)</span>
          </div>`;
      }
  }
  
  document.getElementById('hosp-rec-card').innerHTML = cellSaverBadge;
  
  if (advData.servicosEspecializados && advData.servicosEspecializados.length) {
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:13px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Serviços Especializados</div>
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${advData.servicosEspecializados.map(x => typeof x === 'object' ? `<span class="status-badge" style="font-size:11px; background:rgba(0,0,0,0.2); padding:4px 8px;">${x.tipo || x}</span>` : `<span class="status-badge" style="font-size:11px; background:rgba(0,0,0,0.2); padding:4px 8px;">${x}</span>`).join('')}
          </div>
      </div>`;
  }

  if (advData.comissoes && advData.comissoes.length) {
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:13px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Comissões e Comitês</div>
          <ul style="margin:0; padding-left:15px; font-size:12px; color:var(--text-secondary);">
              ${advData.comissoes.map(x => typeof x === 'object' ? `<li>${x.tipo || x}</li>` : `<li>${x}</li>`).join('')}
          </ul>
      </div>`;
  }
  
  if (advData.atendimentoPrestado && advData.atendimentoPrestado.length) {
      offlineAdvanced += `
      <div style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px;">
          <div style="font-size:13px; font-weight:600; color:var(--accent-purple); margin-bottom:8px;">Atendimento Prestado</div>
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
              ${advData.atendimentoPrestado.map(x => typeof x === 'object' ? `<span class="status-badge" style="font-size:11px;">${x.tipo || x}</span>` : `<span class="status-badge" style="font-size:11px;">${x}</span>`).join('')}
          </div>
      </div>`;
  }
  
  if (advData.leitos && advData.leitos.length) {
    offlineAdvanced += `
    <details style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px; cursor:pointer;">
        <summary style="font-size:13px; font-weight:600; color:var(--accent-purple); outline:none; user-select:none;">Leitos Hospitalares <span style="font-size:11px; font-weight:normal; color:var(--text-muted); float:right; margin-top:2px;">(Expandir/Recolher)</span></summary>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:12px; margin-top:12px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.05);">
            ${advData.leitos.map(x => `<div><strong style="color:var(--text-secondary)">${x.nome}</strong>: ${x.quantidade}</div>`).join('')}
        </div>
    </details>`;
  }

  if (advData.equipamentos && advData.equipamentos.length) {
    offlineAdvanced += `
    <details style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px; cursor:pointer;">
        <summary style="font-size:13px; font-weight:600; color:var(--accent-purple); outline:none; user-select:none;">Equipamentos <span style="font-size:11px; font-weight:normal; color:var(--text-muted); float:right; margin-top:2px;">(Expandir/Recolher)</span></summary>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:12px; margin-top:12px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.05);">
            ${advData.equipamentos.map(x => `<div><strong style="color:var(--text-secondary)">${x.nome}</strong>: ${x.quantidade}</div>`).join('')}
        </div>
    </details>`;
  }
  
  document.getElementById('hosp-rec-card').innerHTML += offlineAdvanced;"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH UI APLICADO!")
else:
    print("STRING NAO ENCONTRADA")
