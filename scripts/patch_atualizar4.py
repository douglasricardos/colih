import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Use iloc for dictionary row access and add composite key for Equipamentos
old_dict_logic = """                        for _, row in df_dic.iterrows():
                            val_id = str(row[cols.index(c_id)]).strip().lstrip('0')
                            dicionarios[c_id][val_id] = str(row[cols.index(c_ds)]).strip()"""

new_dict_logic = """                        for _, row in df_dic.iterrows():
                            if c_id == "CO_EQUIPAMENTO" and "CO_TIPO_EQUIPAMENTO" in cols:
                                val_id = str(row.iloc[cols.index("CO_TIPO_EQUIPAMENTO")]).strip().lstrip('0') + "-" + str(row.iloc[cols.index("CO_EQUIPAMENTO")]).strip().lstrip('0')
                            else:
                                val_id = str(row.iloc[cols.index(c_id)]).strip().lstrip('0')
                            dicionarios[c_id][val_id] = str(row.iloc[cols.index(c_ds)]).strip()"""

content = content.replace(old_dict_logic, new_dict_logic)

# Fix 2: Use composite key lookup for Equipamentos
old_lookup_logic = """                            if cnes_id in estabs:
                                code_val = str(row[col_id]).strip()
                                desc = dic_to_use.get(code_val.lstrip('0'), code_val)
                                qt = str(row[col_qt]).strip() if pd.notnull(row[col_qt]) else "0"
                                
                                if int(float(qt)) > 0:"""

new_lookup_logic = """                            if cnes_id in estabs:
                                code_val = str(row[col_id]).strip().lstrip('0')
                                lookup_key = code_val
                                if col_id == "CO_EQUIPAMENTO" and "CO_TIPO_EQUIPAMENTO" in df_extra.columns:
                                    lookup_key = str(row["CO_TIPO_EQUIPAMENTO"]).strip().lstrip('0') + "-" + code_val
                                
                                desc = dic_to_use.get(lookup_key, code_val)
                                qt = str(row[col_qt]).strip() if pd.notnull(row[col_qt]) else "0"
                                
                                if int(float(qt)) > 0:"""

content = content.replace(old_lookup_logic, new_lookup_logic)

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH 4 APLICADO COM SUCESSO!")
