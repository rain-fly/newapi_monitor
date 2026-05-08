## Why

当前实现仅监控单一模型，无法满足用户查看所有模型列表以及各模型独立状态的需求。实际场景中，用户需要了解 NewAPI 下所有模型的可用性情况，以便选择使用哪个模型或了解各模型的服务质量。

## What Changes

- **BREAKING** 数据库表结构变更：test_records 表增加 model 字段以追踪每个测试对应的模型
- 新增多模型并行监控能力：支持对所有可用模型同时进行可用性测试
- 新增模型列表展示功能：在看板上显示所有模型及其当前状态
- 新增分模型统计功能：每个模型独立计算 3分钟/30分钟/3小时/6小时/12小时/24小时 可用性

## Capabilities

### New Capabilities

- `multi-model-monitor`: 多模型监控能力，包括：
  - 获取并维护模型列表
  - 对每个模型独立发起可用性测试
  - 按模型分组的可用性统计
- `model-list-display`: 模型列表展示能力，包括：
  - 所有模型的实时状态展示
  - 每个模型的独立可用性卡片
  - 模型选择/筛选功能

### Modified Capabilities

- `api-health-monitor`: 现有监控能力需要支持多模型测试，测试记录需要关联模型名称
- `availability-dashboard`: 现有看板需要扩展为支持多模型的视图展示

## Impact

- 数据库：test_records 表增加 model 列（向后兼容，现有数据 model 字段为 NULL）
- API：/api/availability 返回结构需要按模型分组
- 新增 API：/api/models 返回模型列表及各模型状态
- Web 前端：需要支持多模型的 Tab 或下拉切换展示
