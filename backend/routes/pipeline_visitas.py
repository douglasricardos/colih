import os
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

class InstituicaoPipelineReq(BaseModel):
    telefone: Optional[str] = None
    contato_nome: Optional[str] = None
    notas: Optional[str] = None
    grupo_id: Optional[str] = None
    grupo_nome: Optional[str] = None
    nome: Optional[str] = None

class VisitaReq(BaseModel):
    medico_cns: str
    medico_nome: str
    instituicao_cnes: str
    instituicao_nome: str
    grupo_id: str
    grupo_nome: str
    data_agendada: str
    janela_descricao: Optional[str] = None
    criado_por: str

class VisitaResultadoReq(BaseModel):
    status: str
    motivo: Optional[str] = None
    falha_de: Optional[str] = None
    membro_continua: Optional[bool] = None

class SettingsReq(BaseModel):
    webhook_n8n_url: Optional[str] = None
    evolution_instance: Optional[str] = None
    template_mensagem_convite: Optional[str] = None
    template_mensagem_grupo: Optional[str] = None
    retencao_historico_meses: Optional[int] = None

def check_supabase():
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase não configurado.")

@router.get("/api/instituicoes-pipeline/{cnes}/{medico_cns}")
def get_instituicao_pipeline(cnes: str, medico_cns: str):
    check_supabase()
    res = supabase.table("instituicoes_pipeline").select("*").eq("cnes", cnes).eq("medico_cns", medico_cns).execute()
    if res.data:
        return res.data[0]
    return {}

@router.post("/api/instituicoes-pipeline/{cnes}/{medico_cns}")
@router.put("/api/instituicoes-pipeline/{cnes}/{medico_cns}")
def upsert_instituicao_pipeline(cnes: str, medico_cns: str, dados: InstituicaoPipelineReq):
    check_supabase()
    agora = datetime.now().isoformat()
    res = supabase.table("instituicoes_pipeline").select("id").eq("cnes", cnes).eq("medico_cns", medico_cns).execute()
    payload = {
        "cnes": cnes, "medico_cns": medico_cns, "telefone": dados.telefone,
        "contato_nome": dados.contato_nome, "notas": dados.notas,
        "grupo_id": dados.grupo_id, "grupo_nome": dados.grupo_nome, "nome": dados.nome,
        "atualizado_em": agora
    }
    if res.data:
        res_up = supabase.table("instituicoes_pipeline").update(payload).eq("id", res.data[0]["id"]).execute()
        return res_up.data[0]
    payload["criado_em"] = agora
    res_in = supabase.table("instituicoes_pipeline").insert(payload).execute()
    return res_in.data[0]

@router.get("/api/grupos")
def listar_grupos():
    check_supabase()
    res = supabase.table("dados_colih_membros").select("grupo_id, grupo_nome").execute()
    grupos_map = {}
    for r in res.data:
        if r.get("grupo_id"):
            grupos_map[r["grupo_id"]] = r["grupo_nome"]
    grupos = [{"id": k, "nome": v} for k, v in grupos_map.items()]
    return {"grupos": sorted(grupos, key=lambda x: x["nome"] or "")}

@router.post("/api/visitas")
def criar_visita(dados: VisitaReq):
    check_supabase()
    agora = datetime.now().isoformat()
    payload = {
        "medico_cns": dados.medico_cns, "medico_nome": dados.medico_nome,
        "instituicao_cnes": dados.instituicao_cnes, "instituicao_nome": dados.instituicao_nome,
        "grupo_id": dados.grupo_id, "grupo_nome": dados.grupo_nome,
        "data_agendada": dados.data_agendada, "janela_descricao": dados.janela_descricao,
        "criado_por": dados.criado_por, "status": "agendada", "criado_em": agora, "atualizado_em": agora
    }
    vis_res = supabase.table("visitas").insert(payload).execute()
    v_id = vis_res.data[0]["id"]
    supabase.table("visitas_historico").insert({"visita_id": v_id, "evento": "agendamento", "criado_em": agora}).execute()
    
    membros = supabase.table("dados_colih_membros").select("*").eq("grupo_id", dados.grupo_id).execute().data
    for i, m in enumerate(membros):
        supabase.table("membros_fila").insert({
            "visita_id": v_id, "membro_id": m.get("id", str(m.get("nome"))),
            "membro_nome": m.get("nome"), "membro_whatsapp": m.get("telefone"),
            "ordem": i + 1, "status": "pendente"
        }).execute()
    return {"ok": True, "visita_id": v_id}

@router.get("/api/visitas/calendario")
def listar_calendario():
    check_supabase()
    res = supabase.table("visitas").select("*").execute()
    return {"visitas": res.data}

@router.post("/api/visitas/{visita_id}/resultado")
def postar_resultado(visita_id: str, dados: VisitaResultadoReq):
    check_supabase()
    agora = datetime.now().isoformat()
    supabase.table("visitas").update({"status": dados.status, "atualizado_em": agora}).eq("id", visita_id).execute()
    supabase.table("visitas_historico").insert({
        "visita_id": visita_id, "evento": dados.status, "motivo": dados.motivo,
        "falha_de": dados.falha_de, "membro_continua": dados.membro_continua, "criado_em": agora
    }).execute()
    return {"ok": True}

@router.get("/api/settings")
def get_settings():
    check_supabase()
    res = supabase.table("app_settings").select("*").execute()
    return {row["chave"]: row["valor"] for row in res.data}

@router.put("/api/settings")
def save_settings(dados: SettingsReq):
    check_supabase()
    for k, v in dados.dict(exclude_none=True).items():
        if supabase.table("app_settings").select("chave").eq("chave", k).execute().data:
            supabase.table("app_settings").update({"valor": v}).eq("chave", k).execute()
        else:
            supabase.table("app_settings").insert({"chave": k, "valor": v}).execute()
    return {"ok": True}

@router.get("/visita/aceite/{token}", response_class=HTMLResponse)
def page_aceite(token: str):
    check_supabase()
    res = supabase.table("membros_fila").select("*, visitas(*)").eq("token", token).execute()
    if not res.data: return "<h1>Token inválido.</h1>"
    f = res.data[0]
    v = f["visitas"]
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Aceitar Visita</title>
<style>body{{font-family:sans-serif;background:#f4f4f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}}
.card{{background:white;padding:24px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);max-width:400px;width:100%;}}
.btn{{display:block;width:100%;padding:12px;margin-top:12px;border:none;border-radius:6px;font-size:16px;cursor:pointer;color:white;}}
.btn-accept{{background:#22c55e;}}.btn-reject{{background:#ef4444;}}</style></head>
<body><div class="card"><h2>Olá, {f['membro_nome']}!</h2><p>Você tem uma visita:</p>
<ul><li><strong>Médico:</strong> {v['medico_nome']}</li><li><strong>Local:</strong> {v['instituicao_nome']}</li><li><strong>Data:</strong> {v['data_agendada']} {v['janela_descricao'] or ''}</li></ul>
<button class="btn btn-accept" onclick="responder(true)">✅ Aceitar</button>
<button class="btn btn-reject" onclick="responder(false)">❌ Recusar</button>
<div id="resultado" style="margin-top:16px;font-weight:bold;text-align:center;"></div></div>
<script>async function responder(aceito){{
const r=await fetch('/api/visitas/aceite/{token}',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{aceito:aceito}})}});
const d=await r.json();if(d.ok){{document.getElementById('resultado').innerText=aceito?'Visita confirmada!':'Visita recusada.';
document.querySelectorAll('.btn').forEach(b=>b.style.display='none');}}else{{document.getElementById('resultado').innerText='Erro.';}}
}}</script></body></html>'''

class AceiteReq(BaseModel):
    aceito: bool
    motivo: Optional[str] = None

@router.post("/api/visitas/aceite/{token}")
def post_aceite(token: str, dados: AceiteReq):
    check_supabase()
    agora = datetime.now().isoformat()
    res = supabase.table("membros_fila").select("*").eq("token", token).execute()
    if not res.data: raise HTTPException(status_code=404, detail="Token inválido")
    f = res.data[0]
    if f["status"] != "pendente": return {"ok": False, "mensagem": "Já respondido"}
    supabase.table("membros_fila").update({"status": "aceito" if dados.aceito else "recusado", "respondido_em": agora}).eq("id", f["id"]).execute()
    
    if dados.aceito:
        supabase.table("visitas").update({"membro_designado_id": f["membro_id"], "membro_designado_nome": f["membro_nome"], "atualizado_em": agora}).eq("id", f["visita_id"]).execute()
        supabase.table("visitas_historico").insert({"visita_id": f["visita_id"], "evento": "aceite", "membro_id": f["membro_id"], "membro_nome": f["membro_nome"], "criado_em": agora}).execute()
    else:
        supabase.table("visitas_historico").insert({"visita_id": f["visita_id"], "evento": "recusa", "membro_id": f["membro_id"], "membro_nome": f["membro_nome"], "motivo": dados.motivo, "criado_em": agora}).execute()
    return {"ok": True}
