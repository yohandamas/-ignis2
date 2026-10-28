# v209 빌드 파이프라인: 원본에서 최상위 function 경계로 스크립트를 미리 2개로 나눈 뒤(문장 중간 절단 방지) 압축 → 3분할
import re, sys, subprocess, os
from collections import Counter
src_path, ver, B = sys.argv[1], sys.argv[2], os.path.dirname(os.path.abspath(__file__)) + '/'
src = open(src_path, encoding='utf-8').read()
scripts = [m for m in re.finditer(r'<script>([\s\S]*?)</script>', src)]
main = max(scripts, key=lambda m: len(m.group(1)))
js = main.group(1)
head_end = re.search(r'</style>\s*</head>', src).end()
markup = main.start() - head_end
target = (len(js) - markup) / 2  # body(마크업+앞부분) ≈ footer(뒷부분)
cands = [m.start() + 1 for m in re.finditer(r'\n(?:async )?function [A-Za-z0-9_$]+\s*\(', js)]
sp = min(cands, key=lambda x: abs(x - target))
split_src = src[:main.start(1)] + js[:sp] + '</script>\n<script>' + js[sp:] + src[main.end(1):]
open(B + 'split_src.html', 'w', encoding='utf-8').write(split_src)
subprocess.run(['node', B + 'strip2.js', B + 'split_src.html', B + 'stripped2.html'], check=True)
out = open(B + 'stripped2.html', encoding='utf-8').read()
i = re.search(r'</style>\s*</head>', out).end()
h, rest = out[:i], out[i:]
j = rest.rfind('<script>')
body, foot = rest[:j], rest[j:]
o = '/mnt/user-data/outputs/'
for n, t in (('header', h), ('body', body), ('footer', foot)):
    open(o + f'ignis-{n}-{ver}.html', 'w', encoding='utf-8').write(t)
    print(f'{n:6s} 줄 {t.count(chr(10))+1:4d} | {len(t.encode())//1024}KB | 최장줄 {max(len(l) for l in t.split(chr(10)))}')
full = h + body + foot
jsall = '\n'.join(re.findall(r'<script>([\s\S]*?)</script>', full))
for k, s in enumerate(re.findall(r'<script>([\s\S]*?)</script>', full)): open(B + f'f{k}.js', 'w', encoding='utf-8').write(s)
fd = re.findall(r'(?:^|[;}\n])\s*(?:async )?function ([a-zA-Z0-9_$]+)\s*\(', jsall)
ji = set(re.findall(r"getElementById\(['\"]([a-zA-Z0-9_-]+)['\"]\)", full)); hi = set(re.findall(r'id="([a-zA-Z0-9_-]+)"', full))
print('중복함수:', {k: v for k, v in Counter(fd).items() if v > 1} or '없음', '| Missing IDs:', sorted(ji - hi) or '없음', '| JS내 엔티티:', len(re.findall(r'&(amp|lt|gt|quot);', jsall)))
print('DOCTYPE/끝:', full.lstrip().startswith('<!DOCTYPE html>'), full.rstrip().endswith('</html>'), '| 버전표기:', ('v.' + ver[1:]) in full, '| MEMBERS:', 'const MEMBERS' in full)
dec = lambda x: x.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
os.makedirs(B + 'sim', exist_ok=True)
open(B + 'sim/index.html', 'w', encoding='utf-8').write(h + dec(body) + foot)
