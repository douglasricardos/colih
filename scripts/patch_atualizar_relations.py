import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_dics = '            if any(x in p.name.lower() for x in ["equipamento", "leito", "comissao", "instalacaofisica", "atendimentoprestado", "servicoespecializado", "classificacaoservico", "naturezajuridica"]):'

new_dics = '            if any(x in p.name.lower() for x in ["equipamento", "leito", "comissao", "instalacaofisica", "atendimentoprestado", "servicoespecializado", "classificacaoservico", "naturezajuridica", "convenio"]):'

old_rels = """        rels = {
            "equipamentos": ("rlEstabEquipamento*.csv", "CO_EQUIPAMENTO", "QT_EXISTENTE"),
            "leitos": ("rlEstabComplementar*.csv", "CO_LEITO", "QT_EXIST"),
            "instalacoesFisicas": ("rlEstabInstFisiAssist*.csv", "CO_INSTALACAO", "QT_INSTALACAO"),
            "comissoes": ("rlEstabComissaoOutro*.csv", "CO_COMISSAO", None),
            "atendimentoPrestado": ("rlEstabAtendPrestConv*.csv", "CO_ATENDIMENTO_PRESTADO", None),
            "servicosEspecializados": ("rlEstabServClass*.csv", "CO_SERVICO", None)
        }"""

new_rels = """        rels = {
            "equipamentos": ("rlEstabEquipamento*.csv", "CO_EQUIPAMENTO", "QT_EXISTENTE"),
            "leitos": ("rlEstabComplementar*.csv", "CO_LEITO", "QT_EXIST"),
            "instalacoesFisicas": ("rlEstabInstFisiAssist*.csv", "CO_INSTALACAO", "QT_INSTALACAO"),
            "comissoes": ("rlEstabComissaoOutro*.csv", "CO_COMISSAO", None),
            "atendimentoPrestado": ("rlEstabAtendPrestConv*.csv", "CO_ATENDIMENTO_PRESTADO", None),
            "convenios": ("rlEstabAtendPrestConv*.csv", "CO_CONVENIO", None),
            "servicosEspecializados": ("rlEstabServClass*.csv", "CO_SERVICO", None)
        }"""

old_append = """                                if col_qt and col_qt in df_extra.columns and pd.notna(row[col_qt]):
                                    qt_val = str(row[col_qt]).strip()
                                    if qt_val and qt_val != "nan" and qt_val != "0" and qt_val != "0.0":
                                        estabs[cnes_id][k].append({"tipo": desc, "qt": qt_val, "nome": desc, "quantidade": qt_val})
                                else:
                                    if desc not in estabs[cnes_id][k]:
                                        estabs[cnes_id][k].append(desc)"""

new_append = """                                if k == "equipamentos":
                                    qt_existente = str(row.get("QT_EXISTENTE", "")).strip()
                                    qt_uso = str(row.get("QT_USO", "")).strip()
                                    tp_sus = "SIM" if str(row.get("TP_SUS", "")).strip() == "1" else "NÃO"
                                    if qt_existente and qt_existente != "nan" and qt_existente != "0" and qt_existente != "0.0":
                                        estabs[cnes_id][k].append({"tipo": desc, "nome": desc, "quantidade": qt_existente, "existente": qt_existente, "em_uso": qt_uso, "sus": tp_sus})
                                elif col_qt and col_qt in df_extra.columns and pd.notna(row[col_qt]):
                                    qt_val = str(row[col_qt]).strip()
                                    if qt_val and qt_val != "nan" and qt_val != "0" and qt_val != "0.0":
                                        estabs[cnes_id][k].append({"tipo": desc, "qt": qt_val, "nome": desc, "quantidade": qt_val})
                                else:
                                    if desc not in estabs[cnes_id][k]:
                                        estabs[cnes_id][k].append(desc)"""

if old_dics in code and old_rels in code and old_append in code:
    code = code.replace(old_dics, new_dics)
    code = code.replace(old_rels, new_rels)
    code = code.replace(old_append, new_append)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("PATCH APPLIED!")
else:
    print("FAILED TO PATCH")
