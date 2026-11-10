#!/usr/bin/env python3
"""发布前脱敏扫描。

用法：
  python3 scripts/leak-scan.py               扫工作区里被 git 跟踪或待跟踪的全部文件
  python3 scripts/leak-scan.py --staged      只扫暂存区内容（pre-commit 用）
  python3 scripts/leak-scan.py --message F   扫一份提交说明（commit-msg 用）
  python3 scripts/leak-scan.py --self-test   用自造的正例、反例验证扫描器本身

两类检查：
  ① 通用模式：IPv4、私钥头、疑似密钥赋值、Bearer 令牌、sk- 密钥、JWT、长十六进制串、邮箱。
     命中的片段逐个对白名单（整串相等），不按整行放过。
  ② 本机拒绝词表 .leak-denylist（不入库）：每行一个正则，不区分大小写。
     词表里有一行写错，整次扫描判红；没有词表也判红，除非设了 LEAK_SCAN_ALLOW_NO_DENYLIST=1（CI 用）。
另有一条：站点域名（SITE_DOMAIN）只允许出现在 chapters/00-*.md，提交说明里也不允许。
读不到的文件一律判红。任何意外错误都判红，不静默放行。
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DENYLIST = os.path.join(ROOT, '.leak-denylist')
SITE_DOMAIN = re.compile(r'fupanbao\.top', re.I)
SITE_DOMAIN_ALLOWED = re.compile(r'^chapters/00-[^/]*\.md$')

GENERIC = [
    ('IPv4', re.compile(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])')),
    ('私钥', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
    ('密钥赋值', re.compile(r'(?:token|secret|password|passwd|api[_-]?key)\s*[=:]\s*["\']?[A-Za-z0-9_./+-]{12,}', re.I)),
    ('Bearer', re.compile(r'Bearer\s+[A-Za-z0-9._~+/=-]{16,}', re.I)),
    ('sk-密钥', re.compile(r'\bsk-[A-Za-z0-9_-]{16,}')),
    ('JWT', re.compile(r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}')),
    ('长十六进制串', re.compile(r'\b[0-9a-fA-F]{32,}\b')),
    ('邮箱', re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')),
]
ALLOW_EXACT = {'IPv4': {'127.0.0.1', '0.0.0.0'}}
ALLOW_EMAIL = re.compile(r'@(?:example\.(?:com|org|net)|[a-z0-9.-]+\.invalid|users\.noreply\.github\.com)$', re.I)


def load_denylist():
    if not os.path.exists(DENYLIST):
        if os.environ.get('LEAK_SCAN_ALLOW_NO_DENYLIST') == '1':
            print('⚠️ 没有 .leak-denylist，按 LEAK_SCAN_ALLOW_NO_DENYLIST=1 只跑通用模式', file=sys.stderr)
            return []
        sys.exit('❌ 本机没有 .leak-denylist：拒绝词表缺失时一律判红（CI 才设 LEAK_SCAN_ALLOW_NO_DENYLIST=1）')
    pats = []
    with open(DENYLIST, encoding='utf-8') as fh:
        for n, line in enumerate(fh, 1):
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            try:
                pats.append(re.compile(s, re.I))
            except re.error as e:
                sys.exit(f'❌ .leak-denylist 第 {n} 行不是合法正则（{e}），整次扫描判红')
    return pats


def scan_text(name, text, deny, allow_site_domain):
    hits = []
    for ln, line in enumerate(text.splitlines(), 1):
        for label, rx in GENERIC:
            for m in rx.finditer(line):
                frag = m.group(0)
                if frag in ALLOW_EXACT.get(label, ()):
                    continue
                if label == '邮箱' and ALLOW_EMAIL.search(frag):
                    continue
                if label == '长十六进制串' and set(frag) == {'0'}:   # git 的全零空提交号
                    continue
                hits.append(f'{name}:{ln}: [{label}] {frag}')
        for rx in deny:
            for m in rx.finditer(line):
                hits.append(f'{name}:{ln}: [拒绝词] {m.group(0)}')
        if not allow_site_domain:
            for m in SITE_DOMAIN.finditer(line):
                hits.append(f'{name}:{ln}: [站点域名只许出现在第 0 章] {m.group(0)}')
    return hits


def git(*args):
    return subprocess.run(['git', '-c', 'core.quotepath=false', *args], cwd=ROOT,
                          capture_output=True, check=True).stdout


def list_files(staged):
    if staged:
        out = git('diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z')
    else:
        out = git('ls-files', '-co', '--exclude-standard', '-z')
    return [p for p in out.decode('utf-8').split('\0') if p]


def read_file(path, staged):
    if staged:
        return git('show', ':' + path).decode('utf-8', errors='replace')
    with open(os.path.join(ROOT, path), 'rb') as fh:
        return fh.read().decode('utf-8', errors='replace')


def run(mode, arg=None):
    deny = load_denylist()
    hits = []
    if mode == 'message':
        with open(arg, encoding='utf-8', errors='replace') as fh:
            text = ''.join(l for l in fh if not l.startswith('#'))
        hits = scan_text('提交说明', text, deny, allow_site_domain=False)
    else:
        staged = mode == 'staged'
        for p in list_files(staged):
            if p == '.leak-denylist':
                continue
            try:
                text = read_file(p, staged)
            except Exception as e:  # 读不到就判红，不许静默跳过
                hits.append(f'{p}: 读不到文件内容（{e}）')
                continue
            hits += scan_text(p, text, deny, allow_site_domain=bool(SITE_DOMAIN_ALLOWED.match(p)))
    if hits:
        print('\n'.join(hits))
        print('❌ 脱敏扫描不通过（每行：位置: [类别] 命中片段）', file=sys.stderr)
        return 1
    print('✅ 脱敏扫描通过')
    return 0


def self_test():
    deny = [re.compile('SecretName', re.I)]
    # 样例在运行时拼出来，免得扫描器扫自己时命中这些字面量
    j = ''.join
    bad = {
        'IP 与回环同一行': j(['ip 10.1.', '2.3 and 127.0.0.1']),
        '子串含 0.0.0.0': j(['net 10.0.', '0.0/8']),
        '拒绝词小写': 'see secretname here',
        'Bearer': j(['Authorization: Bear', 'er abcdefghijklmnop1234']),
        'sk 密钥': j(['key s', 'k-ant-abcdefghijklmnop12']),
        'JWT': j(['ey', 'JhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NSJ9.x']),
        '裸 40 位十六进制': 'a' * 8 + '0123456789abcdef' * 2,
        '邮箱': j(['mail me at someone', '@', 'qq.com']),
        '站点域名': j(['visit fupan', 'bao.top now']),
    }
    good = {
        '回环地址': 'bind 127.0.0.1 only',
        '示例邮箱': 'user@example.com',
        'noreply': '1+me@users.noreply.github.com',
        '普通中文': '这是一段没有任何敏感信息的正文。',
    }
    fails = []
    for k, v in bad.items():
        if not scan_text('t', v, deny, allow_site_domain=False):
            fails.append(f'应拦未拦：{k}')
    for k, v in good.items():
        if scan_text('t', v, deny, allow_site_domain=False):
            fails.append(f'误拦：{k}')
    if scan_text('t', bad['站点域名'], deny, allow_site_domain=True):
        fails.append('第 0 章的站点域名被误拦')
    # 词表写坏必须判红
    global DENYLIST
    saved = DENYLIST
    with tempfile.TemporaryDirectory() as d:
        DENYLIST = os.path.join(d, 'deny')
        with open(DENYLIST, 'w', encoding='utf-8') as fh:
            fh.write('ok\nfoo(\n')
        try:
            load_denylist()
            fails.append('词表写坏未判红')
        except SystemExit:
            pass
        os.remove(DENYLIST)
        env = os.environ.pop('LEAK_SCAN_ALLOW_NO_DENYLIST', None)
        try:
            load_denylist()
            fails.append('缺词表未判红')
        except SystemExit:
            pass
        finally:
            if env is not None:
                os.environ['LEAK_SCAN_ALLOW_NO_DENYLIST'] = env
    DENYLIST = saved
    total = len(bad) + len(good) + 3
    if fails:
        print('\n'.join(fails))
        print(f'❌ 自测 {total - len(fails)}/{total}', file=sys.stderr)
        return 1
    print(f'✅ 自测 {total}/{total}')
    return 0


def main():
    a = sys.argv[1:]
    try:
        if a[:1] == ['--self-test']:
            return self_test()
        if a[:1] == ['--staged']:
            return run('staged')
        if a[:1] == ['--message'] and len(a) == 2:
            return run('message', a[1])
        if not a:
            return run('worktree')
        print(__doc__)
        return 2
    except SystemExit:
        raise
    except Exception as e:  # 扫描器自身出错也判红
        print(f'❌ 扫描器出错，按不通过处理：{e!r}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
