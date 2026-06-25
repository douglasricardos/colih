import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_unidades = """    col_unidade = next((c for c in ["CO_UNIDADE", "CO_CNES", "CNES"] if c in df_estab.columns), "CO_UNIDADE")
    unidades_salvador = set(df_estab[col_unidade].dropna().unique())"""

new_unidades = """    col_unidade = next((c for c in ["CO_UNIDADE", "CO_CNES", "CNES"] if c in df_estab.columns), "CO_UNIDADE")
    unidades_salvador = set(df_estab[col_unidade].dropna().unique())
    diretores_cpfs = set(df_estab["CO_CPFDIRETORCLN"].dropna().unique()) if "CO_CPFDIRETORCLN" in df_estab.columns else set()"""
content = content.replace(old_unidades, new_unidades)

old_nomes = """    prof_nomes = {}
    prof_cns = {}
    with open(csv_dados, "r", encoding="iso-8859-1") as f:
        reader = csv.DictReader(f, delimiter=";")
        for i, row in enumerate(reader):
            if i % 10000 == 0:
                time.sleep(0.001) # Yield CPU
            if i % 500000 == 0:
                prog = 50 + int(min(50, (i / 6000000) * 50))
                det = f"Cruzando Nomes e CNS de Profissionais... (Linha {i:,} de ~6.000.000)"
                save_sync_status("verificando", [], progresso=prog, detalhes=det, url_fonte=url)
                
            pid = row.get("CO_PROFISSIONAL_SUS")
            if pid in prof_sus_ids:
                prof_nomes[pid] = row.get("NOME_PROF") or row.get("NO_PROF") or row.get("NOME") or row.get("NO_PROFISSIONAL")
                prof_cns[pid] = row.get("CO_CNS") or row.get("CNS_PROF") or row.get("CNS") or row.get("NU_CNS") or ""
                
    for c in prof_cargas:"""

new_nomes = """    prof_nomes = {}
    prof_cns = {}
    cpf_nomes = {}
    with open(csv_dados, "r", encoding="iso-8859-1") as f:
        reader = csv.DictReader(f, delimiter=";")
        for i, row in enumerate(reader):
            if i % 10000 == 0:
                time.sleep(0.001) # Yield CPU
            if i % 500000 == 0:
                prog = 50 + int(min(50, (i / 6000000) * 50))
                det = f"Cruzando Nomes e CNS de Profissionais... (Linha {i:,} de ~6.000.000)"
                save_sync_status("verificando", [], progresso=prog, detalhes=det, url_fonte=url)
                
            pid = row.get("CO_PROFISSIONAL_SUS")
            nome = row.get("NOME_PROF") or row.get("NO_PROF") or row.get("NOME") or row.get("NO_PROFISSIONAL")
            if pid in prof_sus_ids:
                prof_nomes[pid] = nome
                prof_cns[pid] = row.get("CO_CNS") or row.get("CNS_PROF") or row.get("CNS") or row.get("NU_CNS") or ""
            
            cpf = row.get("CO_CPF")
            if cpf and cpf in diretores_cpfs:
                cpf_nomes[cpf] = nome
                
    if "CO_CPFDIRETORCLN" in df_estab.columns:
        df_estab["NOME_DIRETORCLN"] = df_estab["CO_CPFDIRETORCLN"].map(cpf_nomes)
                
    for c in prof_cargas:"""
content = content.replace(old_nomes, new_nomes)

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("PATCH 7 APLICADO")
