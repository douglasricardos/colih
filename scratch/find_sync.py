with open('backend/server.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if '/sync' in line or 'def sync' in line.lower() or 'colih' in line.lower():
            if '@app' in line or 'def ' in line:
                print(f'Line {i+1}: {line.strip()}')
