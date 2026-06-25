import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_card = """    <div class="info-grid">
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

new_card = """    <div class="info-grid">
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

if old_card in js:
    js = js.replace(old_card, new_card)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("FIXED")
else:
    print("FAILED")
