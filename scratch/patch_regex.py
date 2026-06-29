import re

with open('frontend/app.js', 'r', encoding='utf-8', errors='ignore') as f:
    d = f.read()

pattern = re.compile(r'// Links de busca manual.*?</div>\s*</div>\s*', re.DOTALL)
repl = '''// Links de busca manual
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
  '''

def replacement(match):
    # we want to replace up to the end of the linksHtml string literal assignment, which is a bit before the button
    return repl

d2 = re.sub(r'// Links de busca manual.*?</div>\s*</div>\s*', repl, d, count=1, flags=re.DOTALL)
# Actually, the string also has the buttons after `</div>` which we need to preserve. Wait, the template string ends at `</div>\n      ${status === 'pendente' ...`
# Let's match more carefully:

pattern2 = re.compile(r'// Links de busca manual\s+const btnStyle = `[^`]+`;\s+const linksHtml = `.*?</div>\s*</div>\s*`;', re.DOTALL)

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(d2)

print('Done')
