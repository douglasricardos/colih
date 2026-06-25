with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

hlc_dict_html = """
    <!-- Dicionário HLC -->
    <div style="background:var(--bg-card); padding:24px; border:1px solid var(--border-color); border-radius:8px; margin-top:24px;">
      <h3 style="margin-top:0;">Dicionário de Especialidades (De-Para) HLC</h3>
      <p style="font-size:13px; color:var(--text-secondary); margin-bottom:16px;">
        Mapeamento de especialidades do SUS para o termo oficial da gamificação HLC-9.
      </p>
      
      <div style="display:flex; gap:8px; margin-bottom:12px;">
          <input type="text" id="hlc-key-input" placeholder="Termo SUS (ex: Cardiologia)" class="filter-select" style="flex:1;">
          <input type="text" id="hlc-val-input" placeholder="Termo HLC (ex: CLÍNICA MÉDICA)" class="filter-select" style="flex:1;">
          <button class="btn-primary" onclick="adicionarHlcDict()">Adicionar</button>
      </div>

      <div class="table-wrap">
          <table id="table-hlc-dict">
              <thead><tr><th>Termo SUS</th><th>Termo HLC-9</th><th style="width:80px">Ações</th></tr></thead>
              <tbody></tbody>
          </table>
      </div>
      <div style="margin-top: 16px; text-align:right;">
          <button class="btn-secondary" onclick="salvarHlcDict()">Salvar Dicionário</button>
      </div>
    </div>
"""

if 'id="table-hlc-dict"' not in text:
    text = text.replace('<!-- Configuração Geográfica -->', hlc_dict_html + '\n    <!-- Configuração Geográfica -->')
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('HLC dict injected.')
else:
    print('HLC dict already present.')
