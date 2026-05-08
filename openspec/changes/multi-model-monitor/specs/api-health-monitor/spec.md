## MODIFIED Requirements

### Requirement: 定时调度器
系统 SHALL 每3分钟自动触发一次 API 可用性测试任务，对所有模型逐一测试。

#### Scenario: 正常间隔触发
- **WHEN** 距上次测试任务执行已过3分钟
- **THEN** 系统 SHALL 发起新的测试任务，对每个模型逐一测试

#### Scenario: 服务重启后恢复
- **WHEN** 监控服务重启
- **THEN** 系统 SHALL 立即执行一次所有模型的测试，然后按3分钟间隔继续调度

### Requirement: 时间窗口过滤
系统 SHALL 仅在每天 8:00-18:00 时间段内执行测试任务，其他时间不执行。

#### Scenario: 工作时间执行
- **WHEN** 当前时间在 8:00-18:00 之间
- **THEN** 系统 SHALL 正常执行所有模型的测试任务

#### Scenario: 非工作时间跳过
- **WHEN** 当前时间在 18:00-次日8:00 之间
- **THEN** 系统 SHALL 跳过本次测试，继续等待下一个3分钟周期

### Requirement: 最小 Token 测试
系统 SHALL 使用最小输入输出 token 进行模型可用性测试。

#### Scenario: 最小化请求
- **WHEN** 系统发起可用性测试
- **THEN** 系统 SHALL 使用单个字符或单词作为输入，期望获得最短响应

### Requirement: 结果持久化
系统 SHALL 将每次测试结果持久化存储到数据库，并关联模型名称。

#### Scenario: 成功测试记录
- **WHEN** 某模型的 API 调用成功完成
- **THEN** 系统 SHALL 记录时间戳、模型名称、可用状态为 true、响应延迟（毫秒）

#### Scenario: 失败测试记录
- **WHEN** 某模型的 API 调用失败或超时
- **THEN** 系统 SHALL 记录时间戳、模型名称、可用状态为 false、错误信息、延迟（若有）

### Requirement: 数据保留策略
系统 SHALL 自动清理超过30天的历史测试记录。

#### Scenario: 定时清理
- **WHEN** 系统启动时检测到存在超过30天的记录
- **THEN** 系统 SHALL 删除这些过期记录
