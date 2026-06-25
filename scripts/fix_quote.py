path = r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = "const btn = document.querySelector('button[onclick=\"switchTab('tab-hosp-prof', this)\"]');"
new = "const btn = document.querySelector(`button[onclick=\"switchTab('tab-hosp-prof', this)\"]`);"
content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
