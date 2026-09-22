#!/usr/bin/env bash
# veFaaS Native Python 运行时启动入口：FastAPI + uvicorn
# 监听地址必须为 0.0.0.0，端口从 _FAAS_RUNTIME_PORT 读取（默认 8000）
set -euo pipefail

HOST="0.0.0.0"
PORT="${_FAAS_RUNTIME_PORT:-8000}"

exec python3 -m uvicorn app.main:app --host "$HOST" --port "$PORT"
