#!/usr/bin/env python3
"""Delete the ⑦ 功能模块展示 section from index.html and repoint nav links."""
import re, io

IDX = 'index.html'

with io.open(IDX, encoding='utf-8') as f:
    lines = f.readlines()

# 1) locate the ⑦ section comment
start = None
for i, ln in enumerate(lines):
    if '⑦ 功能模块展示' in ln:
        start = i
        break
assert start is not None, '⑦ section comment not found'

# 2) find the matching closing </section> after start
end = None
for i in range(start, len(lines)):
    if lines[i].strip() == '</section>':
        end = i
        break
assert end is not None, 'closing </section> not found'

# remove from start .. end inclusive, then drop a single trailing blank line
del lines[start:end+1]
while lines and lines[start:start+1] == ['\n']:
    del lines[start]
    break

text = ''.join(lines)

# 3) renumber CJK section comments ⑧->⑦, ⑨->⑧, ⑩->⑨
text = text.replace('⑧ 客户案例', '⑦ 客户案例')
text = text.replace('⑨ Bottom CTA', '⑧ Bottom CTA')
text = text.replace('⑩ 合作伙伴', '⑨ 合作伙伴')

with io.open(IDX, 'w', encoding='utf-8') as f:
    f.write(text)

print('index.html: ⑦ section removed, comments renumbered.')

# 4) repoint nav #features -> #features-overview across all html pages
import glob
for fp in glob.glob('*.html'):
    with io.open(fp, encoding='utf-8') as f:
        t = f.read()
    if 'index.html#features"' in t or 'href="#features"' in t:
        t2 = t.replace('index.html#features"', 'index.html#features-overview"').replace('href="#features"', 'href="#features-overview"')
        with io.open(fp, 'w', encoding='utf-8') as f:
            f.write(t2)
        print(f'{fp}: nav repointed #features -> #features-overview')
print('done')
