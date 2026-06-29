import sys
with open('frontend/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix limite=500 -> limite=0
content = content.replace("limite=500", "limite=0")

# 2. Fix Doctoralia block
old_doc_block = """  // Doctoralia block
  let docBlock = '';
  if (doc.status === 'encontrado') {
    const rating = doc.avaliacao ? `★ ${doc.avaliacao} (${doc.total_avaliacoes || 0} avaliações)` : '';
    const esps = (doc.especialidades_doctoralia || []).join(', ') || '—';
    const consultorios = (doc.consultorios || []).map(c =>
      `<div style="font-size:12px;color:var(--text-secondary);margin-bottom:2px;"> <strong>${c.nome || ''}</strong> • ${c.endereco || ''}, ${c.cidade || ''} ${c.telefone ? '· ' + c.telefone : ''}</div>`
    ).join('');
    const convenios = (doc.convenios || []).filter(Boolean).slice(0, 6).join(', ');
    const crmDoc = doc.crm_doctoralia ? `<div><label style="font-size:11px;color:var(--text-muted);font-weight:700;text-transform:uppercase;">CRM (Doctoralia)</label><div style="font-size:13px;font-weight:700;color:var(--accent-green);">${doc.crm_doctoralia}</div></div>` : '';
    docBlock = `
      <div style="margin-top:0px;">
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
  }"""

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
  }"""
if old_doc_block in content:
    content = content.replace(old_doc_block, new_doc_block)
else:
    print("Warning: could not find old_doc_block")

# 3. Fix manual links
old_links_block = """  // Links de busca manual
  const btnStyle = `style="display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none;border:1px solid var(--border-color);color:var(--text-primary);background:var(--bg-body);cursor:pointer;"`;
  const linksHtml = `
    <div style="border-top:1px solid var(--border-color);margin-top:16px;padding-top:16px;">
      <div style="font-size:12px;font-weight:700;color:var(--text-muted);margin-bottom:10px;">🔗 VERIFICAR MANUALMENTE</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">
        ${links.cfm ? `<a href="${links.cfm}" target="_blank" ${btnStyle}> CFM Portal</a>` : ''}
        ${links.cfm_crm ? `<a href="${links.cfm_crm}" target="_blank" ${btnStyle}>🔢 CFM por CRM</a>` : ''}
        ${links.doctoralia ? `<a href="${links.doctoralia}" target="_blank" ${btnStyle}>🩺 Doctoralia</a>` : ''}
        ${links.escavador ? `<a href="${links.escavador}" target="_blank" ${btnStyle}>📄 Escavador</a>` : ''}
        ${links.lattes ? `<a href="${links.lattes}" target="_blank" ${btnStyle}>🎓 Lattes</a>` : ''}
        ${links.google_medico ? `<a href="${links.google_medico}" target="_blank" ${btnStyle}>🔍 Google</a>` : ''}
      </div>
    </div>
  `;"""

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
    </div>
  `;"""
if old_links_block in content:
    content = content.replace(old_links_block, new_links_block)
else:
    print("Warning: could not find old_links_block")

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done patching app.js fully")
