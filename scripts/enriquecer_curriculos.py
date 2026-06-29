"""
COLIH Captacao - Script de Enriquecimento de Curriculos
=========================================================
Enriquece os perfis dos medicos com:
  1. Plataforma Lattes (CNPq): busca por nome via urllib (sem JS)
  2. Doctoralia BR: via Playwright headless (se instalado) - extrai CRM, RQE, consultorios
  3. Links para CFM, Doctoralia, Escavador, Lattes (verificacao manual)

Funciona com ou sem Playwright (degradacao gracosa).
Salva progresso incremental no curriculos_cache.json e sync_curriculos_status.json.
"""

import json, time, re, random, argparse, sys
import urllib.request, urllib.parse, urllib.error, ssl
import threading
from pathlib import Path
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")

# Playwright e opcional - degrada gracosamente
PLAYWRIGHT_OK = False
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_OK = True
except ImportError:
    pass

DATA_DIR     = Path(__file__).parent.parent / "backend" / "data"
CACHE_FILE   = DATA_DIR / "curriculos_cache.json"
MEDICOS_FILE = DATA_DIR / "medicos_cache.json"
STATUS_FILE  = DATA_DIR / "sync_curriculos_status.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

# ---- Status de progresso ----
def carregar_status():
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "rodando": False, "total": 0, "processados": 0,
        "encontrados_lattes": 0, "encontrados_doctoralia": 0, "erros": 0,
        "ultima_rodada": None, "proxima_rodada": None, "medico_atual": None,
        "playwright_ativo": PLAYWRIGHT_OK,
    }

def salvar_status(s):
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

def carregar_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def salvar_cache(cache):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# ---- HTTP simples ----
def fetch_html(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read()
            enc = resp.headers.get_content_charset() or "utf-8"
            try:
                return raw.decode(enc)
            except Exception:
                return raw.decode("utf-8", errors="replace")
    except Exception:
        return None

# ---- Busca Lattes ----
def buscar_lattes(nome):
    resultado = {"fonte": "lattes", "status": "nao_encontrado"}
    query = urllib.parse.quote(nome)
    url = (
        "https://buscatextual.cnpq.br/buscatextual/busca.do"
        "?metodo=apresentar&nome=" + query + "&tipoRecurso=1"
    )
    html = fetch_html(url)
    if not html:
        resultado["status"] = "erro_rede"
        return resultado

    ids = re.findall(r"visualizacv\.do\?id=([A-Z0-9]+)", html)
    nomes_lattes = re.findall(r'class="nomeRPCV"[^>]*>([^<]+)<', html)

    if not ids:
        resultado["status"] = "sem_resultados"
        return resultado

    nome_norm = nome.lower().strip()
    melhor_id = ids[0]
    melhor_nome = nomes_lattes[0] if nomes_lattes else ""

    for lid, lnome in zip(ids, nomes_lattes):
        palavras = [p for p in nome_norm.split() if len(p) > 3]
        if sum(1 for p in palavras if p in lnome.lower()) >= 2:
            melhor_id = lid
            melhor_nome = lnome
            break

    resultado.update({
        "status": "encontrado",
        "lattes_id": melhor_id,
        "lattes_url": "http://lattes.cnpq.br/" + melhor_id,
        "nome_lattes": melhor_nome,
        "total_resultados": len(ids),
    })
    return resultado

# ---- Busca Doctoralia (Playwright) ----
def buscar_doctoralia_playwright(page, nome, crm_cnes=""):
    resultado = {
        "fonte": "doctoralia", "status": "nao_encontrado",
        "doctoralia_url": "", "crm_doctoralia": "", "rqe": "",
        "especialidades_doctoralia": [], "consultorios": [], "convenios": [],
    }
    try:
        import unidecode
        slug = unidecode.unidecode(nome).lower().strip()
    except ImportError:
        slug = nome.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug)
    partes = slug.split("-")

    slugs = [slug]
    if len(partes) >= 2:
        slugs.append(partes[0] + "-" + partes[-1])
    if len(partes) > 2:
        slugs.append(partes[0] + "-" + partes[1] + "-" + partes[-1])

    for s in slugs:
        url = "https://www.doctoralia.com.br/" + s
        try:
            resp = page.goto(url, timeout=10000)
            if not resp or resp.status != 200:
                continue
            current = page.url
            if "busca?" in current or "404" in current:
                continue
            html = page.content()
            if "pagina nao encontrada" in html.lower() or "page not found" in html.lower():
                continue

            crm_extraido = ""
            m = re.search(r"CRM.{0,10}?(\d{4,})\s*([A-Z]{2})", html, re.IGNORECASE)
            if m:
                crm_extraido = m.group(1) + "/" + m.group(2)
            else:
                m2 = re.search(r"CRM[\s:-]*(\d{4,})", html, re.IGNORECASE)
                if m2:
                    crm_extraido = m2.group(1)

            if crm_cnes and crm_extraido:
                c1 = re.sub(r"[^0-9]", "", crm_cnes)
                c2 = re.sub(r"[^0-9]", "", crm_extraido)
                if c1 and c2 and c1 != c2:
                    continue

            resultado["status"] = "encontrado"
            resultado["doctoralia_url"] = current
            resultado["crm_doctoralia"] = crm_extraido

            rqe = re.search(r"RQE.{0,10}?(\d+)", html, re.IGNORECASE)
            if rqe:
                resultado["rqe"] = rqe.group(1)

            avaliacao = re.search(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
            if avaliacao:
                resultado["avaliacao"] = avaliacao.group(1)

            return resultado
        except Exception:
            continue

    resultado["status"] = "sem_resultados"
    return resultado

# ---- Links externos ----
def gerar_links_externos(nome, crm="", uf="BA"):
    nome_enc = urllib.parse.quote(nome)
    crm_num = re.sub(r"[^0-9]", "", crm) if crm else ""
    nome_slug = urllib.parse.quote(nome.lower().replace(" ", "-"))
    return {
        "cfm": "https://portal.cfm.org.br/busca-medicos/?busca=" + nome_enc + "&uf=" + uf,
        "cfm_crm": ("https://portal.cfm.org.br/busca-medicos/?crm=" + crm_num + "&uf=" + uf) if crm_num else "",
        "doctoralia": "https://www.doctoralia.com.br/busca?q=" + nome_enc,
        "escavador": "https://www.escavador.com/sobre/" + nome_slug,
        "lattes": "https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&nome=" + nome_enc + "&tipoRecurso=1",
        "google_medico": "https://www.google.com/search?q=" + nome_enc + "+medico+CRM+" + uf,
    }

# ---- Enriquecimento (sem Playwright) ----
def enriquecer_medico_simples(medico, cache, forcar=False):
    cns  = medico.get("cns", "")
    nome = medico.get("nome", "")
    if not cns or not nome or cns.startswith("SEM_CNS"):
        return None

    if not forcar and cns in cache:
        entrada = cache[cns]
        data_str = entrada.get("enriquecido_em", "")
        if data_str:
            try:
                if datetime.now() - datetime.fromisoformat(data_str) < timedelta(days=90):
                    return entrada
            except Exception:
                pass

    entrada = {
        "cns": cns, "nome": nome,
        "especialidade": medico.get("especialidade", ""),
        "crm_cnes": medico.get("crm", ""),
        "crm_uf": medico.get("crm_uf", "BA"),
        "enriquecido_em": datetime.now().isoformat(),
        "links": gerar_links_externos(nome, medico.get("crm", ""), medico.get("crm_uf", "BA")),
        "doctoralia": {"status": "nao_buscado"},
        "lattes": {},
    }
    res_lattes = buscar_lattes(nome)
    time.sleep(random.uniform(1.0, 2.5))
    entrada["lattes"] = res_lattes
    cache[cns] = entrada
    return entrada

# ---- Loop de sync ----
def run_sync(alvos, forcar=False):
    cache  = carregar_cache()
    status = carregar_status()
    status.update({
        "rodando": True, "total": len(alvos), "processados": 0,
        "encontrados_lattes": 0, "encontrados_doctoralia": 0, "erros": 0,
        "ultima_rodada": datetime.now().isoformat(),
        "proxima_rodada": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
        "playwright_ativo": PLAYWRIGHT_OK,
    })
    salvar_status(status)

    if PLAYWRIGHT_OK:
        _run_sync_playwright(alvos, cache, status, forcar)
    else:
        _run_sync_simples(alvos, cache, status, forcar)

def _run_sync_simples(alvos, cache, status, forcar):
    for i, med in enumerate(alvos):
        status["medico_atual"] = med.get("nome", "")
        try:
            entrada = enriquecer_medico_simples(med, cache, forcar)
            if entrada:
                status["processados"] += 1
                if isinstance(entrada.get("lattes"), dict) and entrada["lattes"].get("status") == "encontrado":
                    status["encontrados_lattes"] += 1
        except Exception as e:
            print("ERRO: " + str(e))
            status["erros"] += 1; status["processados"] += 1
        if (i + 1) % 10 == 0:
            salvar_cache(cache); salvar_status(status)
    salvar_cache(cache)
    status["rodando"] = False; status["medico_atual"] = None
    salvar_status(status)
    print("Concluido (simples): " + str(status["processados"]) + " | Lattes: " + str(status["encontrados_lattes"]))

def _run_sync_playwright(alvos, cache, status, forcar):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = ctx.new_page()
        for i, med in enumerate(alvos):
            cns  = med.get("cns", "")
            nome = med.get("nome", "")
            status["medico_atual"] = nome
            if not cns or not nome or cns.startswith("SEM_CNS"):
                continue
            if not forcar and cns in cache:
                entrada = cache[cns]
                data_str = entrada.get("enriquecido_em", "")
                if data_str:
                    try:
                        if datetime.now() - datetime.fromisoformat(data_str) < timedelta(days=90):
                            status["processados"] += 1; continue
                    except Exception:
                        pass
            try:
                print("   [PW] " + nome)
                entrada = {
                    "cns": cns, "nome": nome,
                    "especialidade": med.get("especialidade", ""),
                    "crm_cnes": med.get("crm", ""), "crm_uf": med.get("crm_uf", "BA"),
                    "enriquecido_em": datetime.now().isoformat(),
                    "links": gerar_links_externos(nome, med.get("crm", ""), med.get("crm_uf", "BA")),
                }
                res_doc = buscar_doctoralia_playwright(page, nome, med.get("crm", ""))
                time.sleep(random.uniform(0.8, 1.5))
                res_lattes = buscar_lattes(nome)
                time.sleep(random.uniform(0.8, 1.5))
                entrada["doctoralia"] = res_doc
                entrada["lattes"] = res_lattes
                cache[cns] = entrada
                status["processados"] += 1
                if res_lattes.get("status") == "encontrado":
                    status["encontrados_lattes"] += 1
                if res_doc.get("status") == "encontrado":
                    status["encontrados_doctoralia"] += 1
                print("      Doc: " + res_doc.get("status","?") + " | Lattes: " + res_lattes.get("status","?"))
            except Exception as e:
                print("   ERRO: " + str(e))
                status["erros"] += 1; status["processados"] += 1
            if (i + 1) % 10 == 0:
                salvar_cache(cache); salvar_status(status)
                print("   Salvo [" + str(i+1) + "/" + str(len(alvos)) + "]")
        browser.close()
    salvar_cache(cache)
    status["rodando"] = False; status["medico_atual"] = None; salvar_status(status)
    print("Concluido (Playwright): " + str(status["processados"]) + " | Doc: " + str(status["encontrados_doctoralia"]) + " | Lattes: " + str(status["encontrados_lattes"]))

# ---- CLI ----
def main(in_memory_medicos=None, arg_colih_only=False, arg_todos=False, arg_cns=None, arg_forcar=False, arg_limite=100):
    if in_memory_medicos is None:
        parser = argparse.ArgumentParser(description="Enriquecer Curriculos")
        parser.add_argument("--todos", action="store_true")
        parser.add_argument("--colih-only", action="store_true")
        parser.add_argument("--cns", type=str)
        parser.add_argument("--forcar", action="store_true")
        parser.add_argument("--limite", type=int, default=100)
        args = parser.parse_args()
        arg_colih_only = args.colih_only
        arg_todos = args.todos
        arg_cns = args.cns
        arg_forcar = args.forcar
        arg_limite = args.limite

        print("Playwright: " + ("ATIVO" if PLAYWRIGHT_OK else "inativo (so Lattes)"))
        with open(MEDICOS_FILE, "r", encoding="utf-8") as f:
            medicos = json.load(f).get("medicos", [])
    else:
        medicos = in_memory_medicos
        print("Playwright: " + ("ATIVO" if PLAYWRIGHT_OK else "inativo (so Lattes)"))
    print("Base: " + str(len(medicos)) + " medicos")
    cache = carregar_cache()
    print("Cache: " + str(len(cache)) + " enriquecidos")

    if arg_cns:
        alvos = [m for m in medicos if m.get("cns") == arg_cns]
    elif arg_colih_only:
        colih_file = DATA_DIR / "dados_colih_medicos.json"
        if colih_file.exists():
            with open(colih_file, "r", encoding="utf-8") as f:
                colih = json.load(f)
            colih_nomes = {str(c.get("nome", "")).strip().lower() for c in colih}
            alvos = [m for m in medicos if str(m.get("nome","")).strip().lower() in colih_nomes]
            print("Modo COLIH-only: " + str(len(alvos)) + " cooperadores")
        else:
            alvos = [m for m in medicos if m.get("cns") not in cache]
    elif arg_todos:
        alvos = [m for m in medicos if m.get("cns") not in cache or arg_forcar]
    else:
        alvos = [m for m in medicos if m.get("cns") not in cache]

    lim = min(len(alvos), arg_limite)
    print("Alvos filtrados: " + str(len(alvos)) + " | Limite proc: " + str(lim))
    alvos = alvos[:lim]
    
    # Free memory
    slim_alvos = []
    for m in alvos:
        slim_alvos.append({
            "cns": m.get("cns", ""),
            "nome": m.get("nome", ""),
            "especialidade": m.get("especialidade", ""),
            "crm": m.get("crm", ""),
            "crm_uf": m.get("crm_uf", "BA")
        })
    alvos = slim_alvos
    
    if in_memory_medicos is None:
        del medicos
        import gc
        gc.collect()

    if not alvos:
        print("Nenhum medico para processar.")
        return

    run_sync(alvos, forcar=arg_forcar)

if __name__ == "__main__":
    main()
