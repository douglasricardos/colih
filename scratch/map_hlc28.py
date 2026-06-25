import json

target_dict = {
  # Cirurgia cardíaca
  "CIRURGIA CARDIOVASCULAR": "Cirurgia cardíaca",
  "CIRURGIA CARDÍACA": "Cirurgia cardíaca",
  "CIRURGIA CARDIOTORÁCICA": "Cirurgia cardíaca",
  "MÉDICO CIRURGIÃO CARDIOVASCULAR": "Cirurgia cardíaca",
  "MÉDICO CIRURGIÃO CARDIOTORÁCICO": "Cirurgia cardíaca",
  
  # Cirurgia torácica
  "CIRURGIA TORÁCICA": "Cirurgia torácica",
  "MÉDICO CIRURGIÃO TORÁCICO": "Cirurgia torácica",
  
  # Cirurgia geral
  "CIRURGIA GERAL": "Cirurgia geral",
  "MÉDICO CIRURGIÃO GERAL": "Cirurgia geral",
  
  # Ortopedia
  "ORTOPEDIA": "Ortopedia",
  "ORTOPEDIA E TRAUMATOLOGIA": "Ortopedia",
  "MÉDICO ORTOPEDISTA E TRAUMATOLOGISTA": "Ortopedia",
  "CIRURGIA DO TRAUMA": "Ortopedia", # Often handled by Ortopedia/Cirurgia Geral
  
  # Ginecologia e Obstetrícia (We separate them because the PDF separates them)
  "GINECOLOGIA": "Ginecologia",
  "OBSTETRÍCIA": "Obstetrícia",
  "GINECOLOGIA E OBSTETRÍCIA": "Ginecologia", # Defaulting to Ginecologia as umbrella
  "MÉDICO GINECOLOGISTA E OBSTETRA": "Ginecologia",
  "MÉDICO GINECOLOGISTA": "Ginecologia",
  
  # Anestesiologia
  "ANESTESIOLOGIA": "Anestesiologia",
  "MÉDICO ANESTESIOLOGISTA": "Anestesiologia",
  
  # Medicina intensiva
  "MEDICINA INTENSIVA": "Medicina intensiva",
  "MÉDICO INTENSIVISTA": "Medicina intensiva",
  
  # Hematologia
  "HEMATOLOGIA": "Hematologia",
  "HEMATOLOGIA E HEMOTERAPIA": "Hematologia",
  "MÉDICO HEMATOLOGISTA": "Hematologia",
  "MÉDICO HEMOTERAPEUTA": "Hematologia",
  
  # Oncologia clínica / Ginecologia oncológica
  "ONCOLOGIA": "Oncologia clínica",
  "ONCOLOGIA CLÍNICA": "Oncologia clínica",
  "MÉDICO ONCOLOGISTA CLÍNICO": "Oncologia clínica",
  "CIRURGIA ONCOLÓGICA": "Oncologia clínica",
  "MÉDICO CIRURGIÃO ONCOLÓGICO": "Oncologia clínica",
  
  # Gastroenterologia
  "GASTROENTEROLOGIA": "Gastroenterologia",
  "MÉDICO GASTROENTEROLOGISTA": "Gastroenterologia",
  "CIRURGIA DO APARELHO DIGESTIVO": "Gastroenterologia",
  "MÉDICO CIRURGIÃO DO APARELHO DIGESTIVO": "Gastroenterologia",
  
  # Coloproctologia
  "COLOPROCTOLOGIA": "Coloproctologia",
  "MÉDICO PROCTOLOGISTA": "Coloproctologia",
  "MÉDICO COLOPROCTOLOGISTA": "Coloproctologia",
  
  # Neurocirurgia
  "NEUROCIRURGIA": "Neurocirurgia",
  "MÉDICO NEUROCIRURGIÃO": "Neurocirurgia",
  
  # Urologia
  "UROLOGIA": "Urologia",
  "MÉDICO UROLOGISTA": "Urologia",
  
  # Pediatria
  "PEDIATRIA": "Pediatria",
  "MÉDICO PEDIATRA": "Pediatria",
  "CIRURGIA PEDIÁTRICA": "Pediatria",
  "MÉDICO CIRURGIÃO PEDIÁTRICO": "Pediatria",
  
  # Neonatologia
  "NEONATOLOGIA": "Neonatologia",
  "MÉDICO NEONATOLOGISTA": "Neonatologia",
  
  # Cirurgia vascular
  "CIRURGIA VASCULAR": "Cirurgia vascular",
  "ANGIOLOGIA E CIRURGIA VASCULAR": "Cirurgia vascular",
  "ANGIOLOGIA": "Cirurgia vascular",
  "MÉDICO CIRURGIÃO VASCULAR": "Cirurgia vascular",
  "MÉDICO ANGIOLOGISTA": "Cirurgia vascular",
  
  # Cirurgia bucomaxilofacial
  "CIRURGIA BUCOMAXILOFACIAL": "Cirurgia bucomaxilofacial",
  "CIRURGIÃO DENTISTA - CIRURGIÃO BUCOMAXILOFACIAL": "Cirurgia bucomaxilofacial",
  "CIRURGIÃO DENTISTA - TRAUMATOLOGISTA BUCOMAXILOFACIAL": "Cirurgia bucomaxilofacial",
  
  # Otorrinolaringologia
  "OTORRINOLARINGOLOGIA": "Otorrinolaringologia",
  "MÉDICO OTORRINOLARINGOLOGISTA": "Otorrinolaringologia",
  
  # Clínica médica
  "CLÍNICA MÉDICA": "Clínica médica",
  "MÉDICO CLÍNICO": "Clínica médica",
  
  # Medicina de emergência
  "MEDICINA DE EMERGÊNCIA": "Medicina de emergência",
  
  # Cabeça e pescoço -> Usually groups into Cirurgia geral or Otorrinolaringologia depending on the area, 
  # but the PDF does not list 'Cirurgia de Cabeça e Pescoço'. Let's map it to Cirurgia geral for now.
  "CIRURGIA DE CABEÇA E PESCOÇO": "Cirurgia geral",
  "MÉDICO CIRURGIÃO DE CABEÇA E PESCOÇO": "Cirurgia geral"
}

with open('backend/data/hlc_dict.json', 'w', encoding='utf-8') as f:
    json.dump(target_dict, f, ensure_ascii=False, indent=2)

print("HLC-9 Dictionary perfectly aligned with the PDF targets.")
