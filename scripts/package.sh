#!/usr/bin/env bash
# 部署包打包脚本：按 veFaaS 运行时规范生成后端/前端 zip 包
# 用法：
#   scripts/package.sh backend                                  # 仅打包后端
#   NEXT_PUBLIC_API_BASE_URL=https://xxx scripts/package.sh frontend  # 仅打包前端
# 产物输出到 dist/ 目录
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
# veFaaS Native Python 运行时提供 3.8-3.12，本地打包需用同代解释器保证 wheel 兼容
PYTHON_BIN="${PYTHON_BIN:-python3.12}"

package_backend() {
  local staging="$DIST_DIR/backend-pkg"
  rm -rf "$staging"
  mkdir -p "$staging"

  # 用 3.12 venv 安装依赖到打包目录（manylinux wheel 兼容运行时的 Debian 11）
  "$PYTHON_BIN" -m venv "$staging/.venv-build"
  "$staging/.venv-build/bin/pip" install --quiet --disable-pip-version-check \
    -r "$ROOT_DIR/backend/requirements.txt" --target "$staging"
  rm -rf "$staging/.venv-build"

  # 应用代码与启动脚本置于 zip 根目录（run.sh 以 app.main:app 为入口）
  cp -r "$ROOT_DIR/backend/app" "$staging/app"
  cp "$ROOT_DIR/backend/run.sh" "$ROOT_DIR/backend/requirements.txt" "$staging/"

  (cd "$staging" && zip -FSrq "$DIST_DIR/backend.zip" .)
  echo "后端部署包：$DIST_DIR/backend.zip"
}

package_frontend() {
  local staging="$DIST_DIR/frontend-pkg"
  rm -rf "$staging"
  mkdir -p "$staging"

  # NEXT_PUBLIC_* 变量在构建期内联进客户端产物，必须显式指定线上后端地址
  : "${NEXT_PUBLIC_API_BASE_URL:?请先设置 NEXT_PUBLIC_API_BASE_URL 为线上后端域名}"

  (cd "$ROOT_DIR/frontend" && npm ci --quiet)
  (cd "$ROOT_DIR/frontend" && NEXT_PUBLIC_API_BASE_URL="$NEXT_PUBLIC_API_BASE_URL" npm run build)

  local standalone="$ROOT_DIR/frontend/.next/standalone"
  cp -r "$standalone/." "$staging/"

  # standalone 产物不含静态资源与 public 目录，需手动补齐
  mkdir -p "$staging/.next"
  cp -r "$ROOT_DIR/frontend/.next/static" "$staging/.next/static"
  if [ -d "$ROOT_DIR/frontend/public" ]; then
    cp -r "$ROOT_DIR/frontend/public" "$staging/public"
  fi
  cp "$ROOT_DIR/frontend/run.sh" "$staging/run.sh"

  (cd "$staging" && zip -FSrq "$DIST_DIR/frontend.zip" .)
  echo "前端部署包：$DIST_DIR/frontend.zip"
}

case "${1:-}" in
  backend) package_backend ;;
  frontend) package_frontend ;;
  *)
    echo "用法：$0 backend|frontend" >&2
    exit 1
    ;;
esac
