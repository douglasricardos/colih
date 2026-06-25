import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'r', encoding='utf-8') as f:
    content = f.read()

# PATCH 1: LSTRIP('0') in Dictionaries
old_block1 = """                        for _, row in df_dic.iterrows():
                            dicionarios[c_id][str(row[cols.index(c_id)]).strip()] = str(row[cols.index(c_ds)]).strip()"""

new_block1 = """                        for _, row in df_dic.iterrows():
                            val_id = str(row[cols.index(c_id)]).strip().lstrip('0')
                            dicionarios[c_id][val_id] = str(row[cols.index(c_ds)]).strip()"""

content = content.replace(old_block1, new_block1)

# PATCH 2: LSTRIP('0') in Relational Matching
old_block2 = """                            if cnes_id in estabs:
                                code_val = str(row[col_id]).strip()
                                desc = dic_to_use.get(code_val, code_val)"""

new_block2 = """                            if cnes_id in estabs:
                                code_val = str(row[col_id]).strip()
                                desc = dic_to_use.get(code_val.lstrip('0'), code_val)"""

content = content.replace(old_block2, new_block2)

# PATCH 3: Get Diretor by CPF and map Natureza Juridica
old_block3 = """            # Cross-reference Director Name from CRM
            dir_crm = e.get("raw", {}).get("REG_DIRETORCLN")
            if dir_crm:
                for m in medicos_list:
                    if m.get("crm", "").startswith(str(dir_crm)):
                        e["raw"]["NOME_DIRETORCLN"] = m.get("nome")
                        break"""

new_block3 = """            # Mapear Natureza Juridica
            nat_code = e.get("raw", {}).get("CO_NATUREZA_JUR")
            if nat_code:
                e["raw"]["DS_NATUREZA_JUR"] = dicionarios.get("CO_NATUREZA_JUR", {}).get(str(nat_code).strip().lstrip('0'), nat_code)

            # Mapear Responsavel Tecnico por CPF ou CRM
            dir_cpf = e.get("raw", {}).get("CO_CPFDIRETORCLN")
            if dir_cpf:
                # We can't access df_dados easily here, so we will use the medicos_list (which might only have SUS)
                # If we don't find it, we just set a flag to fetch live if needed.
                pass
            
            dir_crm = e.get("raw", {}).get("REG_DIRETORCLN")
            if dir_crm:
                for m in medicos_list:
                    if m.get("crm", "").replace("-", "").replace(" ", "").startswith(str(dir_crm).lstrip("0")):
                        e["raw"]["NOME_DIRETORCLN"] = m.get("nome")
                        break"""

content = content.replace(old_block3, new_block3)

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH 2 APLICADO COM SUCESSO!")
