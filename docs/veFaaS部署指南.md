# veFaaS 部署指南

本项目前后端分离，分别部署为火山引擎 veFaaS 上的两个 **Web 应用函数**：

| 函数 | 运行时 | 启动命令 | 监听端口 |
| --- | --- | --- | --- |
| 后端（FastAPI） | Native Python 3.12 | `./run.sh` | 8000 |
| 前端（Next.js standalone） | Native Node.js 20 | `./run.sh` | 8000 |

两个函数的 `run.sh` 均从 `$_FAAS_RUNTIME_PORT` 读取端口（默认 8000）并强制监听 `0.0.0.0`，符合平台规范。

## 一、前置条件

- 火山引擎账号及 AK/SK（需 veFaaS 相关权限）
- 本地环境：Node.js 20+、Python 3.12（打包依赖用，保证 wheel 与运行时兼容）、`zip`
- 至少一个可用的大模型 API Key（DeepSeek / StepFun / 豆包任选，未配置时后端以启发式评分兜底，可正常演示）

## 二、打包部署包

在仓库根目录执行（产物输出到 `dist/`）：

```bash
# 后端：按 Python 3.12 安装依赖并打包（约 13MB）
scripts/package.sh backend

# 前端：先设置线上后端域名，再打包（约 24MB）
NEXT_PUBLIC_API_BASE_URL=https://<后端域名> scripts/package.sh frontend
```

注意：

- `NEXT_PUBLIC_API_BASE_URL` 会在**构建期**内联进前端产物，修改后必须重新打包；
- 因此部署顺序为**先后端、后前端**：后端创建成功获得域名后，再打包前端。

## 三、部署后端（控制台）

1. 登录 [veFaaS 控制台](https://console.volcengine.com/vefaas)，创建函数：
   - 类型：**Web 应用函数**，部署方式：**本地上传 Zip 包**
   - 运行时：**Native Python 3.12**
2. 上传 `dist/backend.zip`，启动命令填 `./run.sh`，监听端口填 `8000`。
   - 若启动日志提示 permission denied，将启动命令改为 `bash run.sh`。
3. 建议规格：内存 1024MB、CPU 500m；最小实例数 1 可避免冷启动延迟（赛事演示建议）。
4. 配置环境变量（见下方清单），发布。
5. 验证：访问 `https://<后端域名>/api/v1/health`，应返回 `{"status":"ok",...}`；`/docs` 可查看接口文档。

## 四、部署前端（控制台）

1. 创建函数：类型 **Web 应用函数** + 本地上传 Zip 包，运行时 **Native Node.js 20**。
2. 上传 `dist/frontend.zip`，启动命令 `./run.sh`，监听端口 `8000`，建议内存 1024MB。
3. 发布后访问前端域名，首页应正常渲染。

## 五、环境变量清单

### 后端（veFaaS 控制台 → 环境变量注入，勿提交 git）

| 变量 | 说明 | 示例 |
| --- | --- | --- |
| `APP_ENV` | 运行环境 | `production` |
| `DEBUG` | 调试开关 | `false` |
| `CORS_ORIGINS` | 允许的前端域名，逗号分隔 | `https://<前端域名>` |
| `LLM_DEFAULT_PROVIDER` | 默认模型厂商 | `deepseek` |
| `DEEPSEEK_API_KEY` | DeepSeek Key | `sk-xxx` |
| `STEPFUN_API_KEY` | StepFun Key | （可选） |
| `DOUBAO_API_KEY` | 豆包 Key | （可选） |
| `LLM_FALLBACK_CHAIN` | 有序降级链 | `stepfun,deepseek,doubao` |

Base URL 与模型名已有默认值，一般无需配置。**前端域名确定后，需把 `CORS_ORIGINS` 更新为前端域名并重新发布后端。**

### 前端

| 变量 | 说明 |
| --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | 后端线上地址，打包前设置（控制台无需配置） |

## 六、CLI 方式（可选）

安装并登录 CLI 后，也可用命令行部署（需 AK/SK）：

```bash
npm i -g @volcengine/vefaas-cli
vefaas login                      # 或通过环境变量提供 AK/SK
cd backend && vefaas deploy --newApp miansyun-backend --command "./run.sh" --port 8000 --memory 1024 --yes
cd frontend && vefaas deploy --newApp miansyun-frontend --command "./run.sh" --port 8000 --memory 1024 --yes
vefaas env set --app miansyun-backend CORS_ORIGINS=https://<前端域名>
```

## 七、常见问题

- **冷启动慢**：最小实例数设为 1，或接受首次请求数秒延迟。
- **接口 404/跨域报错**：检查后端 `CORS_ORIGINS` 是否包含前端域名；检查前端 `NEXT_PUBLIC_API_BASE_URL` 是否指向正确域名且打包后重新上传。
- **模型调用失败**：查看 `/api/v1/health/llm` 返回的 `available_providers`；未配置任何 Key 时各模块自动走本地启发式逻辑，不影响流程演示。
- **包体积限制**：单次上传不超过 256MB，当前两个包均远低于限制。
