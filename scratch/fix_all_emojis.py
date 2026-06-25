import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Known corruptions in the text body
    fixes = {
        '\u2018\xa8\xe2\u26a0\ufe0f\u2022': '🔍',
        '\u201d': '🔍',
        '\u26a0\ufe0f': '⚠️',
        'ðŸ“ ': '📍',
        'ðŸ“': '📍',
        'âš': '⚠️',
        'ðŸ“Œ': '📌',
        'ðŸ”Ž': '🔍',
        'ðŸš¨': '🚨',
        'ðŸ’¼': '💼'
    }

    # Also make sure the empty icons are sensible
    # We can just manually replace the exact broken ones.
    
    for bad, good in fixes.items():
        text = text.replace(bad, good)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Fixed', filepath)

fix_file('frontend/app.js')
fix_file('frontend/index.html')
