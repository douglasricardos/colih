import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = 'if name.endswith(\'.csv\') and ("tbEstab" in name or "tbCarga" in name or "tbDadosP" in name or "rlEstab" in name):'
new_logic = 'if name.endswith(\'.csv\') and (name.startswith("tb") or name.startswith("rl")):'

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH 6 APLICADO COM SUCESSO!")
else:
    print("NAO ENCONTROU A STRING")
