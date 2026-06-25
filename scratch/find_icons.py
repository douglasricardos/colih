import re
with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()
    matches = re.findall(r'class="empty-icon">(.*?)</div>', text)
    for m in matches:
        print('Found:', ascii(m))
