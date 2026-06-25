"""
COLIH Captação — Script de Enriquecimento de Currículos (Headless)
=========================================================
Enriquece os perfis dos médicos da base com dados de:
  1. DATASUS/CNES: CRM já extraído durante a sync principal
  2. Doctoralia BR: via Navegação Simulada (Playwright) e extração de DOM
     - CRM e validação de perfil
  3. Plataforma Lattes (CNPq): busca por nome via urllib (rápido e sem JS)
  4. Links diretos para CFM Portal, Escavador, Doctoralia (verificação manual)
"""

import json
import time
import re
import random
import argparse
import sys
import urllib.request
import urllib.parse
import urllib.error
import ssl
from pathlib import Path
from datetime import datetime, timedelta

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("ERRO: Playwright não instalado. Rode: pip install playwright && playwright install chromium")
    sys.exit(1)

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = Path(__file__).parent.parent / "backend" / "data"
CACHE_FILE = DATA_DIR / "curriculos_cache.json"
MEDICOS_FILE = DATA_DIR / "medicos_cache.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

def carregar_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def salvar_cache(cache: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def fetch_html_lattes(url: str, timeout=15) -> str | None:
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read()
            enc = resp.headers.get_content_charset() or "utf-8"
            try:
                return raw.decode(enc)
            except Exception:
                return raw.decode("utf-8", errors="replace")
    except Exception as e:
        return None

def buscar_lattes(nome: str) -> dict:
    resultado = {"fonte": "lattes", "status": "nao_encontrado"}
    query = urllib.parse.quote(nome)
    url = f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&nome={query}&tipoRecurso=1"
    
    html = fetch_html_lattes(url)
    if not html:
        resultado["status"] = "erro_rede"
        return resultado
    
    ids = re.findall(r'visualizacv\.do\?id=([A-Z0-9]+)', html)
    nomes_lattes = re.findall(r'class="nomeRPCV"[^>]*>([^<]+)<', html)
    
    if not ids:
        resultado["status"] = "sem_resultados"
        return resultado
    
    nome_norm = nome.lower().strip()
    melhor_id = ids[0]
    melhor_nome = nomes_lattes[0] if nomes_lattes else ""
    
    for i, (lid, lnome) in enumerate(zip(ids, nomes_lattes)):
        lnome_norm = lnome.lower().strip()
        palavras = [p for p in nome_norm.split() if len(p) > 3]
        if sum(1 for p in palavras if p in lnome_norm) >= 2:
            melhor_id = lid
            melhor_nome = lnome
            break
            
    resultado.update({
        "status": "encontrado",
        "lattes_id": melhor_id,
        "lattes_url": f"http://lattes.cnpq.br/{melhor_id}",
        "lattes_cv_url": f"https://curriculo-lattes.cnpq.br/{melhor_id}.xml",
        "nome_lattes": melhor_nome,
        "total_resultados": len(ids),
    })
    return resultado

import unidecode

def gerar_links_externos(nome: str, crm: str = "", uf: str = "BA") -> dict:
    nome_enc = urllib.parse.quote(nome)
    crm_num = re.sub(r"[^0-9]", "", crm) if crm else ""
    return {
        "cfm": f"https://portal.cfm.org.br/busca-medicos/?busca={nome_enc}&uf={uf}",
        "cfm_crm": f"https://portal.cfm.org.br/busca-medicos/?crm={crm_num}&uf={uf}" if crm_num else "",
        "doctoralia": f"https://www.doctoralia.com.br/busca?q={nome_enc}",
        "medicosbrasil": f"https://www.medicosbrasil.com/busca?q={nome_enc}",
        "instagram": f"https://www.instagram.com/explore/search/keyword/?q={nome_enc}",
        "lattes": f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&nome={nome_enc}&tipoRecurso=1",
        "google_medico": f"https://www.google.com/search?q={nome_enc}+médico+CRM+{uf}",
    }

def buscar_doctoralia_playwright(page, nome: str, crm_cnes: str = "") -> dict:
    resultado = {
        "fonte": "doctoralia", 
        "status": "nao_encontrado",
        "doctoralia_url": "",
        "crm_doctoralia": "",
        "rqe": "",
        "foto_url": "",
        "especialidades_doctoralia": [],
        "consultorios": [],
        "convenios": [],
        "formacao_doctoralia": [],
    }
    
    slug = unidecode.unidecode(nome).lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    
    partes = slug.split('-')
    urls_para_testar = []
    
    if len(partes) <= 1:
        urls_para_testar.append(f"https://www.doctoralia.com.br/{slug}")
    else:
        slugs = [slug]
        
        slug_curto = f"{partes[0]}-{partes[-1]}"
        if slug_curto not in slugs:
            slugs.append(slug_curto)
            
        if len(partes) > 2:
            slug_penultimo = f"{partes[0]}-{partes[-2]}"
            if slug_penultimo not in slugs:
                slugs.append(slug_penultimo)
                
            slug_a_b_d = f"{partes[0]}-{partes[1]}-{partes[-1]}"
            if slug_a_b_d not in slugs:
                slugs.append(slug_a_b_d)
                
        # Invertido: ultimo-primeiro
        slug_invertido = f"{partes[-1]}-{partes[0]}"
        if slug_invertido not in slugs:
            slugs.append(slug_invertido)
                
        for s in slugs:
            urls_para_testar.append(f"https://www.doctoralia.com.br/{s}")
    
    for direto in urls_para_testar:
        try:
            resp = page.goto(direto, timeout=8000)
            if resp and resp.status == 200 and 'doctoralia.com.br/medico' not in page.url and 'doctoralia.com.br/clinicas' not in page.url and 'busca?' not in page.url:
                html = page.content()
                
                if "página não encontrada" in html.lower() or "page not found" in html.lower():
                    continue
            
                crm_extraido = ""
                crm_match = re.search(r'CRM.{0,10}?(\d+)\s*([A-Z]{2})', html, re.IGNORECASE)
                if crm_match:
                    crm_extraido = f"{crm_match.group(1)}/{crm_match.group(2)}"
                else:
                    crm_simple = re.search(r'CRM[\s:-]*(\d+)', html, re.IGNORECASE)
                    if crm_simple:
                        crm_extraido = crm_simple.group(1)
                        
                # Validar CRM para evitar homônimos
                if crm_cnes and crm_extraido:
                    crm_cnes_clean = re.sub(r'[^0-9]', '', crm_cnes)
                    crm_doc_clean = re.sub(r'[^0-9]', '', crm_extraido)
                    if crm_cnes_clean and crm_doc_clean and crm_cnes_clean != crm_doc_clean:
                        continue # Homônimo ou CRM errado, tenta o próximo slug
                        
                # Se validou ou não havia CRM no CNES para validar, é sucesso!
                resultado["crm_doctoralia"] = crm_extraido
                resultado["status"] = "encontrado"
                resultado["doctoralia_url"] = page.url
                
                rqe_match = re.search(r'RQE.{0,10}?(\d+)', html, re.IGNORECASE)
                if rqe_match:
                    resultado["rqe"] = rqe_match.group(1)
                    
                addresses = page.locator('.media-body').all()
                for addr in addresses:
                    texto = addr.inner_text().strip()
                    if texto and "ampliar o mapa" in texto.lower() or "salvador" in texto.lower() or "rua" in texto.lower():
                        linhas = [t.strip() for t in texto.split('\n') if t.strip() and t.strip().lower() != 'ampliar o mapa']
                        if linhas:
                            resultado["consultorios"].append({
                                "nome": linhas[0],
                                "endereco": ", ".join(linhas[1:]),
                                "telefone": ""
                            })
                    
                return resultado
            
        except PlaywrightTimeoutError:
            continue
        except Exception as e:
            print(f"Doctoralia Exception: {e}")
            continue
            
    resultado["status"] = "sem_resultados"
    return resultado

def enriquecer_medico_pw(page, medico: dict, cache: dict, forcar=False) -> dict:
    cns = medico.get("cns", "")
    nome = medico.get("nome", "")
    especialidade = medico.get("especialidade", "")
    crm_cnes = medico.get("crm", "")
    crm_uf = medico.get("crm_uf", "BA")
    
    if not cns or not nome or cns.startswith("SEM_CNS"):
        return None
        
    if not forcar and cns in cache:
        entrada = cache[cns]
        data_str = entrada.get("enriquecido_em", "")
        if data_str:
            try:
                data_enr = datetime.fromisoformat(data_str)
                if datetime.now() - data_enr < timedelta(days=30):
                    return entrada
            except Exception:
                pass
                
    print(f"   🔍 Enriquecendo: {nome} (CNS: {cns})")
    
    entrada = {
        "cns": cns,
        "nome": nome,
        "especialidade": especialidade,
        "crm_cnes": crm_cnes,
        "crm_uf": crm_uf,
        "enriquecido_em": datetime.now().isoformat(),
        "links": gerar_links_externos(nome, crm_cnes, crm_uf),
    }
    
    res_doc = buscar_doctoralia_playwright(page, nome, crm_cnes)
    time.sleep(random.uniform(0.5, 1.5))
    
    res_lattes = buscar_lattes(nome)
    time.sleep(random.uniform(0.5, 1.5))
    
    entrada["doctoralia"] = res_doc
    entrada["lattes"] = res_lattes
    
    print(f"      Doctoralia: {res_doc['status']} | CRM: {res_doc.get('crm_doctoralia') or '—'}")
    print(f"      Lattes: {res_lattes['status']} | {res_lattes.get('nome_lattes') or '—'}")
    
    cache[cns] = entrada
    return entrada

def main():
    parser = argparse.ArgumentParser(description="Enriquecer Currículos (Playwright)")
    parser.add_argument("--todos", action="store_true", help="Enriquecer todos pendentes")
    parser.add_argument("--cns", type=str, help="Enriquecer apenas um CNS específico")
    parser.add_argument("--forcar", action="store_true", help="Ignorar cache e forçar busca")
    parser.add_argument("--limite", type=int, default=50, help="Limite máximo por rodada")
    args = parser.parse_args()

    if not MEDICOS_FILE.exists():
        print(f"❌ Base não encontrada: {MEDICOS_FILE}")
        return

    with open(MEDICOS_FILE, "r", encoding="utf-8") as f:
        data_med = json.load(f)
    medicos = data_med.get("medicos", [])
    print(f"📦 Base carregada: {len(medicos)} médicos")

    cache = carregar_cache()
    print(f"💾 Cache existente: {len(cache)} médicos já enriquecidos")

    alvos = []
    if args.cns:
        alvos = [m for m in medicos if m.get("cns") == args.cns]
    elif args.todos:
        alvos = [m for m in medicos if m.get("cns") not in cache or args.forcar]
    else:
        alvos = [m for m in medicos if m.get("cns") not in cache]
        random.shuffle(alvos)

    alvos = alvos[:args.limite]
    print(f"🎯 Médicos a enriquecer: {len(alvos)}\n" + "─"*60)

    if not alvos:
        print("✅ Nenhum médico pendente.")
        return

    erros = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        for i, med in enumerate(alvos):
            try:
                enriquecer_medico_pw(page, med, cache, forcar=args.forcar)
            except Exception as e:
                print(f"   ❌ Erro ao processar {med.get('nome')}: {e}")
                erros += 1
            
            if (i + 1) % 5 == 0:
                salvar_cache(cache)
                
        browser.close()

    salvar_cache(cache)
    print("─"*60)
    print(f"✅ Concluído! {len(alvos) - erros} enriquecidos. {erros} erros.")
    print(f"📁 Cache salvo em: {CACHE_FILE}")

if __name__ == "__main__":
    main()
