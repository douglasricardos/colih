# COLIH Captação — Sistema de Médicos Cooperadores
## Salvador, Bahia

Sistema web para identificar, filtrar e contatar médicos potencialmente cooperadores para a COLIH Salvador. Baseado nos dados públicos do CNES/DATASUS.

---

## 🚀 Instalação e Uso

### Pré-requisitos
- **Python 3.10+** instalado
- **curl** disponível no PATH (Windows 10/11: já vem instalado por padrão)
- Conexão de internet (para sincronizar com o DATASUS)

### 1. Clonar o repositório
```bash
git clone https://github.com/<seu-usuario>/COLIH_Captacao.git
cd COLIH_Captacao
```

### 2. Criar e ativar o ambiente virtual
```bash
# Windows
python -m venv backend/venv
backend\venv\Scripts\activate

# Linux / Mac
python3 -m venv backend/venv
source backend/venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r backend/requirements.txt
```

### 4. Iniciar o servidor
```bash
# Windows — duplo-clique em:
iniciar.bat

# Ou via terminal:
cd backend
..\backend\venv\Scripts\python.exe -m uvicorn server:app --host 0.0.0.0 --port 8000
```

### 5. Acessar o sistema
Abra no navegador: **http://localhost:8000**

### 6. Sincronizar dados do CNES (primeiro acesso)
Na interface, clique no badge **"Fonte CNES (Status)"** no cabeçalho → **"Forçar Atualização"**.

> ⚠️ O download da base do DATASUS tem ~1.5GB. A sincronização leva alguns minutos dependendo da sua conexão. O progresso é exibido na tela.

Alternativamente, via terminal:
```bash
cd backend
..\backend\venv\Scripts\python.exe ..\scripts\atualizar_cache.py
```

---

## 📱 Fluxo de Uso

### Fluxo A — Por Hospital
1. Aba **🏥 Buscar Hospital** → filtrar por complexidade, município ou especialidade
2. Clicar no hospital → ver ficha completa (serviços, leitos, equipamentos, alta complexidade)
3. Filtrar médicos vinculados por especialidade
4. Clicar **➕ Pipeline** para iniciar captação

### Fluxo B — Por Médico
1. Aba **👨‍⚕️ Buscar Médico** → digitar nome ou filtrar por especialidade
2. Ver todos os vínculos (hospitais + clínicas onde atua)
3. Adicionar ao **📋 Pipeline** com telefone para WhatsApp

---

## 📊 Fontes dos Dados

| Dado | Fonte | Atualização |
|------|-------|-------------|
| Médicos, especialidades, vínculos | DATASUS/CNES — Portal de Dados Abertos | Mensal |
| Nome, endereço, serviços dos hospitais | DATASUS/CNES — Portal de Dados Abertos | Mensal |
| Alta complexidade (habilitações) | DATASUS/CNES — `rlEstabServClass*.csv` | Mensal |
| CRM, situação do registro | Portal CFM — inserção manual | Por demanda |
| Contato (telefone) | Busca manual externa | Por demanda |

> O sistema sempre exibe a **data de atualização** e a **competência** (mês/ano) dos dados na tela.

---

## 🔑 CFM — Como obter o CRM

1. No pipeline, clique **✏️ Gerenciar** no médico
2. Aba **CRM / CFM** → clique em "Abrir Portal CFM"
3. Busque pelo nome no [portal.cfm.org.br](https://portal.cfm.org.br/busca-medicos/)
4. Anote o CRM e a situação de volta no sistema

---

## 🌐 Deploy Online (acesso para toda a equipe)

### Opção recomendada: VPS + Cloudflare Proxy

1. Instalar em um servidor (Oracle Cloud Free Tier ou similar)
2. Rodar: `python -m uvicorn server:app --host 0.0.0.0 --port 8000`
3. No Cloudflare: apontar DNS para o IP do VPS com proxy habilitado
4. Todos os membros acessam via URL com SSL automático

---

## 👥 Multi-usuários

1. Cada membro cria seu usuário pela interface (Configurações)
2. Todos acessam a **mesma base de médicos** (CNES)
3. Cada um gerencia seus **próprios alvos** no pipeline (campo "Responsável")
4. Filtro por responsável na aba Pipeline

---

## 📅 Manutenção Mensal

Execute no início de cada mês via interface (badge no cabeçalho → "Forçar Atualização")  
ou via terminal:
```bash
python scripts/atualizar_cache.py
```

---

## 📁 Estrutura de Arquivos

```
COLIH_Captacao/
├── .gitignore
├── iniciar.bat                 ← Iniciar no Windows (duplo-clique)
├── README.md
├── frontend/
│   ├── index.html              ← Interface web (SPA)
│   ├── style.css               ← Design premium
│   └── app.js                  ← Lógica JavaScript
├── backend/
│   ├── server.py               ← API FastAPI
│   ├── requirements.txt        ← Dependências Python
│   ├── bairros_distritos.json  ← Mapeamento distritos Salvador
│   └── data/
│       ├── sync_status.json    ← Status da última sync (gerado)
│       ├── pipeline.json       ← Pipeline de captação
│       ├── usuarios.json       ← Usuários cadastrados
│       └── hlc9_dict.json      ← Dicionário HLC-9
└── scripts/
    └── atualizar_cache.py      ← Motor de sync com DATASUS
```

> ⚠️ **Nota:** `medicos_cache.json` e `estab_cache.json` são gerados localmente pelo script de sync e estão no `.gitignore` (são grandes demais para o Git).
