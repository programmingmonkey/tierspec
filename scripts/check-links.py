#!/usr/bin/env python3
"""检查仓库里 Markdown 与 HTML 的相对链接能不能打开。

用法：
  python3 scripts/check-links.py            扫被 git 跟踪或待跟踪的全部 .md / .html
  python3 scripts/check-links.py PATH...    只扫指定文件

查两件事：相对路径指向的文件存在；带 #锚点 的 Markdown 链接，目标文件里有对应标题
（按 GitHub 的标题锚点规则生成）。外部链接（http、https、mailto）不查。
代码围栏和行内代码里的内容不算链接。
"""
import os
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_LINK = re.compile(r'!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
HTML_LINK = re.compile(r'\b(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.I)
EXTERNAL = re.compile(r'^(?:[a-z][a-z0-9+.-]*:|//)', re.I)


def strip_code(text):
    text = re.sub(r'^(```|~~~).*?^\1[^\n]*$', '', text, flags=re.M | re.S)
    return re.sub(r'`[^`\n]*`', '', text)


def slug(heading):
    h = re.sub(r'<[^>]+>', '', heading.strip().lower())
    h = re.sub(r'[^\w\- ]', '', h)   # \w 含中文
    return h.replace(' ', '-')


def anchors(path):
    with open(path, encoding='utf-8') as fh:
        text = strip_code(fh.read())
    seen, out = {}, set()
    for m in re.finditer(r'^#{1,6}\s+(.*?)\s*#*\s*$', text, re.M):
        s = slug(m.group(1))
        n = seen.get(s, 0)
        out.add(s if n == 0 else f'{s}-{n}')
        seen[s] = n + 1
    return out


def files():
    out = subprocess.run(['git', '-c', 'core.quotepath=false', 'ls-files', '-co', '--exclude-standard', '-z'],
                         cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')
    return [p for p in out.split('\0') if p.endswith(('.md', '.html'))]


def check(rel):
    path = os.path.join(ROOT, rel)
    with open(path, encoding='utf-8') as fh:
        raw = fh.read()
    if rel.endswith('.md'):
        targets = MD_LINK.findall(strip_code(raw))
    else:
        targets = HTML_LINK.findall(raw)
    bad = []
    for t in targets:
        if EXTERNAL.match(t):
            continue
        target, _, frag = t.partition('#')
        dest = path if not target else os.path.normpath(os.path.join(os.path.dirname(path), unquote(target)))
        if not os.path.exists(dest):
            bad.append(f'{rel}: 目标不存在 {t}')
        elif frag and dest.endswith('.md') and unquote(frag).lower() not in anchors(dest):
            bad.append(f'{rel}: 锚点不存在 {t}')
    return bad, len(targets)


def main():
    paths = sys.argv[1:] or files()
    bad, total = [], 0
    for p in paths:
        b, n = check(os.path.relpath(os.path.abspath(p), ROOT) if sys.argv[1:] else p)
        bad += b
        total += n
    if bad:
        print('\n'.join(bad))
        print(f'❌ {len(bad)} 个链接打不开（共查 {len(paths)} 个文件、{total} 个链接）', file=sys.stderr)
        return 1
    print(f'✅ 链接检查通过（{len(paths)} 个文件、{total} 个链接）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
