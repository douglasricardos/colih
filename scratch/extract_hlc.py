import pdfplumber
import re

pdf_path = r'C:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Salvador\hlc-9_s-Ba_T.pdf'
specialties = []

try:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Find fully uppercase lines that look like headers
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    # Check if line is mostly uppercase and doesn't have too many lowercase letters
                    # Usually specialties are like "ANESTESIOLOGIA", "CIRURGIA CARDIOVASCULAR"
                    if len(line) > 3 and line.isupper() and not line.startswith('(') and not re.search(r'\d', line):
                        specialties.append(line)
    
    # Clean up duplicates and common non-specialty words
    clean = []
    for s in specialties:
        s = s.replace('', '') # Remove bad chars if any
        if s not in clean and s not in ['COMISSO DE LIGAO COM HOSPITAIS', 'NDICE', 'INTRODUO']:
            clean.append(s)
            
    print("Found Specialties:")
    for s in clean:
        print(" -", s)
except Exception as e:
    print("Error:", e)
