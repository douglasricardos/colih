import json
import os

target_dict = {
  # CIRURGIA CARDIOVASCULAR E TORÁCICA
  "CIRURGIA CARDIOVASCULAR": "Cirurgia Cardiovascular",
  "CIRURGIA CARDÍACA": "Cirurgia Cardiovascular",
  "CIRURGIA CARDIOTORÁCICA": "Cirurgia Cardiovascular",
  "MÉDICO CIRURGIÃO CARDIOVASCULAR": "Cirurgia Cardiovascular",
  "MÉDICO CIRURGIÃO CARDIOTORÁCICO": "Cirurgia Cardiovascular",
  "CIRURGIA TORÁCICA": "Cirurgia Torácica",
  "MÉDICO CIRURGIÃO TORÁCICO": "Cirurgia Torácica",
  
  # CIRURGIA GERAL
  "CIRURGIA GERAL": "Cirurgia Geral",
  "MÉDICO CIRURGIÃO GERAL": "Cirurgia Geral",
  
  # ORTOPEDIA E TRAUMATOLOGIA
  "ORTOPEDIA": "Ortopedia",
  "ORTOPEDIA E TRAUMATOLOGIA": "Ortopedia",
  "MÉDICO ORTOPEDISTA E TRAUMATOLOGISTA": "Ortopedia",
  "CIRURGIA DO TRAUMA": "Ortopedia",
  
  # GINECOLOGIA E OBSTETRÍCIA
  "GINECOLOGIA": "Ginecologia e Obstetrícia",
  "OBSTETRÍCIA": "Ginecologia e Obstetrícia",
  "GINECOLOGIA E OBSTETRÍCIA": "Ginecologia e Obstetrícia",
  "MÉDICO GINECOLOGISTA E OBSTETRA": "Ginecologia e Obstetrícia",
  "MÉDICO GINECOLOGISTA": "Ginecologia e Obstetrícia",
  
  # ANESTESIOLOGIA
  "ANESTESIOLOGIA": "Anestesiologia",
  "MÉDICO ANESTESIOLOGISTA": "Anestesiologia",
  
  # MEDICINA INTENSIVA
  "MEDICINA INTENSIVA": "Medicina Intensiva",
  "MÉDICO INTENSIVISTA": "Medicina Intensiva",
  
  # HEMATOLOGIA E ONCOLOGIA
  "HEMATOLOGIA": "Hematologia",
  "HEMATOLOGIA E HEMOTERAPIA": "Hematologia",
  "MÉDICO HEMATOLOGISTA": "Hematologia",
  "MÉDICO HEMOTERAPEUTA": "Hematologia",
  "ONCOLOGIA": "Oncologia",
  "ONCOLOGIA CLÍNICA": "Oncologia",
  "CIRURGIA ONCOLÓGICA": "Cirurgia Oncológica",
  "MÉDICO ONCOLOGISTA CLÍNICO": "Oncologia",
  "MÉDICO CIRURGIÃO ONCOLÓGICO": "Cirurgia Oncológica",
  
  # GASTROENTEROLOGIA E DIGESTIVO
  "GASTROENTEROLOGIA": "Gastroenterologia",
  "MÉDICO GASTROENTEROLOGISTA": "Gastroenterologia",
  "CIRURGIA DO APARELHO DIGESTIVO": "Cirurgia do Aparelho Digestivo",
  "COLOPROCTOLOGIA": "Cirurgia do Aparelho Digestivo",
  "MÉDICO PROCTOLOGISTA": "Cirurgia do Aparelho Digestivo",
  "MÉDICO COLOPROCTOLOGISTA": "Cirurgia do Aparelho Digestivo",
  "MÉDICO CIRURGIÃO DO APARELHO DIGESTIVO": "Cirurgia do Aparelho Digestivo",
  
  # NEUROCIRURGIA
  "NEUROCIRURGIA": "Neurocirurgia",
  "MÉDICO NEUROCIRURGIÃO": "Neurocirurgia",
  
  # UROLOGIA
  "UROLOGIA": "Urologia",
  "MÉDICO UROLOGISTA": "Urologia",
  
  # PEDIATRIA E NEONATOLOGIA
  "PEDIATRIA": "Pediatria",
  "MÉDICO PEDIATRA": "Pediatria",
  "NEONATOLOGIA": "Neonatologia",
  "MÉDICO NEONATOLOGISTA": "Neonatologia",
  "CIRURGIA PEDIÁTRICA": "Cirurgia Pediátrica",
  "MÉDICO CIRURGIÃO PEDIÁTRICO": "Cirurgia Pediátrica",
  
  # CIRURGIA VASCULAR
  "CIRURGIA VASCULAR": "Cirurgia Vascular",
  "ANGIOLOGIA E CIRURGIA VASCULAR": "Cirurgia Vascular",
  "ANGIOLOGIA": "Cirurgia Vascular",
  "MÉDICO CIRURGIÃO VASCULAR": "Cirurgia Vascular",
  "MÉDICO ANGIOLOGISTA": "Cirurgia Vascular",
  
  # CABEÇA, PESCOÇO E BUCOMAXILO
  "CIRURGIA DE CABEÇA E PESCOÇO": "Cirurgia de Cabeça e Pescoço",
  "MÉDICO CIRURGIÃO DE CABEÇA E PESCOÇO": "Cirurgia de Cabeça e Pescoço",
  "CIRURGIA BUCOMAXILOFACIAL": "Cirurgia Bucomaxilofacial",
  "CIRURGIÃO DENTISTA - CIRURGIÃO BUCOMAXILOFACIAL": "Cirurgia Bucomaxilofacial",
  "CIRURGIÃO DENTISTA - TRAUMATOLOGISTA BUCOMAXILOFACIAL": "Cirurgia Bucomaxilofacial",
  "OTORRINOLARINGOLOGIA": "Otorrinolaringologia",
  "MÉDICO OTORRINOLARINGOLOGISTA": "Otorrinolaringologia",
  
  # CLÍNICA MÉDICA
  "CLÍNICA MÉDICA": "Clínica Médica",
  "MÉDICO CLÍNICO": "Clínica Médica",
  "MEDICINA DE EMERGÊNCIA": "Clínica Médica"
}

with open('backend/data/hlc_dict.json', 'w', encoding='utf-8') as f:
    json.dump(target_dict, f, ensure_ascii=False, indent=2)

print("HLC Dictionary Synthesized.")
