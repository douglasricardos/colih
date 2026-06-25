import pandas as pd
from pathlib import Path
import traceback

extract_dir = r"c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\backend\data\dicts"
dicionarios = {}

for p in Path(extract_dir).glob("tb*.csv"):
    if any(x in p.name.lower() for x in ["equipamento", "leito", "comissao", "instalacaofisica", "atendimentoprestado", "servicoespecializado", "classificacaoservico", "naturezajuridica"]):
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
                    else:
                        val_id = str(row.iloc[cols.index(c_id)]).strip().lstrip('0')
                    dicionarios[c_id][val_id] = str(row.iloc[cols.index(c_ds)]).strip()
            print(f"Loaded {c_id}: {len(dicionarios.get(c_id, {}))} items from {p.name}")
        except Exception as e:
            print(f"FAILED ON {p.name}: {e}")
            traceback.print_exc()

print("Leitos tem 7:", dicionarios.get("CO_LEITO", {}).get("7"))
print("Equipamentos tem 1-1:", dicionarios.get("CO_EQUIPAMENTO", {}).get("1-1"))
print("NatJur tem 3999:", dicionarios.get("CO_NATUREZA_JUR", {}).get("3999"))
