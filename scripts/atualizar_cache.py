"""
COLIH Captação — Script de Atualização de Cache CNES (Resiliente)
==================================================================
Baixa os dados do CNES implementando Escada de Fallback (A -> B -> C):
  - Plano A: FTP Direto (.dbc)
  - Plano B: HTTP Direto (.dbc)
  - Plano C: ZIP Base de Dados do Portal (.zip contendo .txt)

* COM GARBAGE COLLECTOR: arquivos pesados são deletados imediatamente após extração *
"""

import json
import os
import sys
import argparse
import urllib.request
import ftplib
import tempfile
import traceback
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from collections import Counter
import pandas as pd
from dbfread import DBF
import pyreaddbc
from dateutil.relativedelta import relativedelta

DATA_DIR = Path(__file__).parent.parent / "backend" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Municípios de referência da Grande Salvador (mantido como referência para distritos)
CODIGOS_SALVADOR = {
    "292740": "Salvador",
    "291920": "Lauro de Freitas",
    "292530": "Simões Filho",
    "290570": "Camaçari",
    "291992": "Madre de Deus",
    "292370": "São Francisco do Conde",
}

# Prefixos de UF (IBGE): 29 = Bahia, 35 = SP, 33 = RJ etc.
UF_PREFIXOS = {
    "AC": "12", "AL": "27", "AM": "13", "AP": "16", "BA": "29",
    "CE": "23", "DF": "53", "ES": "32", "GO": "52", "MA": "21",
    "MG": "31", "MS": "50", "MT": "51", "PA": "15", "PB": "25",
    "PE": "26", "PI": "22", "PR": "41", "RJ": "33", "RN": "24",
    "RO": "11", "RR": "14", "RS": "43", "SC": "42", "SE": "28",
    "SP": "35", "TO": "17",
}


_IBGE_CACHE = {}
_IBGE_FETCHED_UFS = set()

def get_municipio_nome(cod_mun):
    if not cod_mun: return "N/A"
    cod = str(cod_mun)[:6]
    if cod in CODIGOS_SALVADOR: return CODIGOS_SALVADOR[cod]
    if cod in _IBGE_CACHE: return _IBGE_CACHE[cod]
    
    uf = str(cod)[:2]
    if uf not in _IBGE_FETCHED_UFS:
        _IBGE_FETCHED_UFS.add(uf)
        try:
            import requests
            resp = requests.get(f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios", timeout=5)
            if resp.status_code == 200:
                for m in resp.json():
                    _IBGE_CACHE[str(m["id"])[:6]] = m["nome"].title()
        except Exception:
            pass
            
    if cod in _IBGE_CACHE: return _IBGE_CACHE[cod]
    return cod

def get_sync_config():
    """Lê a configuração de escopo geográfico. Padrão: Bahia inteira."""
    config_file = DATA_DIR / "sync_config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Padrão: Bahia inteira
    return {"uf": "BA", "municipios_especificos": [], "descricao": "Bahia (estado completo)"}

def get_filtro_municipios():
    """Retorna um set de códigos municipais ou um prefixo de UF para filtrar a base."""
    config = get_sync_config()
    uf = config.get("uf", "BA")
    municipios = config.get("municipios_especificos", [])
    if municipios:
        return {"tipo": "lista", "codigos": set(str(m) for m in municipios)}
    uf_prefix = UF_PREFIXOS.get(uf.upper(), "29")
    return {"tipo": "prefixo", "prefixo": uf_prefix}

CBO_MEDICOS_PREFIX = "225"
CBO_NOMES = {
    "225103": "Médico infectologista", "225105": "Médico acupunturista", "225106": "Médico legista",
    "225109": "Médico nefrologista", "225112": "Médico neurologista", "225115": "Médico nutrólogo",
    "225120": "Médico cardiologista", "225121": "Médico oncologista clínico", "225122": "Médico cancerologista pediátrico",
    "225124": "Médico pediatra", "225125": "Médico clínico", "225127": "Médico pneumologista",
    "225130": "Médico de família e comunidade", "225133": "Médico psiquiatra", "225136": "Médico reumatologista",
    "225139": "Médico sanitarista", "225142": "Médico fisiatra", "225148": "Médico anatomopatologista",
    "225151": "Médico anestesiologista", "225155": "Médico endocrinologista", "225165": "Médico gastroenterologista",
    "225170": "Médico generalista", "225180": "Médico geriatra", "225225": "Médico cirurgião geral",
    "225235": "Médico cirurgião plástico", "225250": "Médico ginecologista e obstetra", "225260": "Médico neurocirurgião",
    "225265": "Médico oftalmologista", "225270": "Médico ortopedista e traumatologista", "225275": "Médico otorrinolaringologista",
    "225280": "Médico proctologista", "225285": "Médico urologista", "225305": "Médico citopatologista",
    "225310": "Médico em endoscopia", "225315": "Médico em medicina nuclear", "225320": "Médico em radiologia e diagnóstico por imagem",
    "225325": "Médico patologista", "225330": "Médico radioterapeuta"
}

def get_competencia_atual():
    now = datetime.now()
    mes = now.month - 1
    ano = now.year
    if mes == 0:
        mes = 12
        ano -= 1
    return f"{ano}{mes:02d}"

def nome_especialidade(cbo: str) -> str:
    cbo_clean = str(cbo).strip().replace(" ", "").replace("-", "")[:6]
    return CBO_NOMES.get(cbo_clean, "")

def garbage_collector(paths):
    """Exclui arquivos temporários pesados."""
    for p in paths:
        if p and os.path.exists(p):
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p)
                else:
                    os.remove(p)
                print(f"   [GC] Lixo removido: {os.path.basename(p)}")
            except Exception as e:
                print(f"   [GC] Erro ao remover {p}: {e}")

# ==============================================================================
# PLANO A: FTP DBC
# ==============================================================================
def baixar_dbc_plano_a(tipo: str, uf: str, competencia: str, destino: Path) -> Path:
    print(f"   >>> Executando PLANO A (FTP DBC) para {tipo}...")
    ftp_host = "ftp.datasus.gov.br"
    caminho_ftp = f"/dissemin/publicos/CNES/200508_/Dados/{tipo}/{tipo}{uf}{competencia}.dbc"
    destino_arquivo = destino / f"{tipo}{uf}{competencia}.dbc"
    
    with ftplib.FTP(ftp_host, timeout=20) as ftp:
        ftp.login()
        with open(destino_arquivo, "wb") as f:
            ftp.retrbinary(f"RETR {caminho_ftp}", f.write, blocksize=65536)
    return destino_arquivo

# ==============================================================================
# PLANO B: HTTP DBC
# ==============================================================================
def baixar_dbc_plano_b(tipo: str, uf: str, competencia: str, destino: Path) -> Path:
    print(f"   >>> Executando PLANO B (HTTP DBC) para {tipo}...")
    url = f"http://ftp.datasus.gov.br/dissemin/publicos/CNES/200508_/Dados/{tipo}/{tipo}{uf}{competencia}.dbc"
    destino_arquivo = destino / f"{tipo}{uf}{competencia}.dbc"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as response, open(destino_arquivo, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    return destino_arquivo

def ler_dbc(caminho_dbc: Path):
    dbf_file = str(caminho_dbc).replace(".dbc", ".dbf")
    pyreaddbc.dbc2dbf(str(caminho_dbc), dbf_file)
    table = DBF(dbf_file, encoding='iso-8859-1')
    df = pd.DataFrame(iter(table))
    garbage_collector([dbf_file])
    return df

def executar_planos_ab(competencia: str):
    """Tenta baixar e extrair usando Planos A e B."""
    df_estab = None
    df_prof = None
    temp_files = []
    config = get_sync_config()
    uf = config.get("uf", "BA")

    for plano_func in [baixar_dbc_plano_a, baixar_dbc_plano_b]:
        try:
            # Estabelecimentos
            dbc_estab = plano_func("ST", uf, competencia, Path(tempfile.gettempdir()))
            temp_files.append(dbc_estab)
            df_estab = ler_dbc(dbc_estab)
            
            # Profissionais
            dbc_prof = plano_func("PF", uf, competencia, Path(tempfile.gettempdir()))
            temp_files.append(dbc_prof)
            df_prof = ler_dbc(dbc_prof)
            
            plano_usado = "Plano A (FTP)" if plano_func == baixar_dbc_plano_a else "Plano B (HTTP)"
            garbage_collector(temp_files)
            return df_estab, df_prof, plano_usado
        except Exception as e:
            print(f"   [X] Falha no plano atual: {e}")
            garbage_collector(temp_files)
            temp_files = []
            continue
            
    raise Exception("Planos A e B esgotados.")

def get_competencias_recentes():
    hoje = datetime.now()
    # Tenta 202605, 202604, 202603 - mês atual raramente publicado, começa em -1
    return [(hoje - relativedelta(months=i)).strftime("%Y%m") for i in range(1, 4)]

# ==============================================================================
# PLANO C: HTTP ZIP (BASE DE DADOS PORTAL CNES)
# ==============================================================================
def baixar_zip_plano_c(competencia: str, temp_dir: Path):
    url = f"http://cnes.datasus.gov.br/EstatisticasServlet?path=BASE_DE_DADOS_CNES_{competencia}.ZIP"
    zip_path = temp_dir / f"BASE_{competencia}.zip"
    
    import subprocess
    import zipfile as _zipfile_module

    # NÃO apaga ZIP parcial — o resume (-C -) vai continuar de onde parou
    if zip_path.exists():
        sz_mb = zip_path.stat().st_size / 1_048_576
        print(f"   [Resume] ZIP parcial encontrado ({sz_mb:.1f} MB) — retomando download...")

    print(f"   Iniciando download do ZIP do portal CNES via curl (com resume automático)...")
    save_sync_status("verificando", [], progresso=5, detalhes="Baixando dados do CNES... Isso pode demorar vários minutos.", url_fonte=url)

    MAX_TENTATIVAS = 6
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        tamanho_antes = zip_path.stat().st_size if zip_path.exists() else 0
        if tamanho_antes > 0:
            print(f"   [Tentativa {tentativa}/{MAX_TENTATIVAS}] Retomando download a partir de {tamanho_antes/1_048_576:.1f} MB...")
            detalhe = f"Retomando download... ({tamanho_antes/1_048_576:.0f} MB já baixados)"
        else:
            print(f"   [Tentativa {tentativa}/{MAX_TENTATIVAS}] Iniciando download...")
            detalhe = "Iniciando download do CNES (ZIP ~1.5GB)..."
        save_sync_status("verificando", [], progresso=5 + tentativa, detalhes=detalhe, url_fonte=url)

        cookie_jar = temp_dir / "datasus_cookies.txt"
        curl_cmd = [
            "curl.exe", "-L",
            "-o", str(zip_path),
            "-C", "-",                    # Resume: continua de onde parou
            "--cookie-jar", str(cookie_jar),  # Salva cookies recebidos
            "--cookie", str(cookie_jar) if cookie_jar.exists() else "",  # Reenvia cookies na retomada
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "--retry", "0",               # Nós gerenciamos o retry manualmente
            "--connect-timeout", "30",    # Timeout de conexão: 30s
            "--max-time", "900",          # Timeout total por tentativa: 15 min
            "--speed-limit", "1024",      # Aborta se velocidade cair abaixo de 1KB/s
            "--speed-time", "60",         # por mais de 60 segundos (travado)
            url
        ]

        import re, time
        process = subprocess.Popen(curl_cmd, stderr=subprocess.PIPE, universal_newlines=True, text=True, bufsize=1)
        
        last_update = time.time()
        buffer = ""
        while True:
            char = process.stderr.read(1)
            if not char:
                break
            if char == '\r' or char == '\n':
                if buffer:
                    line = buffer
                    buffer = ""
                    
                    # Regex para tempos do curl: 00:00:00 ou 00:00
                    times = re.findall(r'\d\d:\d\d(?::\d\d)?', line)
                    pct_match = re.search(r'^\s*(\d+)\s+', line)
                    if pct_match:
                        pct = int(pct_match.group(1))
                        eta = ""
                        if len(times) >= 3:
                            eta = times[2]
                        elif len(times) > 0:
                            eta = times[-1] + " decorrido"
                            
                        now = time.time()
                        if now - last_update > 2:
                            pct_real = pct
                            if pct == 100 and len(times) < 3:
                                # Quando Content-Length não é enviado, % fica 100 o tempo todo
                                pct_real = 0 
                            save_sync_status("verificando", [], progresso=5 + int(pct_real * 0.35), detalhes=f"Baixando dados... ({pct_real}% concluído)", url_fonte=url, eta=eta)
                            last_update = now
            else:
                buffer += char

        process.wait()
        returncode = process.returncode
        tamanho_depois = zip_path.stat().st_size if zip_path.exists() else 0

        # Curl código 33 = servidor não suporta range/resume
        if returncode == 33:
            print(f"   [Tentativa {tentativa}] Servidor nao suporta resume.")
            # Se o arquivo ja parece grande (download completo de tentativa anterior), nao apaga
            if tamanho_depois > 400_000_000:
                print(f"   Arquivo grande ({tamanho_depois/1_048_576:.0f} MB) - verificando integridade antes de descartar...")
                try:
                    import zipfile as _zf
                    with _zf.ZipFile(zip_path, 'r') as zf:
                        bad = zf.testzip()
                    if bad is None:
                        print(f"   [OK] ZIP integro com {tamanho_depois/1_048_576:.1f} MB - usando!")
                        break
                except:
                    pass
            if zip_path.exists():
                zip_path.unlink()
            continue

        # Curl código 0 ou arquivo cresceu -> verifica integridade do ZIP
        if zip_path.exists() and tamanho_depois > 100_000_000:  # Pelo menos 100MB
            try:
                import zipfile as _zf
                with _zf.ZipFile(zip_path, 'r') as zf:
                    bad = zf.testzip()  # Retorna None se OK, ou nome do primeiro arquivo corrompido
                if bad is None:
                    print(f"   [OK] ZIP integro! ({tamanho_depois/1_048_576:.1f} MB)")
                    break  # Download completo e valido!
                else:
                    print(f"   [AVISO] ZIP corrompido (arquivo: {bad}). Removendo e reiniciando...")
                    zip_path.unlink()
            except Exception as e_zip_check:
                # ZIP ainda incompleto (EOFError = truncado) -> continua baixando na próxima tentativa
                err_str = str(e_zip_check)
                if "EOF" in err_str or "truncated" in str(type(e_zip_check).__name__).lower() or "codec" in err_str.lower():
                    print(f"   [Tentativa {tentativa}] ZIP ainda incompleto ({tamanho_depois/1_048_576:.1f} MB). Retomando...")
                else:
                    print(f"   [Tentativa {tentativa}] Erro ao verificar ZIP: {err_str}. Retomando...")
        elif returncode != 0:
            print(f"   [Tentativa {tentativa}] curl retornou código {returncode}. Retomando em 10s...")

        if tentativa < MAX_TENTATIVAS:
            import time as _time
            _time.sleep(10)
    else:
        # Esgotou todas as tentativas
        raise Exception(f"Falha no download após {MAX_TENTATIVAS} tentativas. Verifique a conexão ou tente mais tarde.")

    # ZIP válido e completo

    save_sync_status("verificando", [], progresso=40, detalhes="Download concluido. Extraindo arquivos do ZIP...", url_fonte=url)
    print(f"   Extraindo ZIP...")
    extract_dir = temp_dir / f"CNES_{competencia}"
    try:
        with _zipfile_module.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except (_zipfile_module.BadZipFile, Exception) as e_zip:
        garbage_collector([zip_path])
        raise Exception(f"ZIP corrompido, sera baixado novamente na proxima tentativa: {e_zip}")

    garbage_collector([zip_path])

    
    print(f"   Lendo CSVs com Pandas...")
    csv_estab = extract_dir / f"tbEstabelecimento{competencia}.csv"
    csv_carga = extract_dir / f"tbCargaHorariaSus{competencia}.csv"
    csv_dados = extract_dir / f"tbDadosProfissionalSus{competencia}.csv"
    csv_cbo = extract_dir / f"tbCbo{competencia}.csv"
    csv_equip = extract_dir / f"tbEquipamento{competencia}.csv"
    csv_leito = extract_dir / f"tbLeito{competencia}.csv"
    
    # Estabelecimentos (Apenas colunas úteis - expandido para pegar TUDO para o novo UI detalhado)
    cols_estab = ["CO_CNES", "CNES", "CO_UNIDADE", "NO_FANTASIA", "NOME_FANTASIA", "NOME", "CODUFMUN", "CO_MUN", "MUN", "CO_MUNICIPIO_GESTOR", "DS_ENDERECO", "LOGRADOURO", "ENDERE", "NO_LOGRADOURO"]
    df_estab = pd.read_csv(csv_estab, sep=";", encoding="iso-8859-1", dtype=str, on_bad_lines='skip')
    
    # Pré-filtro dinâmico: filtra por UF completa ou municípios específicos (config em sync_config.json)
    filtro = get_filtro_municipios()
    col_mun_estab = next((c for c in ["CODUFMUN", "CO_MUN", "MUN", "CO_MUNICIPIO_GESTOR"] if c in df_estab.columns), None)
    if col_mun_estab:
        col_str = df_estab[col_mun_estab].astype(str).str.strip()
        if filtro["tipo"] == "lista":
            df_estab = df_estab[col_str.isin(filtro["codigos"])]
        else:  # prefixo de UF
            df_estab = df_estab[col_str.str.startswith(filtro["prefixo"])]
    config_atual = get_sync_config()
    print(f"   Filtro geográfico: {config_atual.get('descricao', 'Não configurado')} -> {len(df_estab)} estabelecimentos encontrados")
    
    col_unidade = next((c for c in ["CO_UNIDADE", "CO_CNES", "CNES"] if c in df_estab.columns), "CO_UNIDADE")
    unidades_filtradas = set(df_estab[col_unidade].dropna().unique())
    # Mantemos o nome unidades_salvador para compatibilidade com o código abaixo
    unidades_salvador = unidades_filtradas
    diretores_cpfs = set(df_estab["CO_CPFDIRETORCLN"].dropna().unique()) if "CO_CPFDIRETORCLN" in df_estab.columns else set()
    
    # Profissionais (Raw CSV parsing para velocidade absurda e 0% RAM)
    import csv
    print("   Lendo Profissionais com módulo CSV puro...")
    
    prof_cargas = []
    prof_sus_ids = set()
    
    with open(csv_carga, "r", encoding="iso-8859-1") as f:
        reader = csv.DictReader(f, delimiter=";")
        import time
        for i, row in enumerate(reader):
            if i % 10000 == 0:
                time.sleep(0.001) # Yield CPU
            if i % 1000000 == 0:
                prog = int(min(50, (i / 8000000) * 50))
                det = f"Filtrando Profissionais por unidade... (Linha {i:,} de ~8.000.000)"
                # save_sync_status("verificando", [], progresso=prog, detalhes=det, url_fonte=url)
                
            u = row.get("CO_UNIDADE") or row.get("CO_CNES") or row.get("CNES")
            if u in unidades_salvador:
                prof_cargas.append(row)
                if row.get("CO_PROFISSIONAL_SUS"):
                    prof_sus_ids.add(row["CO_PROFISSIONAL_SUS"])
                    
    prof_nomes = {}
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
            # CRM: captura número de registro, tipo de conselho e UF
            crm_num  = row.get("CO_REGISTRO") or row.get("NU_REGISTRO") or ""
            crm_tipo = row.get("CO_TP_CONSELHO") or row.get("TP_CONSELHO") or ""
            crm_uf   = row.get("CO_UF_CONSELHO") or row.get("UF_CONSELHO") or ""
            if pid in prof_sus_ids:
                prof_nomes[pid] = nome
                prof_cns[pid] = row.get("CO_CNS") or row.get("CNS_PROF") or row.get("CNS") or row.get("NU_CNS") or ""
                # Armazena CRM se o tipo for CRM (código 6 = CRM no padrão CNES)
                if crm_num and crm_num.strip() != "0":
                    prof_nomes[f"{pid}__crm"] = crm_num.strip()
                    prof_nomes[f"{pid}__crm_tipo"] = crm_tipo.strip()
                    prof_nomes[f"{pid}__crm_uf"] = crm_uf.strip()
            
            cpf = row.get("CO_CPF")
            if cpf and cpf in diretores_cpfs:
                cpf_nomes[cpf] = nome
                
    if "CO_CPFDIRETORCLN" in df_estab.columns:
        df_estab["NOME_DIRETORCLN"] = df_estab["CO_CPFDIRETORCLN"].map(cpf_nomes)
                
    for c in prof_cargas:
        pid = c.get("CO_PROFISSIONAL_SUS")
        if pid in prof_nomes:
            c["NOME_PROF"] = prof_nomes[pid]
        if pid in prof_cns and prof_cns[pid]:
            c["CNS_PROF"] = prof_cns[pid]
        # Propaga CRM capturado de tbDadosProfissionalSus
        crm_val = prof_nomes.get(f"{pid}__crm", "")
        if crm_val:
            c["CRM_NUM"]  = crm_val
            c["CRM_TIPO"] = prof_nomes.get(f"{pid}__crm_tipo", "CRM")
            c["CRM_UF"]   = prof_nomes.get(f"{pid}__crm_uf", "")
            
    df_prof = pd.DataFrame(prof_cargas)
    
    # Auxiliares
    df_cbo = pd.DataFrame()
    if csv_cbo.exists():
        cols_cbo = ["CO_CBO", "CBO", "DS_CBO", "NO_CBO"]
        df_cbo = pd.read_csv(csv_cbo, sep=";", encoding="iso-8859-1", dtype=str, on_bad_lines='skip', usecols=lambda c: c.upper().strip() in cols_cbo)
        col_cbo_merge = "CO_CBO" if "CO_CBO" in df_prof.columns else "CBO"
        if col_cbo_merge in df_cbo.columns and col_cbo_merge in df_prof.columns:
            df_prof = pd.merge(df_prof, df_cbo, on=col_cbo_merge, how="left")
        del df_cbo
        
    df_equip = pd.DataFrame()
    if csv_equip.exists():
        cols_equip = ["CO_CNES", "CNES", "CO_UNIDADE", "DS_EQUIPAMENTO", "NO_EQUIPAMENTO", "QT_EQUIPAMENTO", "QUANTIDADE"]
        df_equip = pd.read_csv(csv_equip, sep=";", encoding="iso-8859-1", dtype=str, on_bad_lines='skip', usecols=lambda c: c.upper().strip() in cols_equip)
        
    df_leito = pd.DataFrame()
    if csv_leito.exists():
        cols_leito = ["CO_CNES", "CNES", "CO_UNIDADE", "DS_LEITO", "NO_LEITO", "CO_LEITO", "QT_EXIST", "QT_LEITO", "QUANTIDADE"]
        df_leito = pd.read_csv(csv_leito, sep=";", encoding="iso-8859-1", dtype=str, on_bad_lines='skip', usecols=lambda c: c.upper().strip() in cols_leito)
    
    # Limpa os arquivos extraídos pesados mas mantém os dicionários para leitura das tabelas extras
    garbage_collector([csv_estab, csv_carga, csv_dados, csv_cbo])
    
    return df_estab, df_prof, df_equip, df_leito, extract_dir, "Plano C (Portal CNES — ZIP/CSV)"

# ==============================================================================
# PROCESSADORES E NORMALIZADORES (Traduz A/B/C pro formato da COLIH)
# ==============================================================================
def processar_estabelecimentos(df, df_equip=None, df_leito=None) -> dict:
    df.columns = [str(c).upper().strip() for c in df.columns]
    
    col_cnes = next((c for c in ["CO_UNIDADE", "CO_CNES", "CNES"] if c in df.columns), None)
    col_nome = next((c for c in df.columns if c in ["NO_FANTASIA", "NOME_FANTASIA", "NOME"]), None)
    col_mun  = next((c for c in df.columns if c in ["CODUFMUN", "CO_MUN", "MUN", "CO_MUNICIPIO_GESTOR"]), None)
    col_end  = next((c for c in df.columns if c in ["DS_ENDERECO", "LOGRADOURO", "ENDERE", "NO_LOGRADOURO"]), None)
    
    filtro = get_filtro_municipios()
    if col_mun:
        col_str = df[col_mun].astype(str).str.strip()
        if filtro["tipo"] == "lista":
            df_s = df[col_str.isin(filtro["codigos"])].copy()
        else:
            df_s = df[col_str.str.startswith(filtro["prefixo"])].copy()
    else:
        df_s = df.copy()

    estabs = {}
    for _, row in df_s.iterrows():
        cnes_id = str(row[col_cnes]).strip() if col_cnes and pd.notna(row[col_cnes]) else ""
        cnes_id = cnes_id[-7:] if len(cnes_id) > 7 else cnes_id
        if not cnes_id: continue
        cod_mun = str(row.get(col_mun, "")).strip() if col_mun else ""
        # Tenta o nome amigável; cidades fora de Salvador ficam com o código IBGE até ter dicionário completo
        nome_mun = get_municipio_nome(cod_mun)
        estabs[cnes_id] = {
            "cnes": cnes_id,
            "nome": str(row[col_nome]).title() if col_nome and pd.notna(row[col_nome]) else "",
            "endereco": str(row[col_end]).title() if col_end and pd.notna(row[col_end]) else "",
            "municipio": nome_mun,
            "equipamentos": [],
            "leitos": [],
            "raw": {k: str(v).strip() for k, v in row.to_dict().items() if pd.notna(v) and str(v).strip() and k in ["NO_BAIRRO", "TP_UNIDADE", "CO_CNES", "NU_LATITUDE", "NU_LONGITUDE", "TO_CHAR(DT_ATUALIZACAO,'DD/MM/YYYY')", "TO_CHAR(DT_ATUALIZACAO_ORIGEM,'DD/MM/YYYY')", "CO_NATUREZA_JUR", "CO_MOTIVO_DESAB", "CO_CPFDIRETORCLN", "REG_DIRETORCLN", "NOME_DIRETORCLN"]}
        }
        
    # Process Equipments
    if df_equip is not None and not df_equip.empty:
        df_equip.columns = [str(c).upper().strip() for c in df_equip.columns]
        c_equip_cnes = next((c for c in ["CO_UNIDADE", "CO_CNES", "CNES"] if c in df_equip.columns), None)
        c_equip_nome = next((c for c in df_equip.columns if c in ["DS_EQUIPAMENTO", "NO_EQUIPAMENTO"]), None)
        c_equip_qtd = next((c for c in df_equip.columns if c in ["QT_EQUIPAMENTO", "QUANTIDADE"]), None)
        
        if c_equip_cnes and c_equip_nome:
            for _, row in df_equip.iterrows():
                cnes_id = str(row[c_equip_cnes]).strip()
                if cnes_id in estabs:
                    nome_eq = str(row[c_equip_nome]).title() if pd.notna(row[c_equip_nome]) else "Equipamento"
                    qtd = str(row[c_equip_qtd]).strip() if c_equip_qtd and pd.notna(row[c_equip_qtd]) else "1"
                    if qtd != "0":
                        estabs[cnes_id]["equipamentos"].append({"nome": nome_eq, "quantidade": qtd})

    # Process Beds
    if df_leito is not None and not df_leito.empty:
        df_leito.columns = [str(c).upper().strip() for c in df_leito.columns]
        c_leito_cnes = next((c for c in ["CO_UNIDADE", "CO_CNES", "CNES"] if c in df_leito.columns), None)
        c_leito_nome = next((c for c in df_leito.columns if c in ["DS_LEITO", "NO_LEITO", "CO_LEITO"]), None)
        c_leito_qtd = next((c for c in df_leito.columns if c in ["QT_EXIST", "QT_LEITO", "QUANTIDADE"]), None)
        
        if c_leito_cnes and c_leito_nome:
            for _, row in df_leito.iterrows():
                cnes_id = str(row[c_leito_cnes]).strip()
                if cnes_id in estabs:
                    nome_lt = str(row[c_leito_nome]).title() if pd.notna(row[c_leito_nome]) else "Leito"
                    qtd = str(row[c_leito_qtd]).strip() if c_leito_qtd and pd.notna(row[c_leito_qtd]) else "1"
                    if qtd != "0":
                        estabs[cnes_id]["leitos"].append({"nome": nome_lt, "quantidade": qtd})

    return estabs

def processar_profissionais(df, estabs: dict) -> list:
    df.columns = [str(c).upper().strip() for c in df.columns]
    
    col_cnes = next((c for c in ["CO_UNIDADE", "CO_CNES", "CNES"] if c in df.columns), None)
    col_cns  = next((c for c in ["CNS_PROF", "CO_CNS", "NU_CNS", "CO_PROF", "CNS", "CO_PROFISSIONAL_SUS"] if c in df.columns), None)
    col_nome = next((c for c in ["NOME_PROF", "NO_PROF", "NOME", "NO_PROFISSIONAL"] if c in df.columns), None)
    col_cbo  = next((c for c in ["CBO", "CO_CBO"] if c in df.columns), None)
    col_cbo_nome = next((c for c in ["DS_CBO", "NO_CBO"] if c in df.columns), None)
    col_mun  = next((c for c in ["CODUFMUN", "CO_MUN", "MUN"] if c in df.columns), None)
    # Campos de CRM (já propagados do tbDadosProfissionalSus na leitura)
    col_crm_num  = "CRM_NUM"  if "CRM_NUM"  in df.columns else None
    col_crm_tipo = "CRM_TIPO" if "CRM_TIPO" in df.columns else None
    col_crm_uf   = "CRM_UF"   if "CRM_UF"   in df.columns else None
    
    # Se veio do ZIP (Plano C), não tem CO_MUN no profissional, precisamos cruzar com o estabelecimento
    if not col_mun and col_cnes:
        def get_mun(cnes):
            cnes_str = str(cnes).strip()
            cnes_7 = cnes_str[-7:] if len(cnes_str) > 7 else cnes_str
            return "292740" if cnes_7 in estabs else "000000" # Filtra só os que batem com estabs já filtrados
        df['MUN_INFERIDO'] = df[col_cnes].apply(get_mun)
        col_mun = 'MUN_INFERIDO'

    # Filtro geográfico dinâmico (herda a mesma configuração do filtro de estabelecimentos)
    # Na prática o filtro já foi feito por unidades_filtradas — aqui só garantimos consistencia
    filtro = get_filtro_municipios()
    if col_mun and filtro["tipo"] == "lista" and filtro["codigos"]:
        mask_mun = df[col_mun].astype(str).str.strip().isin(filtro["codigos"])
    elif col_mun and filtro["tipo"] == "prefixo":
        mask_mun = df[col_mun].astype(str).str.strip().str.startswith(filtro["prefixo"])
    else:
        mask_mun = pd.Series([True] * len(df))
    mask_cbo = df[col_cbo].astype(str).str.strip().str.startswith(CBO_MEDICOS_PREFIX) if col_cbo else pd.Series([True] * len(df))
    df_f = df[mask_mun & mask_cbo].copy()

    # Load HLC-9 dict
    hlc9_dict = {}
    try:
        if (DATA_DIR / "hlc9_dict.json").exists():
            with open(DATA_DIR / "hlc9_dict.json", "r", encoding="utf-8") as f:
                hlc9_dict = json.load(f)
    except:
        pass

    medicos_dict = {}
    for _, row in df_f.iterrows():
        cns = str(row[col_cns]).strip() if col_cns and pd.notna(row[col_cns]) else "SEM_CNS"
        nome = str(row[col_nome]).strip().title() if col_nome and pd.notna(row[col_nome]) else ""
        cbo = str(row[col_cbo]).strip()[:6] if col_cbo and pd.notna(row[col_cbo]) else ""
        cbo_nome = str(row[col_cbo_nome]).strip().title() if col_cbo_nome and pd.notna(row[col_cbo_nome]) else ""
        cnes_id = str(row[col_cnes]).strip() if col_cnes and pd.notna(row[col_cnes]) else ""
        cnes_id = cnes_id[-7:] if len(cnes_id) > 7 else cnes_id

        # CRM: extraído do tbDadosProfissionalSus e propagado via CRM_NUM/CRM_TIPO/CRM_UF
        crm_num  = str(row["CRM_NUM"]).strip()  if col_crm_num  and pd.notna(row.get("CRM_NUM"))  and str(row.get("CRM_NUM","")).strip() not in ("","0","nan") else ""
        crm_tipo = str(row["CRM_TIPO"]).strip() if col_crm_tipo and pd.notna(row.get("CRM_TIPO")) else ""
        crm_uf   = str(row["CRM_UF"]).strip()   if col_crm_uf   and pd.notna(row.get("CRM_UF"))   else ""
        # Formata como "12345/BA" quando possível
        crm_fmt = f"{crm_num}/{crm_uf}" if crm_num and crm_uf else crm_num
        
        estab_info = estabs.get(cnes_id, {})
        nm_estab = estab_info.get("nome", f"CNES {cnes_id}" if cnes_id else "Não informado")
        
        vinculo = {
            "cnes": cnes_id,
            "estabelecimento": nm_estab,
            "municipio": estab_info.get("municipio", "Bahia"),
            "endereco": estab_info.get("endereco", ""),
            "ativo": True
        }

        esp = cbo_nome if cbo_nome else nome_especialidade(cbo)
        
        chave = cns if cns and cns != "SEM_CNS" else f"SEM_CNS_{nome}_{cnes_id}"
        if chave not in medicos_dict:
            medicos_dict[chave] = {
                "cns": cns, "cnes": cnes_id, "nome": nome,
                "crm": crm_fmt, "crm_tipo": crm_tipo, "crm_uf": crm_uf,
                "especialidades": set([esp]) if esp else set(),
                "cbos": set([cbo]) if cbo else set(),
                "vinculos": [vinculo], "fonte": "DATASUS (Portal de Dados Abertos)"
            }
        else:
            if esp:
                medicos_dict[chave]["especialidades"].add(esp)
            if cbo:
                medicos_dict[chave]["cbos"].add(cbo)
            # Atualiza CRM se ainda não tinha
            if crm_fmt and not medicos_dict[chave].get("crm"):
                medicos_dict[chave]["crm"] = crm_fmt
                medicos_dict[chave]["crm_tipo"] = crm_tipo
                medicos_dict[chave]["crm_uf"] = crm_uf
            
            # Adiciona o vínculo se ainda não existir, checando pelo CNES para não duplicar
            if not any(v["cnes"] == vinculo["cnes"] for v in medicos_dict[chave]["vinculos"]):
                medicos_dict[chave]["vinculos"].append(vinculo)


    # Processa os dicionários para gerar listas limpas
    medicos_f = list(medicos_dict.values())
    for m in medicos_f:
        esps = sorted(list(m["especialidades"]))
        m["especialidade"] = " / ".join(esps) if esps else ""
        
        cbos = sorted(list(m["cbos"]))
        m["cbo"] = " / ".join(cbos) if cbos else ""
        
        # Mapeia para HLC-9
        m["especialidade_hlc9"] = ""
        for e in esps:
            if e in hlc9_dict:
                m["especialidade_hlc9"] = hlc9_dict[e]
                break
        
        del m["especialidades"]
        del m["cbos"]

    return sorted(medicos_f, key=lambda m: m["nome"])

def save_sync_status(status_geral, planos_state=None, erro_geral=None, proxima_tentativa=None, competencia=None, progresso=None, detalhes=None, url_fonte=None, eta=None):
    if status_geral == "verificando" and progresso is None:
        progresso = 0
        
    # Preservar logs antigos e metadados se não fornecidos novos
    status_file = DATA_DIR / "sync_status.json"
    if status_file.exists():
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                if detalhes is None: detalhes = old_data.get("detalhes")
                if url_fonte is None: url_fonte = old_data.get("url_fonte")
                if not planos_state: planos_state = old_data.get("planos", [])
                if not competencia: competencia = old_data.get("competencia")
                if eta is None: eta = old_data.get("eta")
        except:
            pass
            
    if planos_state is None:
        planos_state = []

    sync_status = {
        "sucesso": status_geral == "sucesso",
        "status_geral": status_geral, # verificando, sucesso, falha_total
        "data_tentativa": datetime.now().isoformat(),
        "data_fmt": datetime.now().strftime('%d/%m/%Y %H:%M'),
        "proxima_tentativa": proxima_tentativa,
        "erro_geral": erro_geral,
        "competencia": competencia,
        "planos": planos_state,
        "progresso": progresso,
        "detalhes": detalhes,
        "url_fonte": url_fonte,
        "eta": eta
    }
    if supabase:
        try:
            supabase.table("app_state").upsert({"id": "sync_status", "data": sync_status}).execute()
        except:
            pass
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(sync_status, f, ensure_ascii=False, indent=2)

# ==============================================================================
# MOTOR PRINCIPAL
# ==============================================================================
def baixar_cnes(competencia: str):
    print(f"\n============================================================")
    print(f" COLIH CAPTAÇÃO — Motor Híbrido CNES (Plano C)")
    print(f"============================================================")

    planos_state = [
        {"id": "OFICIAL", "nome": "DATASUS (Portal de Dados Abertos)", "status": "processando", "erro": None}
    ]
    
    save_sync_status("verificando", planos_state, competencia=competencia, progresso=1)
    
    try:
        df_estab, df_prof, df_equip, df_leito, extract_dir, plano_usado = baixar_zip_plano_c(competencia, Path(tempfile.gettempdir()))
        planos_state[0]["status"] = "sucesso"
    except Exception as e_c:
        import traceback
        print(f"\n[CRITICAL] Falha no Download Principal: {e_c}")
        traceback.print_exc()
        planos_state[0]["status"] = "falha"
        planos_state[0]["erro"] = str(e_c)
        save_sync_status("falha_total", planos_state, erro_geral=f"Portal DATASUS indisponível: {str(e_c)}", competencia=competencia)
        return False

    # Se chegou aqui e tem dados, salva os caches
    save_sync_status("sucesso", planos_state, competencia=competencia, progresso=100)
    print(f"\n[INFO] Processando bases extraidas do {plano_usado}...\n")
    try:
        estabs = processar_estabelecimentos(df_estab, df_equip, df_leito)
        
        # Parse auxiliary tables robustly
        print("Lendo dicionarios avançados...")
        dicionarios = {}
        for p in Path(extract_dir).glob("tb*.csv"):
            if any(x in p.name.lower() for x in ["equipamento", "leito", "comissao", "instalacaofisica", "atendimentoprestado", "servicoespecializado", "classificacaoservico", "naturezajuridica", "convenio"]):
                try:
                    df_dic = pd.read_csv(p, sep=";", encoding="iso-8859-1", dtype=str, on_bad_lines='skip')
                    cols = [str(c).upper().strip() for c in df_dic.columns]
                    c_id = next((c for c in cols if c.startswith("CO_")), None)
                    c_ds = next((c for c in cols if c.startswith("DS_") or c.startswith("NO_")), None)
                    if c_id and c_ds:
                        if c_id not in dicionarios: dicionarios[c_id] = {}
                        for _, row in df_dic.iterrows():
                            if c_id == "CO_EQUIPAMENTO" and "CO_TIPO_EQUIPAMENTO" in cols:
                                val_id = str(row.iloc[cols.index("CO_TIPO_EQUIPAMENTO")]).strip().lstrip('0') + "-" + str(row.iloc[cols.index("CO_EQUIPAMENTO")]).strip().lstrip('0')
                            elif "CO_CLASSIFICACAO_SERVICO" in cols and "CO_SERVICO_ESPECIALIZADO" in cols:
                                c_id_override = "CO_CLASSIFICACAO"
                                if c_id_override not in dicionarios: dicionarios[c_id_override] = {}
                                val_id = str(row.iloc[cols.index("CO_SERVICO_ESPECIALIZADO")]).strip().lstrip('0') + "-" + str(row.iloc[cols.index("CO_CLASSIFICACAO_SERVICO")]).strip().lstrip('0')
                                dicionarios[c_id_override][val_id] = str(row.iloc[cols.index(c_ds)]).strip()
                                continue
                            else:
                                val_id = str(row.iloc[cols.index(c_id)]).strip().lstrip('0')
                            dicionarios[c_id][val_id] = str(row.iloc[cols.index(c_ds)]).strip()
                except:
                    pass

        print("Lendo relacionamentos avançados (Comissões, Instalações, Equipamentos etc) se disponíveis...")
        rels = {
            "equipamentos": ("rlEstabEquipamento*.csv", "CO_EQUIPAMENTO", "QT_EXISTENTE"),
            "leitos": ("rlEstabComplementar*.csv", "CO_LEITO", "QT_EXIST"),
            "instalacoesFisicas": ("rlEstabInstFisiAssist*.csv", "CO_INSTALACAO", "QT_INSTALACAO"),
            "comissoes": ("rlEstabComissaoOutro*.csv", "CO_COMISSAO", None),
            "atendimentoPrestado": ("rlEstabAtendPrestConv*.csv", "CO_ATENDIMENTO_PRESTADO", None),
            "convenios": ("rlEstabAtendPrestConv*.csv", "CO_CONVENIO", None),
            "servicosEspecializados": ("rlEstabServClass*.csv", "CO_SERVICO", None),
            "classificacoesServicos": ("rlEstabServClass*.csv", "CO_CLASSIFICACAO", None)
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
                            cnes_id = cnes_id[-7:] if len(cnes_id) > 7 else cnes_id
                            if cnes_id in estabs:
                                code_val = str(row[col_id]).strip()
                                lookup_key = code_val.lstrip('0')
                                if col_id == "CO_EQUIPAMENTO" and "CO_TIPO_EQUIPAMENTO" in df_extra.columns:
                                    lookup_key = str(row["CO_TIPO_EQUIPAMENTO"]).strip().lstrip('0') + "-" + lookup_key
                                elif col_id == "CO_CLASSIFICACAO" and "CO_SERVICO" in df_extra.columns:
                                    lookup_key = str(row["CO_SERVICO"]).strip().lstrip('0') + "-" + lookup_key
                                
                                desc = dic_to_use.get(lookup_key, code_val)
                                
                                if k not in estabs[cnes_id]: estabs[cnes_id][k] = []
                                
                                if k == "equipamentos":
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
                                        estabs[cnes_id][k].append(desc)
                except Exception as ex:
                    print(f"Erro parseando {p.name}: {ex}")

        medicos_list = processar_profissionais(df_prof, estabs)

        # Calcular especialidades por hospital
        for m in medicos_list:
            for v in m.get("vinculos", []):
                cnes_id = v.get("cnes")
                if cnes_id in estabs:
                    if "especialidades" not in estabs[cnes_id]:
                        estabs[cnes_id]["especialidades"] = set()
                    if m.get("especialidade"):
                        estabs[cnes_id]["especialidades"].add(m["especialidade"])
        
        for e in estabs.values():
            if "especialidades" in e:
                e["especialidades"] = sorted(list(e["especialidades"]))
            else:
                e["especialidades"] = []
            
            # Mapear Natureza Juridica
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
                        break

    except Exception as e_proc:
        print(f"Erro durante o processamento: {e_proc}")
        return False

    meta = {
        "competencia": competencia,
        "data_atualizacao": datetime.now().isoformat(),
        "data_atualizacao_fmt": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "plano_extracao": plano_usado,
        "total_medicos": len(set([m['cns'] for m in medicos_list])),
        "total_estabelecimentos": len(estabs),
    }

    # Salva Cache Limpo
    with open(DATA_DIR / "medicos_cache.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "medicos": medicos_list}, f, ensure_ascii=False, indent=2)
    with open(DATA_DIR / "estab_cache.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "estabelecimentos": list(estabs.values())}, f, ensure_ascii=False, indent=2)
        
    try:
        shutil.rmtree(extract_dir)
    except:
        pass
        
    save_sync_status("sucesso", planos_state, proxima_tentativa="Daqui a 1 mês", competencia=competencia)
    return meta

if __name__ == "__main__":
    competencias = get_competencias_recentes()
    print(f"Mês atual pode não estar publicado. Testando fila de competências: {competencias}")
    
    sucesso = False
    for comp in competencias:
        print(f"\n[*] Tentando extrair dados da Competência: {comp}")
        resultado = baixar_cnes(comp)
        if resultado is not False:
            sucesso = True
            break
            
    if not sucesso:
        print("Todas as competências recentes falharam.")
        sys.exit(1)
