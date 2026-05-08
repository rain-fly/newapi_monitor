## ADDED Requirements

### Requirement: 模型列表展示
系统 SHALL 在看板上展示所有监控的模型及其当前状态。

#### Scenario: 显示所有模型
- **WHEN** 用户打开看板主页
- **THEN** 系统 SHALL 展示所有模型的卡片，每个卡片显示模型名称和在线/离线状态

#### Scenario: 模型状态指示
- **WHEN** 模型的最新测试成功
- **THEN** 该模型卡片 SHALL 显示绿色在线状态

#### Scenario: 模型离线指示
- **WHEN** 模型的最新测试失败
- **THEN** 该模型卡片 SHALL 显示红色离线状态

### Requirement: 分模型可用性统计
系统 SHALL 支持查看单个模型的详细可用性统计。

#### Scenario: 选择模型查看详情
- **WHEN** 用户点击某个模型卡片
- **THEN** 系统 SHALL 显示该模型的 3分钟/30分钟/3小时/6小时/12小时/24小时 可用性

#### Scenario: 分模型趋势图
- **WHEN** 用户选择查看某模型详情
- **THEN** 系统 SHALL 显示该模型过去24小时的可用性和延迟趋势图

### Requirement: 模型列表 API
系统 SHALL 提供 API 返回所有模型及其状态。

#### Scenario: 获取模型列表
- **WHEN** 调用 /api/models 接口
- **THEN** 系统 SHALL 返回所有模型名称及其最新状态

#### Scenario: 获取指定模型统计
- **WHEN** 调用 /api/models/<model_name>/availability 接口
- **THEN** 系统 SHALL 返回该模型的各时间窗口可用性统计
