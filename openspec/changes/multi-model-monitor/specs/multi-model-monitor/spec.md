## ADDED Requirements

### Requirement: 多模型测试
系统 SHALL 对所有可用模型逐一发起可用性测试。

#### Scenario: 启动时获取模型列表
- **WHEN** 监控服务启动
- **THEN** 系统 SHALL 从 /models 端点获取可用模型列表

#### Scenario: 逐一测试每个模型
- **WHEN** 调度周期触发测试任务
- **THEN** 系统 SHALL 对列表中的每个模型独立发起可用性测试

#### Scenario: 按模型记录测试结果
- **WHEN** 某个模型的测试完成
- **THEN** 系统 SHALL 记录该次测试对应的模型名称

### Requirement: 模型列表维护
系统 SHALL 维护最新的模型列表并在模型不可用时重新获取。

#### Scenario: 模型不可用时刷新列表
- **WHEN** 测试某个模型时返回 model_not_found 错误
- **THEN** 系统 SHALL 重新获取模型列表

#### Scenario: 定时刷新模型列表
- **WHEN** 连续测试失败超过3次
- **THEN** 系统 SHALL 刷新模型列表

### Requirement: 并发控制
系统 SHALL 确保同一时间只有一个模型的测试在进行。

#### Scenario: 测试互斥
- **WHEN** 一个模型的测试正在进行
- **THEN** 系统 SHALL 等待当前测试完成后才开始下一个模型的测试
