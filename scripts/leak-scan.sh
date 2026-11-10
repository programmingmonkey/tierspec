#!/bin/bash
# 发布前脱敏扫描。用法：bash scripts/leak-scan.sh [--staged]
#   默认扫工作区里所有被 git 跟踪或待跟踪的文件；--staged 只扫暂存区内容（pre-commit 用）。
# 两类检查：
#   ① 通用模式：IPv4、私钥头、疑似密钥赋值、邮箱。
#   ② 本机拒绝词表 .leak-denylist（不入库）：项目专属的 IP、域名、内部名。
# 读不到的文件一律判红。
# 例外：站点域名 fupanbao.top 只允许出现在 chapters/00-*.md。
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
MODE="${1:-}"
if [ "$MODE" = "--staged" ]; then
  FILES=$(git -c core.quotepath=false diff --cached --name-only --diff-filter=ACMR)
  show() { git show ":$1"; }
else
  FILES=$(git -c core.quotepath=false ls-files -co --exclude-standard)
  show() { cat "$1"; }
fi
GENERIC='\b([0-9]{1,3}\.){3}[0-9]{1,3}\b|-----BEGIN [A-Z ]*PRIVATE KEY-----|(token|secret|password|passwd|api[_-]?key)[[:space:]]*[=:][[:space:]]*["'"'"']?[A-Za-z0-9_./+-]{12,}|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
DENY=""
if [ -f .leak-denylist ]; then
  DENY=$(grep -vE '^\s*(#|$)' .leak-denylist | paste -sd'|' -)
else
  echo "⚠️ 本机没有 .leak-denylist，只跑通用模式" >&2
fi
hits=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$f" in .leak-denylist|scripts/leak-scan.sh) continue;; esac
  # 读不到就判红，不许静默跳过（曾因 git 转义中文文件名，整章被悄悄漏扫）
  if ! show "$f" >/dev/null 2>&1; then echo "$f: 读不到文件内容" ; hits=1; continue; fi
  out=$(show "$f" 2>/dev/null | grep -nEi -- "$GENERIC" | grep -vE '127\.0\.0\.1|0\.0\.0\.0|example\.(com|org)' || true)
  if [ -n "$DENY" ]; then out="$out"$'\n'$(show "$f" 2>/dev/null | grep -nE -- "$DENY" || true); fi
  case "$f" in chapters/00-*) ;; *) out="$out"$'\n'$(show "$f" 2>/dev/null | grep -nE 'fupanbao\.top' || true);; esac
  out=$(printf '%s\n' "$out" | sed '/^$/d')
  if [ -n "$out" ]; then hits=1; printf '%s\n' "$out" | sed "s|^|$f:|"; fi
done <<< "$FILES"
if [ "$hits" -ne 0 ]; then echo "❌ 脱敏扫描不通过（上面每行：文件:行号:内容）" >&2; exit 1; fi
echo "✅ 脱敏扫描通过"
