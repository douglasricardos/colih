import sys

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if skip:
        if "    </div>" in line and "`;" in lines[i+1]:
            # This is the end of the linksHtml block
            skip = False
            # skip the "`;" line too
            continue
        if "  `;" in line and "}" in lines[i+1]:
            skip = False
            continue
        continue

    # 1. limite=500 -> limite=0
    if "limite=500" in line:
        line = line.replace("limite=500", "limite=0")

    # 2. Doctoralia Block
    if "// Doctoralia block" in line:
        # We replace the Doctoralia block
        skip = True
        new_doc_block = """  // Doctoralia block
  let docBlock = '';
  if (doc.status === 'encontrado') {
    const rating = doc.avaliacao ? `★ ${doc.avaliacao} (${doc.total_avaliacoes || 0} avaliações)` : '';
    const esps = (doc.especialidades_doctoralia && doc.especialidades_doctoralia.length > 0) ? doc.especialidades_doctoralia.join(', ') : '';
    const consultorios = (doc.consultorios || []).map(c =>
      `<div style="font-size:12px;color:var(--text-secondary);margin-bottom:2px;"> <strong>${c.nome || ''}</strong> • ${c.endereco || ''}, ${c.cidade || ''} ${c.telefone ? '· ' + c.telefone : ''}</div>`
    ).join('');
    const convenios = (doc.convenios || []).filter(Boolean).slice(0, 6).join(', ');
    const crmDoc = doc.crm_doctoralia ? `<div><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;">CRM (Doctoralia)</label><div style="font-size:13px;font-weight:700;color:var(--accent-green);">${doc.crm_doctoralia}</div></div>` : '';
    
    const hasData = crmDoc || doc.rqe || esps || rating || consultorios || convenios;

    if (hasData) {
      docBlock = `
        <div style="margin-top:0px;">
          <div style="font-size:12px;font-weight:800;color:var(--accent-purple);text-transform:uppercase;margin-bottom:10px;">🩺 Doctoralia</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
            ${crmDoc}
            ${doc.rqe ? `<div><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;">RQE</label><div style="font-size:13px;font-weight:600;">${doc.rqe}</div></div>` : ''}
            ${esps ? `<div style="grid-column:1/-1;"><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;">Especialidades</label><div style="font-size:13px;">${esps}</div></div>` : ''}
            ${rating ? `<div style="grid-column:1/-1;font-size:13px;color:var(--accent-yellow,#f59e0b);">${rating}</div>` : ''}
          </div>
          ${consultorios ? `<div style="margin-bottom:10px;"><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;display:block;margin-bottom:6px;">Consultórios</label>${consultorios}</div>` : ''}
          ${convenios ? `<div><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;display:block;margin-bottom:4px;">Convênios</label><div style="font-size:12px;color:var(--text-secondary);">${convenios}</div></div>` : ''}
          <a href="${doc.doctoralia_url || links.doctoralia || '#'}" target="_blank" style="display:inline-block;margin-top:12px;font-size:12px;color:var(--accent-cyan);text-decoration:none;font-weight:700;">Ver perfil completo na Doctoralia ↗</a>
        </div>`;
    } else {
      docBlock = `
        <div style="margin-top:0px;">
          <div style="font-size:12px;font-weight:800;color:var(--accent-purple);text-transform:uppercase;margin-bottom:10px;">🩺 Doctoralia</div>
          <div style="font-size:13px;color:var(--text-secondary);margin-bottom:12px;">Perfil básico (sem dados adicionais extraídos automaticamente).</div>
          <a href="${doc.doctoralia_url || links.doctoralia || '#'}" target="_blank" style="display:inline-block;font-size:12px;color:var(--accent-cyan);text-decoration:none;font-weight:700;">Abrir perfil na Doctoralia ↗</a>
        </div>`;
    }
  }
"""
        new_lines.append(new_doc_block)
        continue

    # 3. Manual Links Block
    if "// Links de busca manual" in line:
        skip = True
        new_links_block = """  // Links de busca manual
  const btnStyle = `style="display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none;border:1px solid var(--border-color);color:var(--text-primary);background:var(--bg-body);cursor:pointer;"`;
  const nomeEnc = encodeURIComponent(m.nome || '');
  const linksHtml = `
    <div style="border-top:1px solid var(--border-color);margin-top:16px;padding-top:16px;">
      <div style="font-size:12px;font-weight:700;color:var(--text-muted);margin-bottom:10px;">🔗 VERIFICAR MANUALMENTE</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">
        <a href="https://portal.cfm.org.br/busca-medicos/?nome=${nomeEnc}" target="_blank" ${btnStyle}>🏛️ CFM Portal</a>
        <a href="https://www.escavador.com/busca?q=${nomeEnc}" target="_blank" ${btnStyle}>📄 Escavador</a>
        <a href="https://www.google.com/search?q=site:lattes.cnpq.br+%22${nomeEnc}%22" target="_blank" ${btnStyle}>🎓 Lattes</a>
        <a href="https://www.google.com/search?q=%22${nomeEnc}%22+instagram+medico" target="_blank" ${btnStyle}>📸 Instagram</a>
        <a href="https://www.google.com/search?q=%22${nomeEnc}%22+medico" target="_blank" ${btnStyle}>🔍 Google</a>
      </div>
      ${status === 'pendente' ? `
        <button onclick="enriquecerMedico('${m.cns}')" style="margin-top:12px;padding:6px 14px;background:var(--accent-purple);color:white;border:none;border-radius:6px;font-size:12px;font-weight:700;cursor:pointer;" id="btn-enriquecer-${m.cns}">
          ⚡ Buscar dados automaticamente (Doctoralia + Lattes)
        </button>` : `
        <button onclick="enriquecerMedico('${m.cns}')" style="margin-top:12px;padding:6px 14px;background:rgba(255,255,255,0.1);color:var(--text-secondary);border:1px dashed var(--border-color);border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;" id="btn-enriquecer-${m.cns}">
          🔄 Tentar buscar dados novamente
        </button>`}
    </div>
  `;
"""
        new_lines.append(new_links_block)
        continue
    
    new_lines.append(line)

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Done")
