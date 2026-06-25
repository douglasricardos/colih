import re
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()
m = re.search(r'<div id="syncStatusModal" class="modal">.*?</div>.*?</div>', text, re.DOTALL)
if m:
    print(m.group(0)[:1500])
