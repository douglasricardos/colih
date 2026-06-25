import pathlib

for filepath in ['frontend/app.js', 'frontend/index.html']:
    path = pathlib.Path(filepath)
    if not path.exists(): continue
    text = path.read_text(encoding='utf-8')
    
    fixes = {
        'ðŸ“': '📍',
        'âš': '⚠️',
        'ðŸ“Œ': '📌',
        'ðŸ”Ž': '🔍',
        'ðŸš¨': '🚨',
        'ðŸ’¼': '💼'
    }
    
    for bad, good in fixes.items():
        text = text.replace(bad, good)
        
    path.write_text(text, encoding='utf-8')
    print('Fixed', filepath)
