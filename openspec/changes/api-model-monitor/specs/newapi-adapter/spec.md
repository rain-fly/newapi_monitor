## ADDED Requirements

### Requirement: NewAPI 连接配置
系统 SHALL 支持配置 NewAPI 的 API Endpoint 和认证信息。

#### Scenario: 基础配置
- **WHEN** 系统启动时
- **THEN** 系统 SHALL 从配置文件读取 API Endpoint、API Key 等配置信息

### Requirement: API 调用封装
系统 SHALL 封装 NewAPI 的模型查询接口。

#### Scenario: 成功调用
- **WHEN** 系统发起 API 调用请求
- **THEN** 系统 SHALL 发送 HTTP POST 请求到 /chat/completions 端点

#### Scenario: 请求格式
- **WHEN** 系统发起请求
- **THEN** 请求 SHALL 包含 model、messages 等必要参数，messages 内容为最小化测试文本

### Requirement: 错误处理机制
系统 SHALL 妥善处理 API 调用中的各类错误。

#### Scenario: 网络超时
- **WHEN** API 响应时间超过10秒
- **THEN** 系统 SHALL 判定为超时失败，返回错误信息

#### Scenario: HTTP 错误响应
- **WHEN** API 返回非200状态码
- **THEN** 系统 SHALL 记录错误状态码和响应内容

#### Scenario: 重试机制
- **WHEN** 首次 API 调用失败
- **THEN** 系统 SHALL 最多重试3次，每次重试间隔10秒

### Requirement: 响应解析与延迟计算
系统 SHALL 正确解析 API 响应并计算响应延迟。

#### Scenario: 成功响应解析
- **WHEN** API 返回 200 状态码
- **THEN** 系统 SHALL 提取响应内容并计算从发起到收到响应的时间差作为延迟

#### Scenario: 延迟单位
- **WHEN** 系统计算响应延迟
- **THEN** 延迟 SHALL 以毫秒（ms）为单位记录
