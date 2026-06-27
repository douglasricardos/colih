import os
import json
import time
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'backend', 'data')
CURRICULOS_DIR = os.path.join(DATA_DIR, 'curriculos')

STATUS_FILE = os.path.join(DATA_DIR, 'sync_crm_status.json')
MEDICOS_FILE = os.path.join(DATA_DIR, 'medicos_cache.json')

API_KEY = "5300468837"
MONTHLY_LIMIT = 100

def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def carregar_status():
    status = load_json(STATUS_FILE, {
        "rodando": False,
        "mes_atual": datetime.now().strftime("%Y-%m"),
        "api_consultas": 0,
        "total_medicos": 0,
        "processados": 0,
        "erros": 0
    })
    
    mes_agora = datetime.now().strftime("%Y-%m")
    if status.get("mes_atual") != mes_agora:
        status["mes_atual"] = mes_agora
        status["api_consultas"] = 0
        status["processados"] = 0
        status["erros"] = 0
        status["rodando"] = True 
    
    return status

def get_medicos_priorizados():
    medicos_dict = load_json(MEDICOS_FILE, {})
    
    try:
        pipeline_data = requests.get("http://127.0.0.1:8000/api/pipeline").json()
        pipeline_cns = [p.get("cns") for p in pipeline_data if p.get("cns")]
    except:
        pipeline_cns = []
        
    try:
        colih_data = requests.get("http://127.0.0.1:8000/api/colih/medicos").json()
        colih_names = [m.get("nome", "").strip().upper() for m in colih_data]
    except:
        colih_names = []
    
    lista = []
    medicos_list = medicos_dict.get("medicos", [])
    for m in medicos_list:
        cns = m.get("cns")
        if not cns: continue
        
        curr_path = os.path.join(CURRICULOS_DIR, f"{cns}.json")
        has_crm_data = False
        if os.path.exists(curr_path):
            curr = load_json(curr_path, {})
            if curr.get("data", {}).get("consultacrm"):
                has_crm_data = True
        
        if not has_crm_data:
            score = 1
            if cns in pipeline_cns:
                score = 3
            elif m.get("nome", "").strip().upper() in colih_names:
                score = 2
            
            lista.append((score, m))
            
    lista.sort(key=lambda x: x[0], reverse=True)
    return [m for score, m in lista]

def fetch_crm_api(nome):
    url = "https://www.consultacrm.com.br/api/index.php"
    params = {
        "tipo": "crm",
        "q": nome,
        "chave": API_KEY,
        "destino": "xml"
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        
        root = ET.fromstring(r.text)
        channel = root.find("channel")
        if channel is None: return None
        
        api_consultas = channel.find("api_consultas")
        consultas = int(api_consultas.text) if api_consultas is not None and api_consultas.text else 0
        
        item = channel.find("item")
        if item is not None:
            numero = item.find("numero").text if item.find("numero") is not None else ""
            uf = item.find("uf").text if item.find("uf") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            
            return {
                "encontrado": True,
                "api_consultas": consultas,
                "dados": {
                    "crm": numero,
                    "uf": uf,
                    "link": link
                }
            }
        else:
            return {
                "encontrado": False,
                "api_consultas": consultas,
                "dados": None
            }
            
    except Exception as e:
        print(f"Erro na API para {nome}: {e}")
        return None

def scrape_biografia(link):
    if not link: return ""
    try:
        r = requests.get(link, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # O texto "Sobre" geralmente fica numa tag específica, pelo exemplo do usuário.
        # Procurando h3 "Sobre" ou a div com text
        sobre_header = soup.find(lambda tag: tag.name in ["h2", "h3", "h4"] and "Sobre" in tag.text)
        if sobre_header:
            p = sobre_header.find_next_sibling("p")
            if p:
                return p.get_text(strip=True)
                
        # Fallback: tentar achar pelo texto conhecido do exemplo
        # Procurando o elemento principal do perfil
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 100 and "é um profissional médico" in text or "experiência em sua área" in text:
                return text
                
        # Se não achou de forma específica, pega os p tags e filtra
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 80]
        if paragraphs:
            return paragraphs[0] # Assume o primeiro parágrafo longo como bio
            
    except Exception as e:
        print(f"Erro no scraping de {link}: {e}")
    return ""

def main():
    status = carregar_status()
    
    if status["api_consultas"] >= MONTHLY_LIMIT:
        print("Limite mensal já atingido. Saindo...")
        status["rodando"] = False
        save_json(STATUS_FILE, status)
        return
        
    status["rodando"] = True
    save_json(STATUS_FILE, status)
    
    print("Obtendo fila de médicos...")
    fila = get_medicos_priorizados()
    status["total_medicos"] = len(fila)
    save_json(STATUS_FILE, status)
    
    print(f"Iniciando busca. Fila: {len(fila)} médicos. Consultas já feitas: {status['api_consultas']}/{MONTHLY_LIMIT}")
    
    for m in fila:
        if status["api_consultas"] >= MONTHLY_LIMIT:
            print("Limite mensal alcançado durante a execução. Parando.")
            break
            
        cns = m['cns']
        nome = m['nome']
        print(f"[{status['api_consultas']}/{MONTHLY_LIMIT}] Buscando: {nome}")
        
        res = fetch_crm_api(nome)
        
        if res:
            # Atualiza o contador de uso com o valor exato que a API retornou
            if res["api_consultas"] > status["api_consultas"]:
                status["api_consultas"] = res["api_consultas"]
            
            # Se a API retornou 0 mas nós sabemos que gastamos uma consulta (porque achou ou buscou válido),
            # Vamos incrementar localmente se a API nao atualizou ainda. 
            # Mas o melhor é confiar na API. Na dúvida, assumir +1 se não estava mapeado
            elif res["encontrado"]:
                # Alguns endpoints contam apenas consultas encontradas
                status["api_consultas"] += 1

            curr_path = os.path.join(CURRICULOS_DIR, f"{cns}.json")
            curr = load_json(curr_path, {"cns": cns, "data": {}})
            
            if "data" not in curr: curr["data"] = {}
            
            if res["encontrado"]:
                dados = res["dados"]
                bio = scrape_biografia(dados["link"])
                
                curr["data"]["consultacrm"] = {
                    "status": "encontrado",
                    "crm": dados["crm"],
                    "uf": dados["uf"],
                    "url": dados["link"],
                    "biografia": bio,
                    "atualizado_em": datetime.now().isoformat()
                }
                print(f" -> Encontrado! CRM: {dados['crm']}-{dados['uf']}")
            else:
                curr["data"]["consultacrm"] = {
                    "status": "nao_encontrado",
                    "atualizado_em": datetime.now().isoformat()
                }
                print(f" -> Não encontrado na API.")
                
            save_json(curr_path, curr)
            status["processados"] += 1
        else:
            status["erros"] += 1
            print(f" -> Falha na requisição.")
            
        # Salva o status a cada requisição
        save_json(STATUS_FILE, status)
        time.sleep(2.5) # Sleep para não martelar a API
        
    status["rodando"] = False
    save_json(STATUS_FILE, status)
    print("Processamento finalizado!")

if __name__ == "__main__":
    main()
