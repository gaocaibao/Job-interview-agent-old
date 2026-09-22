import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 独立部署模式：构建产物自带精简 node_modules，适配 veFaaS 等 Serverless 平台
  output: "standalone",
};

export default nextConfig;
