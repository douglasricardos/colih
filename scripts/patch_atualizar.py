import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """        # Parse auxiliary tables robustly
        print("Lendo tabelas avançadas (Comissões, Instalações, etc) se disponíveis...")
        tabelas_extras = {
            "comissoes": ["*Comissao*.csv"],
            "instalacoesFisicas": ["*Instalacao*.csv", "*InstFisica*.csv"],
            "atendimentoPrestado": ["*AtendimentoPrestado*.csv", "*AtendPrest*.csv"],
            "servicosEspecializados": ["*ServicoEspecializado*.csv", "*ServClass*.csv"]
        }
        for k, prefixes in tabelas_extras.items():
            for prefix in prefixes:
                for p in Path(extract_dir).glob(prefix):
                    try:
                        df_extra = pd.read_csv(p, sep=";", encoding="iso-8859-1", dtype=str)
                        df_extra.columns = [str(c).upper().strip() for c in df_extra.columns]
                        c_cnes = next((c for c in ["CO_UNIDADE", "CO_CNES", "CNES"] if c in df_extra.columns), None)
                        c_val = next((c for c in df_extra.columns if any(x in c for x in ["DS_", "NO_", "NOME", "DESC", "COMPLEMENTO", "NIVEL"])), None)
                        c_qt = next((c for c in df_extra.columns if any(x in c for x in ["QT_", "QUANTIDADE"])), None)
                        
                        if c_cnes and c_val:
                            for _, row in df_extra.iterrows():
                                cnes_id = str(row[c_cnes]).strip()
                                if cnes_id in estabs:
                                    val = str(row[c_val]).strip()
                                    if val and val != "nan":
                                        if k not in estabs[cnes_id]: estabs[cnes_id][k] = []
                                        if c_qt and pd.notna(row[c_qt]):
                                            estabs[cnes_id][k].append({"tipo": val, "qt": row[c_qt]})
                                        else:
                                            estabs[cnes_id][k].append(val)
                    except Exception:
                        pass"""

new_block = """        # Parse auxiliary tables robustly
        print("Lendo dicionarios avançados...")
        dicionarios = {}
        for p in Path(extract_dir).glob("tb*.csv"):
            if any(x in p.name.lower() for x in ["equipamento", "leito", "comissao", "instalacaofisica", "atendimentoprestado", "servicoespecializado", "classificacaoservico"]):
                try:
                    df_dic = pd.read_csv(p, sep=";", encoding="iso-8859-1", dtype=str, on_bad_lines='skip')
                    cols = [str(c).upper().strip() for c in df_dic.columns]
                    c_id = next((c for c in cols if c.startswith("CO_")), None)
                    c_ds = next((c for c in cols if c.startswith("DS_") or c.startswith("NO_")), None)
                    if c_id and c_ds:
                        if c_id not in dicionarios: dicionarios[c_id] = {}
                        for _, row in df_dic.iterrows():
                            dicionarios[c_id][str(row[cols.index(c_id)]).strip()] = str(row[cols.index(c_ds)]).strip()
                except:
                    pass

        print("Lendo relacionamentos avançados (Comissões, Instalações, Equipamentos etc) se disponíveis...")
        rels = {
            "equipamentos": ("rlEstabEquipamento*.csv", "CO_EQUIPAMENTO", "QT_EXISTENTE"),
            "leitos": ("rlEstabComplementar*.csv", "CO_LEITO", "QT_EXIST"),
            "instalacoesFisicas": ("rlEstabInstFisiAssist*.csv", "CO_INSTALACAO", "QT_INSTALACAO"),
            "comissoes": ("rlEstabComissaoOutro*.csv", "CO_COMISSAO", None),
            "atendimentoPrestado": ("rlEstabAtendPrestConv*.csv", "CO_ATENDIMENTO_PRESTADO", None),
            "servicosEspecializados": ("rlEstabServClass*.csv", "CO_SERVICO", None)
        }
        for k, (pattern, col_id, col_qt) in rels.items():
            for p in Path(extract_dir).glob(pattern):
                try:
                    df_extra = pd.read_csv(p, sep=";", encoding="iso-8859-1", dtype=str, on_bad_lines='skip')
                    df_extra.columns = [str(c).upper().strip() for c in df_extra.columns]
                    c_cnes = next((c for c in ["CO_UNIDADE", "CO_CNES", "CNES"] if c in df_extra.columns), None)
                    
                    if c_cnes and col_id in df_extra.columns:
                        dic_to_use = dicionarios.get(col_id, {})
                        if col_id == "CO_SERVICO": dic_to_use = dicionarios.get("CO_SERVICO_ESPECIALIZADO", {})

                        for _, row in df_extra.iterrows():
                            cnes_id = str(row[c_cnes]).strip()
                            if cnes_id in estabs:
                                code_val = str(row[col_id]).strip()
                                desc = dic_to_use.get(code_val, code_val)
                                
                                if k not in estabs[cnes_id]: estabs[cnes_id][k] = []
                                
                                if col_qt and col_qt in df_extra.columns and pd.notna(row[col_qt]):
                                    qt_val = str(row[col_qt]).strip()
                                    if qt_val and qt_val != "nan" and qt_val != "0" and qt_val != "0.0":
                                        estabs[cnes_id][k].append({"tipo": desc, "qt": qt_val, "nome": desc, "quantidade": qt_val})
                                else:
                                    if desc not in estabs[cnes_id][k]:
                                        estabs[cnes_id][k].append(desc)
                except Exception as ex:
                    print(f"Erro parseando {p.name}: {ex}")"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH SUCESSO!")
else:
    print("FALHA AO ENCONTRAR O BLOCO!")
