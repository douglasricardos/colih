import re

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    r"openTab(\'medicos\', document.getElementById(\'tab-btn-medicos\'));",
    "openTab('medicos', document.getElementById('tab-btn-medicos'));"
)

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    index = f.read()
index = re.sub(r'app\.js\?v=\d+', 'app.js?v=51', index)
with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(index)

print("Patch applied successfully")
