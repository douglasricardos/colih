import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_list = '["equipamento", "leito", "comissao", "instalacaofisica", "atendimentoprestado", "servicoespecializado", "classificacaoservico"]'
new_list = '["equipamento", "leito", "comissao", "instalacaofisica", "atendimentoprestado", "servicoespecializado", "classificacaoservico", "naturezajuridica"]'

content = content.replace(old_list, new_list)

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH 5 (Natureza Juridica whitelist) APLICADO!")
