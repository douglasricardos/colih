import os
import re
import requests
import pandas as pd
import math
import json
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path
import tempfile
import urllib3
urllib3.disable_warnings()

load_dotenv(Path(__file__).parent / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
COLIH_USER = os.getenv('COLIH_USER')
COLIH_PASS = os.getenv('COLIH_PASS')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def clean_val(v):
    if pd.isna(v): return None
    if isinstance(v, float) and math.isnan(v): return None
    s = str(v).strip()
    return s if s else None

def get_current_data():
    current_docs = []
    current_mem = []
    if supabase:
        try:
            docs_res = supabase.table('dados_colih_medicos').select('nome').execute()
            current_docs = [r['nome'] for r in docs_res.data if r.get('nome')]
            mem_res = supabase.table('dados_colih_membros').select('nome').execute()
            current_mem = [r['nome'] for r in mem_res.data if r.get('nome')]
        except Exception as e:
            print("Supabase err:", e)
    return current_docs, current_mem

def sync_colih_data(preview=False, commit=False, discard=False):
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    preview_file = data_dir / 'preview_colih.json'

    if discard:
        if preview_file.exists():
            preview_file.unlink()
        return {"success": True, "message": "Preview descartado."}

    if commit:
        if not preview_file.exists():
            return {"success": False, "error": "Arquivo de preview não encontrado."}
        
        with open(preview_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        docs_records = data.get('docs_records', [])
        membros_records = data.get('membros_records', [])
        
        if supabase:
            # Clear Supabase
            supabase.table('dados_colih_medicos').delete().neq('id', 0).execute()
            supabase.table('dados_colih_membros').delete().neq('id', 0).execute()
            
            # Batch insert doctors
            for i in range(0, len(docs_records), 100):
                supabase.table('dados_colih_medicos').insert(docs_records[i:i+100]).execute()
            
            # Batch insert members
            for i in range(0, len(membros_records), 100):
                supabase.table('dados_colih_membros').insert(membros_records[i:i+100]).execute()
                
        preview_file.unlink()
        return {"success": True, "message": "Dados da COLIH aplicados com sucesso."}

    # Otherwise, download and generate preview (or run full sync if preview=False and not commit/discard, but we'll always use preview flow now)
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        # Login
        resp = session.get('https://salvador.colih.med.br', timeout=30, verify=False)
        csrf = re.search(r'name="_token"[^>]+value="([^"]+)"', resp.text)
        if not csrf: csrf = re.search(r'name="csrf-token" content="([^"]+)"', resp.text)
        
        if not csrf:
            return {"success": False, "error": "CSRF token not found. Site structure might have changed."}
            
        csrf_token = csrf.group(1)
        
        login_resp = session.post(
            'https://salvador.colih.med.br/auth/login',
            data={'_token': csrf_token, 'username': COLIH_USER, 'password': COLIH_PASS},
            headers={'Referer': 'https://salvador.colih.med.br/auth/login'},
            allow_redirects=True, timeout=30, verify=False
        )
        
        if 'panel' not in login_resp.url and 'dashboard' not in login_resp.url:
            return {"success": False, "error": "Login failed. Invalid credentials or captcha."}
            
        # Download Doctors
        docs_url = 'https://salvador.colih.med.br/panel/doctors/export?type=xls&moreFilters=0&isMultipleRegions=1&cooperationLevel=9&region=1&sortOrder=nm'
        docs_resp = session.get(docs_url, timeout=60, verify=False)
        
        # Local members file
        mem_file = r'C:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Salvador\Lista_Membros_16-06-2026.xlsx'
        
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_file = Path(tmpdir) / 'doctors.xlsx'
            with open(docs_file, 'wb') as f: f.write(docs_resp.content)
            
            df_docs = pd.read_excel(docs_file, engine='openpyxl')
            df_mem = pd.DataFrame()
            if os.path.exists(mem_file):
                df_mem = pd.read_excel(mem_file, engine='openpyxl')
            
            # Read CSV Coordinates
            csv_path = r'C:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Salvador\lista_membros_para_coordenadas.csv'
            coords_map = {}
            if os.path.exists(csv_path):
                import unicodedata
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    lines = f.readlines()
                    for line in lines[1:]: # skip header
                        parts = line.split(';')
                        if len(parts) >= 3:
                            raw_nome = parts[0].strip().upper()
                            nome = ''.join(c for c in unicodedata.normalize('NFKD', raw_nome) if not unicodedata.combining(c))
                            end = parts[1].strip()
                            coords = parts[2].split(',')
                            lat = coords[0].strip() if len(coords) > 0 else None
                            lon = coords[1].strip() if len(coords) > 1 else None
                            coords_map[nome] = {'end': end, 'lat': lat, 'lon': lon}
                            
            # Process Doctors
            docs_records = []
            new_docs_names = []
            for _, row in df_docs.iterrows():
                nome_clean = clean_val(row.get('Nome'))
                if nome_clean: new_docs_names.append(nome_clean)
                rec = {
                    'nome': nome_clean,
                    'especialidade_1_hid': clean_val(row.get('Especialidade 1 - HID')),
                    'especialidade_1_colih': clean_val(row.get('Especialidade 1 - Colih')),
                    'especialidade_2_hid': clean_val(row.get('Especialidade 2 - HID')),
                    'especialidade_2_colih': clean_val(row.get('Especialidade 2 - Colih')),
                    'especialidade_3_hid': clean_val(row.get('Especialidade 3 - HID')),
                    'especialidade_3_colih': clean_val(row.get('Especialidade 3 - Colih')),
                    'especialidade_4_hid': clean_val(row.get('Especialidade 4 - HID')),
                    'especialidade_4_colih': clean_val(row.get('Especialidade 4 - Colih')),
                    'atende_menores': clean_val(row.get('Atende Menores')),
                    'atende_bebes': clean_val(row.get('Atende Bebês')),
                    'atende_sus': clean_val(row.get('Atende SUS')),
                    'ultima_visita': clean_val(row.get('Última visita')),
                    'e_tj': clean_val(row.get('É TJ?')),
                    'e_consultor': clean_val(row.get('É Consultor?')),
                    'membro_resp': clean_val(row.get('Membro resp.')),
                    'colaboracao': clean_val(row.get('Colaboração')),
                    'atende_particular': clean_val(row.get('Atende Particular')),
                    'preencheu_hlc23': clean_val(row.get('Prencheu HLC-23')),
                    'tem_pasta_csa': clean_val(row.get('Tem Pasta CSA')),
                    'e_cirurgiao': clean_val(row.get('É cirurgião')),
                    'secretaria': clean_val(row.get('Secretária(o)')),
                    'telefone': clean_val(row.get('Telefone')),
                    'celular': clean_val(row.get('Celular')),
                    'endereco_consultorio': clean_val(row.get('Endereço Consultório')),
                    'email': clean_val(row.get('E-mail')),
                    'hospitais': clean_val(row.get('Hospitais')),
                    'convenios': clean_val(row.get('Convênios')),
                    'observacoes': clean_val(row.get('Observações'))
                }
                docs_records.append(rec)
            
            # Process Members
            membros_records = []
            new_mem_names = []
            if not df_mem.empty:
                for _, row in df_mem.iterrows():
                    nome = clean_val(row.get('Nome'))
                    if nome: new_mem_names.append(nome)
                    
                    import unicodedata
                    norm_nome = ''.join(c for c in unicodedata.normalize('NFKD', str(nome).upper()) if not unicodedata.combining(c))
                    
                    c_data = coords_map.get(norm_nome, {})
                    
                    rec = {
                        'nome': nome,
                        'telefone': clean_val(row.get('Telefone')),
                        'email_particular': clean_val(row.get('E-mail Particular')),
                        'email_jwpub': clean_val(row.get('E-mail JWPub')),
                        'hospital': clean_val(row.get('Hospital')),
                        'funcao': clean_val(row.get('Função')),
                        'regiao': clean_val(row.get('Região')),
                        'endereco_atual': c_data.get('end'),
                        'lat': c_data.get('lat'),
                        'lon': c_data.get('lon')
                    }
                    membros_records.append(rec)

            # Generate Diff
            current_docs, current_mem = get_current_data()
            
            added_docs = [n for n in new_docs_names if n not in current_docs]
            removed_docs = [n for n in current_docs if n not in new_docs_names]
            
            added_mem = [n for n in new_mem_names if n not in current_mem]
            removed_mem = [n for n in current_mem if n not in new_mem_names]
            
            preview_data = {
                "diff": {
                    "docs_added": added_docs,
                    "docs_removed": removed_docs,
                    "mem_added": added_mem,
                    "mem_removed": removed_mem
                },
                "docs_records": docs_records,
                "membros_records": membros_records
            }
            
            if preview:
                with open(preview_file, 'w', encoding='utf-8') as f:
                    json.dump(preview_data, f, ensure_ascii=False)
                return {"success": True, "preview_ready": True, "diff": preview_data["diff"]}
            else:
                # If not preview, just apply it (legacy or fallback mode)
                if supabase:
                    supabase.table('dados_colih_medicos').delete().neq('id', 0).execute()
                    supabase.table('dados_colih_membros').delete().neq('id', 0).execute()
                    for i in range(0, len(docs_records), 100):
                        supabase.table('dados_colih_medicos').insert(docs_records[i:i+100]).execute()
                    for i in range(0, len(membros_records), 100):
                        supabase.table('dados_colih_membros').insert(membros_records[i:i+100]).execute()
                return {"success": True, "message": "Dados atualizados."}
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == '__main__':
    # For testing
    res = sync_colih_data(preview=True)
    print("Preview res:", res)
