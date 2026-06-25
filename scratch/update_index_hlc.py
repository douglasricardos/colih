import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_html = r'''<div style="display:flex; gap:10px; margin-bottom:15px;">
            <input type="text" id="hlc-key-input" placeholder="Especialidade CNES (Ex: CARDIOLOGIA)" style="flex:1; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
            <input type="text" id="hlc-val-input" placeholder="Termo HLC-9 (Ex: CLÍNICA MÉDICA)" style="flex:1; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
            <button class="btn-primary" onclick="adicionarHlcDict()">Adicionar</button>
        </div>'''

new_html = '''<div style="display:flex; gap:10px; margin-bottom:15px;">
            <input type="text" id="hlc-key-input" list="cnes-especialidades-list" placeholder="Especialidade CNES (Pesquise...)" style="flex:1; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
            <datalist id="cnes-especialidades-list"></datalist>
            
            <input type="text" id="hlc-val-input" list="hlc-alvos-list" placeholder="Classificação HLC-9 (Ex: Cirurgia Geral)" style="flex:1; padding:10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-input); color:var(--text-primary);">
            <datalist id="hlc-alvos-list">
                <option value="Cirurgia Geral">
                <option value="Cirurgia Cardiovascular">
                <option value="Cirurgia Torácica">
                <option value="Ortopedia">
                <option value="Ginecologia e Obstetrícia">
                <option value="Anestesiologia">
                <option value="Medicina Intensiva">
                <option value="Hematologia">
                <option value="Oncologia">
                <option value="Cirurgia Oncológica">
                <option value="Gastroenterologia">
                <option value="Cirurgia do Aparelho Digestivo">
                <option value="Neurocirurgia">
                <option value="Urologia">
                <option value="Pediatria">
                <option value="Neonatologia">
                <option value="Cirurgia Pediátrica">
                <option value="Cirurgia Vascular">
                <option value="Cirurgia de Cabeça e Pescoço">
                <option value="Cirurgia Bucomaxilofacial">
                <option value="Otorrinolaringologia">
                <option value="Clínica Médica">
            </datalist>
            
            <button id="btn-adicionar-hlc" class="btn-primary" onclick="adicionarHlcDict()">Adicionar</button>
        </div>'''

text = text.replace(old_html, new_html)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('index.html updated with datalists')
