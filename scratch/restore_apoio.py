import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_apoio = r'<section class="tab-panel" id="tab-config-apoio">.*?</section>'
new_apoio = '''<section class="tab-panel" id="tab-config-apoio">
    <div class="panel-header">
      <h1><i data-lucide="settings-2" style="color:var(--accent-blue); vertical-align:middle; margin-right:8px;"></i> Termos de Apoio</h1>
      <p>Configure as palavras-chave para detectar equipamentos de apoio ao paciente na base de dados.</p>
    </div>
    <div style="background:var(--bg-card); padding:20px; border-radius:12px; border:1px solid var(--border-color); max-width:600px;">
        <div style="margin-bottom:15px;">
            <label style="display:block; font-weight:700; color:var(--text-secondary); margin-bottom:5px;">Termos (Separados por vírgula)</label>
            <textarea id="config-equip-termos" rows="4" style="width:100%; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary); font-size:14px;"></textarea>
        </div>
        <div style="text-align:right;">
            <button class="btn-primary" onclick="salvarConfiguracoes()" style="padding:10px 20px; font-weight:600;">Salvar Termos</button>
        </div>
    </div>
  </section>'''

text = re.sub(old_apoio, new_apoio, text, flags=re.DOTALL)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Config Apoio Tab restored.')
