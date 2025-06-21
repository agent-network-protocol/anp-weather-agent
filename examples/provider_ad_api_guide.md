# 按提供商分离的 Agent Description API 指南

## 概述

重构后的系统现在支持按服务提供商分离的 Agent Description (ad.json) 接口，使得不同的服务提供商可以有独立的代理描述文件。

## API 接口

### 1. 获取所有可用提供商列表

**接口:** `GET /mcp/agents/providers`

**描述:** 获取系统中所有可用的服务提供商及其统计信息

**响应示例:**
```json
{
  "total_providers": 1,
  "providers": [
    {
      "name": "amap",
      "tools_count": 15,
      "resources_count": 0,
      "tools": [
        {
          "name": "maps_direction_bicycling",
          "description": "骑行路径规划用于规划骑行通勤方案..."
        }
      ],
      "ad_url": "http://localhost:9870/mcp/agents/amap/ad.json"
    }
  ]
}
```

### 2. 获取特定提供商的 Agent Description

**接口:** `GET /mcp/agents/{provider}/ad.json`

**参数:**
- `provider`: 服务提供商名称（如 `amap`, `kuaidi100` 等）

**描述:** 获取指定服务提供商的 Agent Description，只包含该提供商的工具和资源

**响应示例:**
```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "did": "https://w3id.org/did#",
    "ad": "https://agent-network-protocol.com/ad#"
  },
  "@type": "ad:AgentDescription",
  "@id": "http://localhost:9870/mcp/agents/amap/ad.json",
  "name": "Weather Agent MCP - AMAP",
  "provider": "amap",
  "description": "Weather agent providing weather information lookup services via AMAP MCP protocol. Specialized for amap services.",
  "version": "1.0.0",
  "ad:interfaces": [
    {
      "@type": "ad:StructuredInterface",
      "protocol": {
        "name": "JSON-RPC",
        "version": "2.0",
        "transport": "HTTP",
        "HTTP Method": "POST"
      },
      "schema": {
        "method": "maps_direction_bicycling",
        "description": "骑行路径规划...",
        "params": { /* 工具参数模式 */ }
      },
      "url": "http://localhost:9870/mcp/tools/amap"
    }
  ],
  "ad:resources": []
}
```

### 3. 获取所有提供商汇总的 Agent Description（兼容性接口）

**接口:** `GET /mcp/agents/weather/ad.json`

**描述:** 返回包含所有服务提供商工具和资源的汇总 Agent Description，保持向后兼容

**响应:** 包含所有提供商的工具和资源的完整 ad.json

## 错误处理

### 提供商不存在
当请求不存在的提供商时，返回 404 错误：

```json
{
  "detail": "Provider 'nonexistent' not found. Available providers: ['amap']"
}
```

## 使用场景

### 1. 发现可用提供商
```bash
curl http://localhost:9870/mcp/agents/providers
```

### 2. 获取特定提供商信息
```bash
curl http://localhost:9870/mcp/agents/amap/ad.json
```

### 3. 客户端集成
客户端可以：
1. 首先调用 `/mcp/agents/providers` 获取可用提供商列表
2. 根据需要选择特定提供商
3. 调用 `/mcp/agents/{provider}/ad.json` 获取该提供商的详细信息
4. 使用对应的工具接口 `/mcp/tools/{provider}` 调用工具

## 扩展新提供商

添加新的服务提供商后，系统会自动：
1. 在 `/mcp/agents/providers` 接口中显示新提供商
2. 为新提供商生成独立的 ad.json 接口
3. 支持通过 `/mcp/agents/{new_provider}/ad.json` 访问

示例：添加 kuaidi100 提供商后
- 可通过 `/mcp/agents/kuaidi100/ad.json` 访问
- 在 `/mcp/agents/providers` 中会显示 kuaidi100 相关信息

## 优势

1. **模块化**: 每个提供商有独立的 ad.json，便于管理和维护
2. **可扩展性**: 新增提供商时不影响现有接口
3. **向后兼容**: 保留原有的汇总接口
4. **清晰性**: 客户端可以明确知道每个提供商提供的具体服务
5. **灵活性**: 支持按需获取特定提供商的信息，减少不必要的数据传输

## 测试

运行测试脚本验证接口功能：
```bash
poetry run python examples/test_provider_ad.py
```
