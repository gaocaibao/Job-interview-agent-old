#!/usr/bin/env bash
# veFaaS Native Node.js 20 运行时启动入口：Next.js standalone 服务
# 监听地址必须为 0.0.0.0，端口从 _FAAS_RUNTIME_PORT 读取（默认 8000）
set -euo pipefail

# veFaaS 要求监听 0.0.0.0（HOSTNAME 强制覆盖，避免继承容器主机名导致仅本机可访问）
export HOSTNAME="0.0.0.0"
export PORT="${_FAAS_RUNTIME_PORT:-8000}"

exec node server.js
