"""
COLIH Captação — Backend FastAPI
=================================
Serve dados de médicos do CNES e gerencia o pipeline de captação
com suporte a múltiplos usuários.

Endpoints principais:
  GET  /api/info             — Status do cache e metadados da fonte
  GET  /api/hospitais        — Busca estabelecimentos por nome
  GET  /api/hospitais/{id}   — Ficha do hospital + lista de médicos por especialidade
  GET  /api/medicos          — Busca médicos por nome/especialidade
  GET  /api/medicos/{cns}    — Ficha do médico + histórico de vínculos
  GET  /api/especialidades   — Lista de CBOs disponíveis
  GET  /api/pipeline         — Pipeline completo ou filtrado por usuário
  POST /api/pipeline         — Adicionar médico ao pipeline
  PUT  /api/pipeline/{cns}   — Atualizar status, contato, notas
  POST /api/pipeline/{cns}/interacao  — Adicionar interação ao histórico
  DELETE /api/pipeline/{cns} — Remover do pipeline
  GET  /api/stats            — Estatísticas gerais
  GET  /api/usuarios         — Listar usuários cadastrados
  POST /api/usuarios         — Criar usuário
"""

import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ─── Configuração ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

MEDICOS_CACHE = DATA_DIR / "medicos_cache.json"
ESTAB_CACHE_PATH = DATA_DIR / "estab_cache.json"
PIPELINE_FILE = DATA_DIR / "pipeline.json"
USUARIOS_FILE = DATA_DIR / "usuarios.json"

app = FastAPI(
    title="COLIH Captação API",
    description="Sistema de Captação de Médicos Cooperadores — COLIH Salvador",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes.pipeline_visitas import router as pipeline_visitas_router
app.include_router(pipeline_visitas_router)

# ─── Helpers de Dados ────────────────────────────────────────────────────────
def load_json(path: Path, default):
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_medicos_cache():
    return load_json(MEDICOS_CACHE, {"meta": {}, "medicos": []})

import unicodedata

def normalize_str(s: str) -> str:
    if not s:
        return ""
    # Remove all unicode replacement characters that may corrupt matching
    s = s.replace("\ufffd", "")
    s = unicodedata.normalize("NFD", str(s))
    s = s.encode("ascii", "ignore").decode("utf-8")
    return s.lower().strip()

BAIRROS_DISTRITOS = {}
try:
    with open(os.path.join(BASE_DIR, "bairros_distritos.json"), "r", encoding="utf-8", errors="replace") as f:
        raw_dict = json.load(f)
        BAIRROS_DISTRITOS = {normalize_str(k): v for k, v in raw_dict.items()}
except Exception:
    try:
        with open("bairros_distritos.json", "r", encoding="utf-8", errors="replace") as f:
            raw_dict = json.load(f)
            BAIRROS_DISTRITOS = {normalize_str(k): v for k, v in raw_dict.items()}
    except:
        pass

IBGE_CIDADES = {}
try:
    with open(os.path.join(BASE_DIR, "ibge_cidades.json"), "r", encoding="utf-8-sig") as f:
        IBGE_CIDADES = json.load(f)
except Exception as e:
    print(f"Erro ao carregar IBGE: {e}")

TP_UNIDADE_MAP = {
    "01": "Posto de Saúde",
    "02": "Centro de Saúde / UBS",
    "04": "Policlínica",
    "05": "Hospital Geral",
    "07": "Hospital Especializado",
    "15": "Unidade Mista",
    "20": "Pronto Socorro Geral",
    "21": "Pronto Socorro Especializado",
    "22": "Consultório Isolado",
    "36": "Clínica / Centro de Especialidade",
    "39": "Unidade de Apoio Diagnose e Terapia",
    "40": "Unidade Móvel Terrestre",
    "42": "Unidade Móvel Pré-Hospitalar (SAMU)",
    "43": "Farmácia",
    "50": "Unidade de Vigilância em Saúde",
    "60": "Cooperativa / Cessão de Trabalhadores",
    "62": "Hospital Dia",
    "68": "Central de Gestão em Saúde",
    "69": "Centro de Hemoterapia / Hematologia",
    "70": "Centro de Atenção Psicossocial",
    "72": "Atenção a Saúde Indígena",
    "73": "Pronto Atendimento (UPA)",
    "75": "TeleSaúde",
    "76": "Central de Regulação Médica",
    "77": "Serviço de Atenção Domiciliar",
    "80": "Laboratório de Saúde Pública",
    "83": "Polo de Prevenção e Promoção da Saúde",
    "85": "Centro de Imunização"
}

import difflib

def get_distrito_fuzzy(bairro_norm):
    if not bairro_norm:
        return "Não Informado"
        
    # Tentativa direta
    if bairro_norm in BAIRROS_DISTRITOS:
        return BAIRROS_DISTRITOS[bairro_norm]
        
    # Limpeza de prefixos/sufixos sujos comuns no DATASUS
    clean = bairro_norm
    for sufixo in ["invasao do ", "invasao da ", "invasao ", "loteamento ", "parque ", "conjunto ", "vila ", "bairro ", "centro de "]:
        if clean.startswith(sufixo):
            clean = clean.replace(sufixo, "", 1).strip()
            
    # Mapeamentos manuais para grandes ofensores que o fuzzy não resolve
    HARDCODED = {
        "sao rafael": "sao marcos",
        "stella maris": "stela maris",
        "pituacu": "pituacu",
        "iguatemi": "caminho das arvores",
        "bela vista": "brotas",
        "nazare": "centro historico",
        "chamechame": "chame-chame",
        "dois de": "centro historico", # São bento dois de
        "centro": "centro historico",
        "candeal": "brotas",
        "alphaville i": "itapua",
        "stella mares": "stela maris",
        "resgate": "cabula",
        "trobogy": "pau da lima",
        "nova brasilia de ita": "itapua",
        "nova brasilia de val": "itapua",
        "rio vermelho garibal": "rio vermelho",
        "politeama": "centro historico",
        "centro sao pedro": "centro historico",
        "corredor da vitoria": "vitoria",
    }
    
    for k, v in HARDCODED.items():
        if k in clean:
            if v in BAIRROS_DISTRITOS:
                return BAIRROS_DISTRITOS[v]
            
    # Tentativa direta pós limpeza
    if clean in BAIRROS_DISTRITOS:
        return BAIRROS_DISTRITOS[clean]
        
    # Fuzzy Matching
    chaves = list(BAIRROS_DISTRITOS.keys())
    matches = difflib.get_close_matches(clean, chaves, n=1, cutoff=0.8)
    if matches:
        return BAIRROS_DISTRITOS[matches[0]]
        
    # Tenta fuzzy apenas com a primeira palavra se for nome longo
    if " " in clean:
        first_word = clean.split()[0]
        matches = difflib.get_close_matches(first_word, chaves, n=1, cutoff=0.85)
        if matches:
            return BAIRROS_DISTRITOS[matches[0]]

    return "Não Informado"

_PBM_CACHE = None
def get_pbm_config():
    global _PBM_CACHE
    if _PBM_CACHE is None:
        _PBM_CACHE = {}
        if supabase:
            try:
                res = supabase.table("pbm_config").select("*").execute()
                for row in res.data:
                    _PBM_CACHE[row["cnes"]] = {"pbm": row["pbm"], "link": row.get("link", "")}
            except Exception as e:
                print("Error loading PBM config from Supabase:", e)
    return _PBM_CACHE or {}

def enrich_estab(hosp):
    pbm_conf = get_pbm_config()
    pbm_data = pbm_conf.get(str(hosp.get("cnes")), {})
    if isinstance(pbm_data, bool):
        hosp["_pbm"] = pbm_data
        hosp["_pbm_link"] = ""
    else:
        hosp["_pbm"] = pbm_data.get("pbm", False)
        hosp["_pbm_link"] = pbm_data.get("link", "")
    # Macrorregião e Distrito
    raw = hosp.get("raw", {})
    bairro_norm = normalize_str(raw.get("NO_BAIRRO", ""))
    
    tp = raw.get("TP_UNIDADE")
    if tp and tp in TP_UNIDADE_MAP:
        hosp["tipo"] = TP_UNIDADE_MAP[tp]
    
    # DATASUS pode vir com código IBGE de 6 dígitos no campo municipio
    mun_raw = hosp.get("municipio", "Salvador").strip()
    if mun_raw in IBGE_CIDADES:
        hosp["municipio"] = IBGE_CIDADES[mun_raw].upper()
    elif mun_raw.isdigit():
        hosp["municipio"] = "Outros" # IBGE desconhecido
        
    mun = hosp.get("municipio", "Salvador").strip().upper()
    if mun == "SALVADOR":
        hosp["_distrito"] = get_distrito_fuzzy(bairro_norm)
        hosp["_macrorregiao"] = "Leste"
    else:
        # Para outras cidades, não temos DS. O Frontend vai mostrar a cidade.
        hosp["_distrito"] = hosp.get("municipio").title() # Retorna formatado "Lauro de Freitas"
        hosp["_macrorregiao"] = "Outros"
    
    lat = raw.get("NU_LATITUDE")
    lng = raw.get("NU_LONGITUDE")
    if lat and lng:
        try:
            val_lat = float(str(lat).replace(',', '.'))
            val_lng = float(str(lng).replace(',', '.'))
            
            # Bounding box para a Bahia (exclui coordenadas zeradas/falsas frequentes no DATASUS)
            if -18.50 <= val_lat <= -8.50 and -46.50 <= val_lng <= -37.00:
                hosp["_lat"] = val_lat
                hosp["_lng"] = val_lng
        except ValueError:
            pass
            
    hosp["cnes"] = raw.get("CO_CNES", "")
    hosp["id"] = hosp["cnes"]
    
    # Complexidade baseada em serviços especializados
    servicos = [str(s).upper().strip() for s in hosp.get("servicosEspecializados", [])]
    
    # Categorias de Alta Complexidade para COLIH
    ALTA_COMPLEXIDADE_MAP = {
        "Transplante": ["TRANSPLANTE"],
        "Alta Complexidade Cardiovascular": [
            "SERVICO DE ATENCAO CARDIOVASCULAR",
            "CARDIO",
        ],
        "Alta Complexidade Oncológica": [
            "ONCOLOGIA", "CANCER", "QUIMIOTERAPIA", "RADIOTERAPIA", "ACELERADOR"
        ],
        "Alta Complexidade Neurológica": [
            "NEUROLOGIA", "NEUROCIRURGIA", "NEUROCIRUGIA"
        ],
        "Alta Complexidade Ortopédica": [
            "ORTOPEDIA", "TRAUMATOLOGIA"
        ],
        "Hemoterapia / Hematologia": [
            "HEMOTERAPIA", "HEMATOLOGIA", "HEMOSTASIA"
        ],
        "Terapia Renal Substitutiva": [
            "NEFR", "HEMODIALISE", "DIALISE"
        ],
        "Alta Complexidade Maternidade": [
            "MATERNIDADE", "NEONATOLOGIA", "PERINATAL"
        ],
    }
    
    alta_complex_presentes = []
    for categoria, termos in ALTA_COMPLEXIDADE_MAP.items():
        for termo in termos:
            if any(termo in s for s in servicos):
                alta_complex_presentes.append(categoria)
                break
    
    hosp["_altaComplexidade"] = alta_complex_presentes
    
    # Nível de complexidade geral
    atend = hosp.get("atendimentoPrestado", {})
    tipos_atend = list(atend.keys()) if isinstance(atend, dict) else atend
    
    if alta_complex_presentes or "INTERNACAO" in [str(a).upper() for a in tipos_atend]:
        if len(alta_complex_presentes) >= 3 or "Transplante" in alta_complex_presentes:
            hosp["_complexidade"] = "Alta Complexidade"
        elif len(alta_complex_presentes) >= 1:
            hosp["_complexidade"] = "Média-Alta Complexidade"
        else:
            hosp["_complexidade"] = "Média Complexidade"
    else:
        hosp["_complexidade"] = "Atenção Básica"
        
    # Cell Saver (Máquina de Recuperação)
    has_cell_saver = False
    for eq in hosp.get("equipamentos", []):
        eq_name = eq.get("nome", "").lower()
        if any(term in eq_name for term in ["recuperador", "cell saver", "recuperação de sangue", "autotransfusão", "circulacao extracorporea"]):
            has_cell_saver = True
            break
    hosp["_hasCellSaver"] = has_cell_saver
    
    # Total de Leitos (mantido para informação)
    total_leitos = 0
    for leito in hosp.get("leitos", []):
        try:
            total_leitos += int(leito.get("quantidade", 0))
        except:
            pass
    hosp["_totalLeitos"] = total_leitos

    # Datas de Atualização (Nacional e Local)
    dt_nacional = raw.get("TO_CHAR(DT_ATUALIZACAO,'DD/MM/YYYY')", "")
    dt_regional = raw.get("TO_CHAR(DT_ATUALIZACAO_ORIGEM,'DD/MM/YYYY')", "")
    hosp["_dtAtualizacaoNacional"] = dt_nacional if dt_nacional else "Não Informada"
    hosp["_dtAtualizacaoRegional"] = dt_regional if dt_regional else "Não Informada"

_cached_data = None

def get_estab_cache():
    global _cached_data
    if _cached_data is not None:
        return _cached_data
    if not os.path.exists(ESTAB_CACHE_PATH):
        return {"meta": {}, "estabelecimentos": []}
    with open(ESTAB_CACHE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        validos = []
        for h in data.get("estabelecimentos", []):
            raw = h.get("raw", {})
            if raw.get("CO_MOTIVO_DESAB"):
                continue
            enrich_estab(h)
            validos.append(h)
        data["estabelecimentos"] = validos
        _cached_data = data
        return data


def get_pipeline():
    if supabase:
        try:
            res = supabase.table("pipeline").select("*").execute()
            return {str(row["cns"]): row["data"] for row in res.data}
        except:
            pass
    return load_json(PIPELINE_FILE, {})





# ─── Modelos Pydantic ────────────────────────────────────────────────────────
class AdicionarPipeline(BaseModel):
    cns: str
    nome: str
    especialidade: str
    cbo: Optional[str] = None
    vinculo_principal: Optional[str] = None  # nome do hospital principal
    cnes_principal: Optional[str] = None
    responsavel: Optional[str] = None  # usuário da COLIH responsável
    contato: Optional[str] = None
    notas: Optional[str] = None


class AtualizarPipeline(BaseModel):
    status: Optional[str] = None  # novo | em_contato | aguardando | reuniao | cooperador | recusou
    contato: Optional[str] = None
    crm: Optional[str] = None
    crm_situacao: Optional[str] = None
    notas: Optional[str] = None
    responsavel: Optional[str] = None


class Interacao(BaseModel):
    tipo: str  # ligacao | whatsapp | email | visita | outro
    descricao: str
    resultado: Optional[str] = None
    responsavel: Optional[str] = None


class Usuario(BaseModel):
    nome: str
    email: Optional[str] = None
    whatsapp: Optional[str] = None


# ─── Endpoints de Informação ─────────────────────────────────────────────────
@app.get("/api/info")
def info():
    """Retorna metadados do cache: data de atualização, fonte, totais."""
    cache = get_medicos_cache()
    meta = cache.get("meta", {})
    pipeline = get_pipeline()
    usuarios = listar_usuarios()

    return {
        "status": "ok" if meta else "sem_cache",
        "cache_disponivel": bool(meta),
        "fonte": {
            "nome": meta.get("fonte_primaria", "DATASUS/CNES"),
            "descricao": "Cadastro Nacional de Estabelecimentos de Saúde — Ministério da Saúde",
            "url": "https://cnes.datasus.gov.br",
            "competencia": meta.get("competencia"),
            "data_atualizacao": meta.get("data_atualizacao"),
            "data_atualizacao_fmt": meta.get("data_atualizacao_fmt"),
            "aviso": meta.get("aviso"),
        },
        "totais": {
            "medicos": meta.get("total_medicos", 0),
            "estabelecimentos": meta.get("total_estabelecimentos", 0),
            "municipios": meta.get("municipios_cobertos", []),
            "filtro": meta.get("filtro_cbo"),
        },
        "pipeline": {
            "total": len(pipeline),
            "cooperadores": sum(1 for p in pipeline.values() if p.get("status") == "cooperador"),
        },
        "usuarios_ativos": len(usuarios),
        "mensagem_atualizacao": "Execute scripts/atualizar_cache.py mensalmente para manter os dados atualizados.",
    }


@app.get("/api/regioes")
def listar_regioes():
    """Retorna a lista de todas as Macrorregiões e seus Distritos Sanitários mapeados."""
    # Como Salvador é Macrorregião Leste, vamos estruturar dessa forma
    distritos_map = {}
    for bairro, distrito in BAIRROS_DISTRITOS.items():
        if distrito not in distritos_map:
            distritos_map[distrito] = []
        distritos_map[distrito].append(bairro.title())
        
    resultado = []
    for dist, bairros in distritos_map.items():
        resultado.append({
            "macrorregiao": "Leste",
            "distrito_sanitario": dist,
            "bairros": sorted(bairros)
        })
    return {"regioes": sorted(resultado, key=lambda x: x["distrito_sanitario"])}

# ─── Endpoints de Hospitais/Estabelecimentos ─────────────────────────────────
@app.get("/api/hospitais/valores")
def listar_valores(field: str = Query(...)):
    """Retorna os valores únicos para o campo selecionado na base de hospitais."""
    cache = get_estab_cache()
    estabs = cache.get("estabelecimentos", [])
    valores = set()
    
    for hosp in estabs:
        if field == "nome":
            v = hosp.get("nome", "")
            if v: valores.add(v)
        elif field == "bairro":
            raw = hosp.get("raw", {})
            v = raw.get("NO_BAIRRO", "")
            if v: valores.add(v)
        elif field == "distrito":
            v = hosp.get("_distrito", "")
            if v: valores.add(v)
        elif field == "complexidade":
            v = hosp.get("_complexidade", "")
            if v: valores.add(v)
            
    return {"valores": sorted(list(valores))}

_TMO_CUSTOM_CACHE = None
def get_tmo_custom():
    global _TMO_CUSTOM_CACHE
    if _TMO_CUSTOM_CACHE is None:
        _TMO_CUSTOM_CACHE = {}
        if supabase:
            try:
                res = supabase.table("tmo_custom").select("*").execute()
                for row in res.data:
                    _TMO_CUSTOM_CACHE[row["cnes"]] = row["data"]
            except Exception as e:
                print("Error loading TMO custom config:", e)
    return _TMO_CUSTOM_CACHE


cnes_especialidades_cache = []

@app.get("/api/cnes/especialidades")
def api_get_cnes_especialidades():
    global cnes_especialidades_cache
    if cnes_especialidades_cache:
        return cnes_especialidades_cache
        
    sp_set = set()
    
    # 1. Puxar do cache de medicos do CNES
    cache_file = DATA_DIR / "medicos_cache.json"
    if cache_file.exists():
        try:
            import json
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                docs = data.get("medicos", [])
                for d in docs:
                    esp = d.get("especialidade")
                    if esp:
                        # O CNES retorna especialidades separadas por " / "
                        for e in esp.split(" / "):
                            clean_e = e.strip().upper()
                            if clean_e and not clean_e.startswith("CBO "):
                                sp_set.add(clean_e)
        except Exception as e:
            print("Erro lendo cache de especialidades CNES:", e)
            
    # 2. Puxar da base da COLIH
    if supabase:
        try:
            res = supabase.table("dados_colih_medicos").select("especialidade_1_colih, especialidade_1_hid").execute()
            for row in res.data:
                e1 = row.get("especialidade_1_colih")
                e2 = row.get("especialidade_1_hid")
                if e1: sp_set.add(e1.strip().upper())
                if e2: sp_set.add(e2.strip().upper())
        except Exception as e:
            print("Erro lendo especialidades COLIH:", e)
            
    cnes_especialidades_cache = sorted(list(sp_set))
    return cnes_especialidades_cache

@app.get("/api/hospitais")
def buscar_hospitais(
    nome: Optional[str] = Query(None, description="Busca por nome do estabelecimento"),
    tipo: Optional[str] = Query(None),
    distrito: Optional[str] = Query(None),
    complexidade: Optional[str] = Query(None),
    apoio_colih: Optional[str] = Query(None),
    sus: Optional[str] = Query(None),
    pa: Optional[str] = Query(None),
    apoio_termos: Optional[str] = Query(None),
    tmo: Optional[str] = Query(None),
    pbm: Optional[str] = Query(None),
    limit: int = 40
):
    global _PBM_CACHE
    _PBM_CACHE = None  # force reload on search
    """Busca estabelecimentos de saúde em Salvador com múltiplos filtros."""
    cache = get_estab_cache()
    estabs = cache.get("estabelecimentos", [])
    meta = cache.get("meta", {})

    resultado = estabs
    def apply_filters(h):
        if nome and nome.lower() not in h.get("nome", "").lower():
            return False
        if tipo and h.get("tipo", "").lower() != tipo.lower():
            return False
        if distrito and h.get("_distrito", "").lower() != distrito.lower():
            return False
        if complexidade and h.get("_complexidade", "").lower() != complexidade.lower():
            return False
        if sus:
            is_sus = h.get("_isSus", False)
            if (sus.lower() == 's' and not is_sus) or (sus.lower() == 'n' and is_sus):
                return False
        if tmo and tmo.lower() == 's':
            has_tmo = 'MEDULA OSSEA' in [str(c).upper().strip() for c in (h.get('classificacoesServicos') or [])]
            if not has_tmo:
                cnes_id = str(h.get('cnes', '')).zfill(7)
                custom_tmo = get_tmo_custom()
                if cnes_id in custom_tmo:
                    has_tmo = True
            if not has_tmo: return False
        if pbm and pbm.lower() == 's':
            if not h.get('_pbm'): return False

        if pa:
            is_pa = h.get("_isPA", False)
            if (pa.lower() == 's' and not is_pa) or (pa.lower() == 'n' and is_pa):
                return False
        if apoio_colih:
            termos = [t.strip().lower() for t in apoio_termos.split(',')] if apoio_termos else ["recuperador", "cell saver"]
            has_apoio = False
            for eq in h.get("equipamentos", []):
                eq_nome = str(eq.get("nome", "") or eq.get("descricao", "")).lower()
                if any(t in eq_nome for t in termos):
                    has_apoio = True
                    break
            if (apoio_colih.lower() == 's' and not has_apoio) or (apoio_colih.lower() == 'n' and has_apoio):
                return False
                
        return True

    resultado = [e for e in resultado if apply_filters(e)]
    resultado.sort(key=lambda x: x.get("_totalLeitos", 0), reverse=True)

    total = len(resultado)
    pagina = resultado[:limit]

    return {
        "total": total,
        "limit": limit,
        "fonte": {
            "nome": meta.get("fonte_primaria", "DATASUS/CNES"),
            "competencia": meta.get("competencia"),
            "data_atualizacao_fmt": meta.get("data_atualizacao_fmt"),
        },
        "estabelecimentos": pagina
    }

import urllib.request
import urllib.error

import time

@app.post("/api/hospitais/{cnes}/pbm")
def toggle_pbm(cnes: str, body: dict):
    global _PBM_CACHE, _cached_data
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
        
    try:
        if body.get("pbm") is False:
            supabase.table("pbm_config").delete().eq("cnes", cnes).execute()
        else:
            supabase.table("pbm_config").upsert({
                "cnes": cnes,
                "pbm": True,
                "link": body.get("link", "")
            }).execute()
    except Exception as e:
        print("Error saving PBM to Supabase:", e)
        raise HTTPException(status_code=500, detail="Failed to save to database")
        
    _PBM_CACHE = None # Clear cache
    
    # Update in-memory estab cache dynamically!
    if _cached_data is not None:
        for h in _cached_data.get("estabelecimentos", []):
            if h.get("cnes") == cnes:
                enrich_estab(h) # re-enrich this specific hospital
                break
                
    return {"status": "ok", "cnes": cnes, "pbm": body.get("pbm", False)}

@app.get("/api/hospitais/{cnes}/live")
def detalhe_hospital_live(cnes: str):
    """Busca dados complexos do hospital na API do CNES com Cache Local e Resiliência."""
    cache_dir = DATA_DIR.parent / "cache" / "live_api"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{cnes}.json"

    # 1. Tentar ler do Cache Local primeiro
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return {"status": "sucesso", "dados": json.load(f), "origem": "cache_local"}
        except Exception:
            pass

    # 2. Se não tem cache, busca na Web API do CNES com Retry Exponencial (Anti-503)
    url = f"https://cnes.datasus.gov.br/services/estabelecimentos/{cnes}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://cnes.datasus.gov.br/pages/estabelecimentos/'
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode('utf-8'))
                
                # Salvar no Cache Local permanentemente
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                
                return {"status": "sucesso", "dados": data, "origem": "api_governo_live"}
        except urllib.error.HTTPError as e:
            if e.code in [503, 429, 502, 504]:
                time.sleep(1 + attempt * 2) # Backoff: 1s, 3s, 5s
                continue
            return {"status": "erro", "detalhe": f"Erro HTTP {e.code}"}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return {"status": "erro", "detalhe": str(e)}
            
    return {"status": "erro", "detalhe": "Falha após múltiplas tentativas (Possível bloqueio 503 temporário do DATASUS)"}

@app.get("/api/hospitais/{cnes_id}")
def detalhe_hospital(cnes_id: str, especialidade: Optional[str] = Query(None)):
    """Ficha do hospital com lista de médicos. Filtro opcional por especialidade."""
    estab_cache = get_estab_cache()
    medicos_cache = get_medicos_cache()
    meta = medicos_cache.get("meta", {})

    # Encontrar hospital
    estab = next(
        (e for e in estab_cache.get("estabelecimentos", []) if e.get("cnes") == cnes_id),
        None,
    )
    if not estab:
        raise HTTPException(status_code=404, detail="Estabelecimento não encontrado")

    # Médicos vinculados a este hospital
    medicos = [
        m for m in medicos_cache.get("medicos", [])
        if any(v.get("cnes") == cnes_id for v in m.get("vinculos", []))
    ]

    # Filtro especialidade
    if especialidade:
        esp_lower = especialidade.lower()
        medicos = [
            m for m in medicos
            if esp_lower in m.get("especialidade", "").lower()
            or esp_lower in m.get("cbo", "").lower()
        ]

    # Verificar pipeline
    pipeline = get_pipeline()
    for m in medicos:
        m["no_pipeline"] = m.get("cns") in pipeline
        if m["no_pipeline"]:
            m["status_pipeline"] = pipeline[m["cns"]].get("status")

    return {
        "estabelecimento": estab,
        "total_medicos": len(medicos),
        "especialidade_filtrada": especialidade,
        "fonte": {
            "nome": meta.get("fonte_primaria", "DATASUS/CNES"),
            "competencia": meta.get("competencia"),
            "data_atualizacao_fmt": meta.get("data_atualizacao_fmt"),
        },
        "medicos": sorted(medicos, key=lambda m: m.get("nome", "")),
    }


# ─── Endpoints de Médicos ────────────────────────────────────────────────────
@app.get("/api/especialidades")
def listar_especialidades():
    """Lista todas as especialidades médicas disponíveis no cache."""
    cache = get_medicos_cache()
    meta = cache.get("meta", {})
    medicos = cache.get("medicos", [])

    from collections import Counter
    counts = Counter()
    for m in medicos:
        esp = m.get("especialidade", "")
        if esp:
            for e in esp.split(" / "):
                clean_e = e.strip()
                if clean_e and not clean_e.startswith("CBO "):
                    # Capitalize first letter properly
                    if clean_e.isupper() or clean_e.islower():
                        clean_e = clean_e.capitalize()
                    counts[clean_e] += 1
                    
    esp_list = sorted(
        [{"especialidade": esp, "total": count} for esp, count in counts.items()],
        key=lambda x: x["total"],
        reverse=True,
    )
    return {
        "total_especialidades": len(esp_list),
        "fonte": {
            "nome": meta.get("fonte_primaria", "DATASUS/CNES"),
            "competencia": meta.get("competencia"),
            "data_atualizacao_fmt": meta.get("data_atualizacao_fmt"),
        },
        "especialidades": esp_list,
    }



_sus_hospitais_set = None

def get_sus_hospitais_set():
    global _sus_hospitais_set
    if _sus_hospitais_set is None:
        hospitais = get_estab_cache().get("estabelecimentos", [])
        _sus_hospitais_set = {h.get("cnes") for h in hospitais if h.get("convenios") and "SUS" in h.get("convenios")}
    return _sus_hospitais_set

@app.get("/api/medicos")
def buscar_medicos(
    nome: str = Query("", description="Busca por nome do médico"),
    especialidade: str = Query("", description="Busca por especialidade ou CBO"),
    hospital: str = Query("", description="Filtra por nome do estabelecimento"),
    municipio: Optional[str] = Query(None),
    apenas_ativos: bool = Query(True),
    atende_sus: Optional[str] = Query(None, description="Filtra por Atende SUS (sim/nao)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Busca médicos com filtros múltiplos."""
    cache = get_medicos_cache()
    meta = cache.get("meta", {})
    medicos = cache.get("medicos", [])

    sus_cnes_set = get_sus_hospitais_set()
    resultado = medicos
    
    if atende_sus:
        want_sus = (atende_sus.lower() == "sim")
        resultado = [
            m for m in resultado
            if any(v.get("cnes") in sus_cnes_set for v in m.get("vinculos", [])) == want_sus
        ]

    if nome:
        nome_lower = nome.lower()
        resultado = [m for m in resultado if nome_lower in m.get("nome", "").lower()]

    if especialidade:
        esp_lower = especialidade.lower()
        
        # Check if it's an HLC-9 Target
        import json
        cnes_targets = []
        try:
            with open(DATA_DIR / 'hlc_dict.json', 'r', encoding='utf-8') as f:
                hlc_dict = json.load(f)
                cnes_targets = [k.lower() for k, v in hlc_dict.items() if v.lower() == esp_lower]
        except Exception:
            pass
            
        if cnes_targets:
            resultado = [
                m for m in resultado
                if any(ct in m.get("especialidade", "").lower() for ct in cnes_targets)
                or esp_lower in m.get("especialidade", "").lower()
                or esp_lower in m.get("cbo", "").lower()
            ]
        else:
            resultado = [
                m for m in resultado
                if esp_lower in m.get("especialidade", "").lower()
                or esp_lower in m.get("cbo", "").lower()
            ]

    if hospital:
        hosp_norm = normalize_str(hospital)
        resultado = [
            m for m in resultado
            if any(hosp_norm in normalize_str(v.get("estabelecimento", "")) for v in m.get("vinculos", []))
        ]

    if municipio:
        mun_lower = municipio.lower()
        resultado = [
            m for m in resultado
            if any(mun_lower in v.get("municipio", "").lower() for v in m.get("vinculos", []))
        ]

    if apenas_ativos:
        resultado = [
            m for m in resultado
            if any(v.get("ativo", True) for v in m.get("vinculos", []))
        ]

    total = len(resultado)
    pagina = resultado[offset : offset + limit]

    # Enriquecer com dados do pipeline e SUS
    pipeline = get_pipeline()
    for m in pagina:
        m["atende_sus"] = "Sim" if any(v.get("cnes") in sus_cnes_set for v in m.get("vinculos", [])) else "Não"
        m["hospitais_sus"] = list(set([v.get("estabelecimento") for v in m.get("vinculos", []) if v.get("cnes") in sus_cnes_set and v.get("estabelecimento")]))
        
        m["no_pipeline"] = m.get("cns") in pipeline
        if m["no_pipeline"]:
            p = pipeline[m["cns"]]
            m["status_pipeline"] = p.get("status")
            m["responsavel_pipeline"] = p.get("responsavel")
            
    enrich_with_colih(pagina)

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "fonte": {
            "nome": meta.get("fonte_primaria", "DATASUS/CNES"),
            "competencia": meta.get("competencia"),
            "data_atualizacao_fmt": meta.get("data_atualizacao_fmt"),
            "aviso": meta.get("aviso"),
        },
        "medicos": pagina,
    }


@app.get("/api/medicos/{cns}")
def detalhe_medico(cns: str):
    """Ficha completa do médico com histórico de vínculos."""
    cache = get_medicos_cache()
    meta = cache.get("meta", {})
    medico = next((m for m in cache.get("medicos", []) if m.get("cns") == cns), None)

    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")

    pipeline = get_pipeline()
    medico_data = dict(medico)
    medico_data["pipeline"] = pipeline.get(cns)
    medico_data["fonte"] = {
        "nome": meta.get("fonte_primaria", "DATASUS/CNES"),
        "competencia": meta.get("competencia"),
        "data_atualizacao_fmt": meta.get("data_atualizacao_fmt"),
        "aviso": meta.get("aviso"),
    }
    enrich_with_colih([medico_data])

    return medico_data


# ─── Endpoints de Pipeline ───────────────────────────────────────────────────
STATUS_VALIDOS = ["novo", "em_contato", "aguardando", "reuniao", "cooperador", "recusou"]


@app.get("/api/status")
def get_status():
    if supabase:
        try:
            res = supabase.table("app_state").select("data").eq("id", "sync_status").execute()
            if res.data: return res.data[0]["data"]
        except:
            pass
            
    status_path = DATA_DIR / "sync_status.json"
    if status_path.exists():
        with open(status_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "sucesso": False,
        "data_fmt": "Nunca",
        "plano_usado": "Nenhum",
        "logs": ["Arquivo de status não encontrado."]
    }

@app.post("/api/sync")
def force_sync():
    """Endpoint for the frontend to trigger a background sync update."""
    import subprocess
    import threading
    
    def run_sync():
        script_path = Path(__file__).parent.parent / "scripts" / "atualizar_cache.py"
        venv_python = Path(__file__).parent.parent / "backend" / "venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            venv_python = "python"
        subprocess.run([str(venv_python), str(script_path)])
        
    threading.Thread(target=run_sync).start()
    return {"message": "Sincronização iniciada em segundo plano."}

@app.post("/api/sync/importar-zip")
def importar_zip_local(body: dict):
    """
    Processa um arquivo ZIP do CNES já baixado manualmente.
    Recebe: { "caminho": "C:/Users/.../BASE_DE_DADOS_CNES_202605.ZIP" }
    """
    import threading, shutil, tempfile, zipfile as _zf, re as _re
    
    caminho = body.get("caminho", "").strip()
    if not caminho:
        return {"ok": False, "erro": "Caminho do arquivo não informado."}
    
    zip_path = Path(caminho)
    if not zip_path.exists():
        return {"ok": False, "erro": f"Arquivo não encontrado: {caminho}"}
    if not zip_path.suffix.upper() == ".ZIP":
        return {"ok": False, "erro": "O arquivo deve ter extensão .ZIP"}

    # Tenta extrair a competência do nome do arquivo (ex: BASE_DE_DADOS_CNES_202605.ZIP)
    m = _re.search(r'(\d{6})', zip_path.name)
    competencia = m.group(1) if m else "000000"
    
    def run_import():
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        from atualizar_cache import save_sync_status, processar_estabelecimentos, processar_medicos, DATA_DIR
        import pandas as pd
        
        save_sync_status("verificando", [{"id": "IMPORT", "nome": "Importação de ZIP Local", "status": "processando", "erro": None}],
                         competencia=competencia, progresso=10, detalhes=f"Processando ZIP local: {zip_path.name}")
        try:
            extract_dir = Path(tempfile.mkdtemp())
            with _zf.ZipFile(str(zip_path), 'r') as z:
                z.extractall(str(extract_dir))
            
            # Encontra CSVs principais
            estab_csvs = list(extract_dir.rglob("tbEstabelecimento*.csv")) or list(extract_dir.rglob("STBA*.csv"))
            prof_csvs = list(extract_dir.rglob("tbDadosProfissionalSus*.csv")) or list(extract_dir.rglob("PFBA*.csv"))
            carga_csvs = list(extract_dir.rglob("tbCargaHorariaSus*.csv")) or list(extract_dir.rglob("PFBA*.csv"))

            if not estab_csvs:
                save_sync_status("falha_total", erro_geral="Não encontrei o arquivo de estabelecimentos no ZIP.")
                return
            
            save_sync_status("verificando", progresso=40, detalhes="Lendo estabelecimentos...")
            df_estab = pd.read_csv(str(estab_csvs[0]), sep=";", encoding="iso-8859-1", dtype=str, on_bad_lines='skip')
            
            save_sync_status("verificando", progresso=60, detalhes="Lendo profissionais...")
            df_prof = pd.DataFrame()
            if prof_csvs:
                df_prof = pd.read_csv(str(prof_csvs[0]), sep=";", encoding="iso-8859-1", dtype=str, on_bad_lines='skip')
            
            save_sync_status("verificando", progresso=80, detalhes="Processando e salvando cache...")
            estabs = processar_estabelecimentos(df_estab)
            medicos = processar_medicos(df_prof, df_prof) if not df_prof.empty else []
            
            import json, datetime as _dt
            meta = {
                "competencia": competencia,
                "data_atualizacao": _dt.datetime.now().isoformat(),
                "data_atualizacao_fmt": _dt.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "plano_extracao": f"Importação Manual: {zip_path.name}",
                "total_medicos": len(medicos),
                "total_estabelecimentos": len(estabs),
            }
            with open(DATA_DIR / "medicos_cache.json", "w", encoding="utf-8") as f:
                json.dump({"meta": meta, "medicos": medicos}, f, ensure_ascii=False, indent=2)
            with open(DATA_DIR / "estab_cache.json", "w", encoding="utf-8") as f:
                json.dump({"meta": meta, "estabelecimentos": list(estabs.values())}, f, ensure_ascii=False, indent=2)
            
            shutil.rmtree(str(extract_dir), ignore_errors=True)
            save_sync_status("sucesso", [{"id": "IMPORT", "nome": "Importação de ZIP Local", "status": "sucesso", "erro": None}],
                             competencia=competencia, progresso=100)
        except Exception as e:
            save_sync_status("falha_total", erro_geral=f"Erro ao processar ZIP: {e}")
    
    threading.Thread(target=run_import).start()
    return {"ok": True, "message": f"Importando {zip_path.name} — competência {competencia}. Acompanhe o status."}

@app.get("/api/sync-config")
def get_sync_config():
    if supabase:
        try:
            res = supabase.table("app_state").select("data").eq("id", "sync_config").execute()
            if res.data: return res.data[0]["data"]
        except:
            pass
    config_file = DATA_DIR / "sync_config.json"
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"uf": "BA", "municipios_especificos": [], "descricao": "Bahia (estado completo)"}

@app.post("/api/sync-config")
def save_sync_config(body: dict):
    """Salva a configuração de escopo geográfico da sync."""
    config_file = DATA_DIR / "sync_config.json"
    uf = body.get("uf", "BA").upper()
    municipios = body.get("municipios_especificos", [])
    descricao = body.get("descricao") or (f"{uf} (estado completo)" if not municipios else f"{len(municipios)} município(s) selecionado(s)")
    config = {"uf": uf, "municipios_especificos": municipios, "descricao": descricao}
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return {"ok": True, "config": config}


# ─── Helper COLIH ──────────────────────────────────────────────────────────────
_colih_cache = None
def get_colih_cache():
    global _colih_cache
    if _colih_cache is None and supabase:
        try:
            docs = supabase.table("dados_colih_medicos").select("*").execute().data
            mems = supabase.table("dados_colih_membros").select("*").execute().data
            import unicodedata
            def norm(s):
                if not s: return ""
                return ''.join(c for c in unicodedata.normalize('NFKD', str(s).upper()) if not unicodedata.combining(c)).strip()
            
            docs_map = {norm(d.get('nome')): d for d in docs}
            mems_map = {norm(m.get('nome')): m for m in mems}
            _colih_cache = {"medicos": docs_map, "membros": mems_map}
        except:
            pass
    return _colih_cache or {"medicos": {}, "membros": {}}

def reset_colih_cache():
    global _colih_cache
    _colih_cache = None

def enrich_with_colih(medicos):
    cache = get_colih_cache()
    import unicodedata
    def norm(s):
        if not s: return ""
        return ''.join(c for c in unicodedata.normalize('NFKD', str(s).upper()) if not unicodedata.combining(c)).strip()
        
    for m in medicos:
        nome_norm = norm(m.get('nome'))
        if nome_norm in cache['medicos']:
            m['colih'] = cache['medicos'][nome_norm]

# ─── Enriquecimento de Currículos ────────────────────────────────────────────

CURRICULOS_CACHE = DATA_DIR / "curriculos_cache.json"

def get_curriculos_cache() -> dict:
    if CURRICULOS_CACHE.exists():
        try:
            with open(CURRICULOS_CACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

@app.get("/api/medicos/{cns}/curriculo")
def get_curriculo_medico(cns: str):
    """Retorna dados de currículo enriquecido para um médico específico."""
    cache = get_curriculos_cache()
    if cns in cache:
        return {"status": "encontrado", "data": cache[cns]}
    # Tenta encontrar os links diretos pelo nome do médico (sem precisar ter enriquecido)
    medicos = get_medicos_cache().get("medicos", [])
    medico = next((m for m in medicos if m.get("cns") == cns), None)
    if medico:
        import urllib.parse
        nome = medico.get("nome", "")
        crm = medico.get("crm", "")
        uf = medico.get("crm_uf", "BA")
        nome_enc = urllib.parse.quote(nome)
        crm_num = "".join(c for c in crm if c.isdigit())
        return {
            "status": "pendente",
            "crm_cnes": crm,
            "links": {
                "cfm": f"https://portal.cfm.org.br/busca-medicos/?busca={nome_enc}&uf={uf}",
                "cfm_crm": f"https://portal.cfm.org.br/busca-medicos/?crm={crm_num}&uf={uf}" if crm_num else "",
                "doctoralia": f"https://www.doctoralia.com.br/busca?q={nome_enc}",
                "escavador": f"https://www.escavador.com/busca?q={nome_enc}",
                "lattes": f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&nome={nome_enc}&tipoRecurso=1",
                "google_medico": f"https://www.google.com/search?q={nome_enc}+médico+CRM+{uf}",
            }
        }
    raise HTTPException(status_code=404, detail="Médico não encontrado")

@app.post("/api/medicos/{cns}/enriquecer")
def enriquecer_medico_bg(cns: str):
    """Dispara enriquecimento síncrono para um médico específico."""
    import subprocess
    script = Path(__file__).parent.parent / "scripts" / "enriquecer_curriculos.py"
    venv_py = Path(__file__).parent.parent / "backend" / "venv" / "Scripts" / "python.exe"
    py = str(venv_py) if venv_py.exists() else "python"
    
    try:
        subprocess.run([py, str(script), "--cns", cns, "--forcar"], check=True, timeout=45)
        return {"ok": True, "message": f"Enriquecimento concluído para CNS {cns}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enriquecer-todos")
def enriquecer_todos_bg(limite: int = 100):
    """Dispara enriquecimento em background para todos os médicos sem currículo."""
    import subprocess, threading
    def run():
        script = Path(__file__).parent.parent / "scripts" / "enriquecer_curriculos.py"
        venv_py = Path(__file__).parent.parent / "backend" / "venv" / "Scripts" / "python.exe"
        py = str(venv_py) if venv_py.exists() else "python"
        subprocess.run([py, str(script), "--todos", "--limite", str(limite)])
    threading.Thread(target=run, daemon=True).start()
    return {"ok": True, "message": f"Enriquecimento em lote iniciado (até {limite} médicos)"}

@app.get("/api/pipeline")
def listar_pipeline(
    responsavel: Optional[str] = Query(None, description="Filtrar por responsável"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    especialidade: Optional[str] = Query(None),
    atende_sus: Optional[str] = Query(None, description="Filtrar por Atende SUS (sim/nao)"),
):
    """Lista médicos no pipeline. Suporta filtro por usuário responsável."""
    pipeline = get_pipeline()
    cache = get_medicos_cache()
    meta = cache.get("meta", {})
    medicos_sus = cache.get("medicos", [])
    
    sus_dict = {}
    for ms in medicos_sus:
        if ms.get("cns"):
            sus_dict[ms["cns"]] = ms.get("vinculos", [])

    resultado = list(pipeline.values())

    for p in resultado:
        cns = p.get("cns")
        if cns and cns in sus_dict:
            p["atende_sus"] = "Sim"
            p["hospitais_sus"] = list(set([v.get("estabelecimento") for v in sus_dict[cns] if v.get("estabelecimento")]))
        else:
            p["atende_sus"] = "Não"
            p["hospitais_sus"] = []

    if responsavel:
        resultado = [p for p in resultado if p.get("responsavel", "").lower() == responsavel.lower()]
    if status:
        resultado = [p for p in resultado if p.get("status") == status]
    if especialidade:
        esp_lower = especialidade.lower()
        resultado = [p for p in resultado if esp_lower in p.get("especialidade", "").lower()]
    if atende_sus:
        val = "Sim" if atende_sus.lower() == "sim" else "Não"
        resultado = [p for p in resultado if p.get("atende_sus") == val]
    return {
        "total": len(resultado),
        "fonte": {
            "nome": meta.get("fonte_primaria", "DATASUS/CNES"),
            "competencia": meta.get("competencia"),
            "data_atualizacao_fmt": meta.get("data_atualizacao_fmt"),
        },
        "pipeline": sorted(resultado, key=lambda p: p.get("data_adicao", ""), reverse=True),
    }


@app.post("/api/pipeline")
def adicionar_pipeline(dados: AdicionarPipeline):
    """Adiciona um médico ao pipeline de captação."""
    pipeline = get_pipeline()

    if dados.cns in pipeline:
        raise HTTPException(status_code=409, detail="Médico já está no pipeline")

    agora = datetime.now().isoformat()
    pipeline[dados.cns] = {
        "cns": dados.cns,
        "nome": dados.nome,
        "especialidade": dados.especialidade,
        "cbo": dados.cbo,
        "vinculo_principal": dados.vinculo_principal,
        "cnes_principal": dados.cnes_principal,
        "status": "novo",
        "responsavel": dados.responsavel,
        "contato": dados.contato,
        "crm": None,
        "crm_situacao": None,
        "notas": dados.notas or "",
        "interacoes": [],
        "data_adicao": agora,
        "data_ultimo_contato": None,
        "data_atualizacao": agora,
    }
    if supabase:
        try:
            # We must upsert the specific cns that was modified
            # It's easier to just upsert everything or the specific one.
            # But the functions modify pipeline[cns]
            rows = [{"cns": k, "data": v} for k, v in pipeline.items()]
            supabase.table("pipeline").upsert(rows).execute()
        except Exception as e: print("Supabase error:", e)
    else:
        save_json(PIPELINE_FILE, pipeline)
    return {"ok": True, "cns": dados.cns, "mensagem": f"{dados.nome} adicionado ao pipeline"}


@app.put("/api/pipeline/{cns}")
def atualizar_pipeline(cns: str, dados: AtualizarPipeline):
    """Atualiza status, contato, notas ou responsável de um médico no pipeline."""
    pipeline = get_pipeline()

    if cns not in pipeline:
        raise HTTPException(status_code=404, detail="Médico não encontrado no pipeline")

    entrada = pipeline[cns]
    agora = datetime.now().isoformat()

    if dados.status and dados.status not in STATUS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Status inválido. Válidos: {STATUS_VALIDOS}")

    if dados.status:
        entrada["status"] = dados.status
    if dados.contato is not None:
        entrada["contato"] = dados.contato
    if dados.crm is not None:
        entrada["crm"] = dados.crm
    if dados.crm_situacao is not None:
        entrada["crm_situacao"] = dados.crm_situacao
    if dados.notas is not None:
        entrada["notas"] = dados.notas
    if dados.responsavel is not None:
        entrada["responsavel"] = dados.responsavel

    entrada["data_atualizacao"] = agora
    pipeline[cns] = entrada
    if supabase:
        try:
            # We must upsert the specific cns that was modified
            # It's easier to just upsert everything or the specific one.
            # But the functions modify pipeline[cns]
            rows = [{"cns": k, "data": v} for k, v in pipeline.items()]
            supabase.table("pipeline").upsert(rows).execute()
        except Exception as e: print("Supabase error:", e)
    else:
        save_json(PIPELINE_FILE, pipeline)
    return {"ok": True, "cns": cns, "status": entrada["status"]}


@app.post("/api/pipeline/{cns}/interacao")
def adicionar_interacao(cns: str, interacao: Interacao):
    """Registra uma interação (ligação, WhatsApp, visita) no histórico do médico."""
    pipeline = get_pipeline()

    if cns not in pipeline:
        raise HTTPException(status_code=404, detail="Médico não encontrado no pipeline")

    agora = datetime.now().isoformat()
    agora_fmt = datetime.now().strftime("%d/%m/%Y %H:%M")

    entrada = pipeline[cns]
    entrada.setdefault("interacoes", []).append({
        "id": len(entrada["interacoes"]) + 1,
        "tipo": interacao.tipo,
        "descricao": interacao.descricao,
        "resultado": interacao.resultado,
        "responsavel": interacao.responsavel,
        "data": agora,
        "data_fmt": agora_fmt,
    })
    entrada["data_ultimo_contato"] = agora
    entrada["data_atualizacao"] = agora

    if supabase:
        try:
            # We must upsert the specific cns that was modified
            # It's easier to just upsert everything or the specific one.
            # But the functions modify pipeline[cns]
            rows = [{"cns": k, "data": v} for k, v in pipeline.items()]
            supabase.table("pipeline").upsert(rows).execute()
        except Exception as e: print("Supabase error:", e)
    else:
        save_json(PIPELINE_FILE, pipeline)
    return {"ok": True, "cns": cns, "total_interacoes": len(entrada["interacoes"])}


@app.delete("/api/pipeline/{cns}")
def remover_pipeline(cns: str):
    """Remove um médico do pipeline."""
    pipeline = get_pipeline()
    if cns not in pipeline:
        raise HTTPException(status_code=404, detail="Médico não encontrado no pipeline")
    nome = pipeline[cns].get("nome", cns)
    del pipeline[cns]
    if supabase:
        try:
            # We must upsert the specific cns that was modified
            # It's easier to just upsert everything or the specific one.
            # But the functions modify pipeline[cns]
            rows = [{"cns": k, "data": v} for k, v in pipeline.items()]
            supabase.table("pipeline").upsert(rows).execute()
        except Exception as e: print("Supabase error:", e)
    else:
        save_json(PIPELINE_FILE, pipeline)
    return {"ok": True, "mensagem": f"{nome} removido do pipeline"}


# ─── Estatísticas ────────────────────────────────────────────────────────────
@app.get("/api/stats")
def estatisticas():
    """Estatísticas gerais do pipeline e do cache."""
    pipeline = get_pipeline()
    cache = get_medicos_cache()
    meta = cache.get("meta", {})

    from collections import Counter
    status_count = Counter(p.get("status", "novo") for p in pipeline.values())
    esp_count = Counter(p.get("especialidade", "") for p in pipeline.values() if p.get("status") == "cooperador")
    resp_count = Counter(p.get("responsavel", "Sem responsável") for p in pipeline.values())

    total = len(pipeline)
    cooperadores = status_count.get("cooperador", 0)

    return {
        "fonte": {
            "nome": meta.get("fonte_primaria", "DATASUS/CNES"),
            "competencia": meta.get("competencia"),
            "data_atualizacao_fmt": meta.get("data_atualizacao_fmt"),
        },
        "pipeline": {
            "total": total,
            "por_status": dict(status_count),
            "taxa_conversao": round((cooperadores / total * 100), 1) if total > 0 else 0,
        },
        "cooperadores_por_especialidade": dict(esp_count.most_common(10)),
        "por_responsavel": dict(resp_count),
        "cache": {
            "total_medicos": meta.get("total_medicos", 0),
            "total_estabelecimentos": meta.get("total_estabelecimentos", 0),
            "municipios": meta.get("municipios_cobertos", []),
        },
    }

@app.get("/api/mapeamento")
def mapeamento():
    """Retorna o dicionário de mapeamento HLC-9."""
    try:
        with open(DATA_DIR / "hlc9_dict.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# ─── Endpoints de Usuários & Congregações ─────────────────────────────────────
@app.get("/api/congregacoes")
def listar_congregacoes():
    if not supabase: return {"congregacoes": []}
    try:
        res = supabase.table("congregacoes").select("*").execute()
        return {"congregacoes": res.data}
    except Exception as e:
        print("Erro congregacoes", e)
        return {"congregacoes": []}

class UsuarioCreateReq(BaseModel):
    nome: str
    telefone: Optional[str] = None
    congregacao_id: Optional[int] = None

@app.get("/api/usuarios")
def listar_usuarios():
    if not supabase: return {"usuarios": []}
    try:
        res = supabase.table("usuarios").select("*, congregacoes(nome)").execute()
        # formatando a saida
        usuarios_list = []
        for u in res.data:
            usuarios_list.append({
                "id": u["id"],
                "nome": u["nome"],
                "telefone": u.get("telefone"),
                "congregacao_id": u.get("congregacao_id"),
                "congregacao_nome": u.get("congregacoes", {}).get("nome") if u.get("congregacoes") else None,
                "criado_em": u.get("criado_em")
            })
        return {"usuarios": usuarios_list}
    except Exception as e:
        print("Erro list usuarios", e)
        return {"usuarios": []}

@app.post("/api/usuarios")
def criar_usuario(usuario: UsuarioCreateReq):
    if not supabase: raise HTTPException(status_code=500, detail="Sem banco")
    payload = {
        "nome": usuario.nome,
        "telefone": usuario.telefone,
        "congregacao_id": usuario.congregacao_id
    }
    try:
        res = supabase.table("usuarios").insert(payload).execute()
        return {"ok": True, "usuario": res.data[0]}
    except Exception as e:
        print("Erro criar usuario", e)
        raise HTTPException(status_code=500, detail="Erro ao criar usuario")

@app.delete("/api/usuarios/{uid}")
def deletar_usuario(uid: str):
    if not supabase: return {"ok": False}
    try:
        supabase.table("usuarios").delete().eq("id", uid).execute()
        return {"ok": True}
    except Exception as e:
        print("Erro deletar usuario", e)
        return {"ok": False}# ─── ROTAS RESTAURADAS DA COLIH ──────────────────────────────────────────────────
@app.get("/api/colih/medicos")
def api_get_colih_medicos():
    if not getattr(supabase, 'table', None): return []
    try:
        res = supabase.table("dados_colih_medicos").select("*").execute()
        return res.data
    except Exception as e:
        print("Erro colih medicos:", e)
        return []

@app.get("/api/colih/membros")
def api_get_colih_membros():
    if not getattr(supabase, 'table', None): return []
    try:
        res = supabase.table("dados_colih_membros").select("*").execute()
        return res.data
    except Exception as e:
        print("Erro colih membros:", e)
        return []

@app.get("/api/config/hlc-dict")
def api_get_config_hlc_dict():
    config_file = DATA_DIR / "hlc_dict.json"
    if config_file.exists():
        try:
            import json
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

@app.post("/api/config/hlc-dict")
def api_post_config_hlc_dict(body: dict):
    config_file = DATA_DIR / "hlc_dict.json"
    try:
        import json
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(body, f, ensure_ascii=False, indent=2)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/config/hlc-stats")
def api_get_config_hlc_stats():
    config_file = DATA_DIR / "hlc_dict.json"
    hlc_dict = {}
    if config_file.exists():
        try:
            import json
            with open(config_file, "r", encoding="utf-8") as f:
                hlc_dict = json.load(f)
        except:
            pass
            
    # Criar um dict reverso para busca mais rapida: HLC_Name -> [CNES_Name1, CNES_Name2...]
    cnes_map = {}
    for cnes_name, hlc_name in hlc_dict.items():
        hlc_lower = hlc_name.lower().strip()
        if hlc_lower not in cnes_map:
            cnes_map[hlc_lower] = []
        cnes_map[hlc_lower].append(cnes_name.lower().strip())
        
    targets = [
        "Cirurgia cardíaca", "Cirurgia torácica", "Cirurgia geral", "Ortopedia", 
        "Cirurgia de trauma", "Ginecologia", "Obstetrícia", "Anestesiologia",
        "Medicina intensiva", "Hematologia", "Oncologia clínica", "Gastroenterologia",
        "Coloproctologia", "Medicina de emergência", "Medicina hospitalar", "Nefrologia",
        "Neonatologia", "Neurocirurgia", "Otorrinolaringologia", "Pneumologia", 
        "Radiologia intervencionista", "Tratamento de queimados", "Urologia"
    ]
    
    counts = {t: 0 for t in targets}
    
    try:
        medicos = get_medicos_cache().get("medicos", [])
    except Exception as e:
        print("Erro ao buscar medicos do cache para stats:", e)
        medicos = []
        
    for m in medicos:
        esp = (m.get("especialidade") or "").lower()
        cbo = (m.get("cbo") or "").lower()
        if not esp and not cbo: continue
        
        for t in targets:
            t_lower = t.lower()
            ct_list = cnes_map.get(t_lower, [])
            # match if any of the mapped CNES names is in the doctor's specialty/cbo
            if any(ct in esp for ct in ct_list) or t_lower in esp or t_lower in cbo:
                counts[t] += 1
                
    return counts






import os
frontend_path = os.path.join(BASE_DIR.parent, 'frontend')
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
else:
    print(f"ATENÇÃO: Pasta frontend não encontrada em {frontend_path}")




if __name__ == "__main__":

    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)





