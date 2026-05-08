## ADDED Requirements

### Requirement: 多时间窗口可用性计算
系统 SHALL 提供 3分钟/30分钟/3小时/6小时/12小时/24小时 六个时间窗口的可用性统计。

#### Scenario: 3分钟窗口计算
- **WHEN** 用户请求3分钟可用性
- **THEN** 系统 SHALL 计算最近3分钟内所有测试的成功率

#### Scenario: 30分钟窗口计算
- **WHEN** 用户请求30分钟可用性
- **THEN** 系统 SHALL 计算最近30分钟内所有测试的成功率

#### Scenario: 3小时窗口计算
- **WHEN** 用户请求3小时可用性
- **THEN** 系统 SHALL 计算最近3小时内所有测试的成功率

#### Scenario: 6小时窗口计算
- **WHEN** 用户请求6小时可用性
- **THEN** 系统 SHALL 计算最近6小时内所有测试的成功率

#### Scenario: 12小时窗口计算
- **WHEN** 用户请求12小时可用性
- **THEN** 系统 SHALL 计算最近12小时内所有测试的成功率

#### Scenario: 24小时窗口计算
- **WHEN** 用户请求24小时可用性
- **THEN** 系统 SHALL 计算最近24小时内所有测试的成功率

### Requirement: 实时状态展示
系统 SHALL 在看板上实时展示当前 API 的可用状态。

#### Scenario: 当前在线状态
- **WHEN** 最近一次测试成功
- **THEN** 看板 SHALL 显示"在线"状态，状态指示灯为绿色

#### Scenario: 当前离线状态
- **WHEN** 最近一次测试失败
- **THEN** 看板 SHALL 显示"离线"状态，状态指示灯为红色

### Requirement: 历史趋势可视化
系统 SHALL 提供历史数据的可视化图表展示。

#### Scenario: 可用性趋势图
- **WHEN** 用户打开看板
- **THEN** 系统 SHALL 显示过去24小时的可用性折线图

#### Scenario: 延迟趋势图
- **WHEN** 用户打开看板
- **THEN** 系统 SHALL 显示过去24小时的响应延迟折线图

### Requirement: 看板数据刷新
系统 SHALL 自动刷新看板数据。

#### Scenario: 自动刷新
- **WHEN** 看板页面处于打开状态
- **THEN** 系统 SHALL 每30秒自动刷新一次数据
