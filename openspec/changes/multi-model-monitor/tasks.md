## 1. 数据库迁移

- [x] 1.1 修改 Database 类，test_records 表增加 model 字段
- [x] 1.2 修改 insert_record 方法，支持 model 参数
- [x] 1.3 修改 get_recent_records 方法，支持 model 过滤
- [x] 1.4 修改 get_all_recent_records 方法，支持 model 过滤
- [x] 1.5 修改 get_latest_record 方法，支持 model 参数

## 2. Adapter 改造

- [x] 2.1 修改 test_connection 方法，支持指定 model 参数
- [x] 2.2 修改 _test_model 方法，支持指定 model 测试
- [x] 2.3 添加 _find_working_model 方法，查找可用模型

## 3. Agent 多模型测试

- [x] 3.1 修改 HealthMonitor，保存模型列表
- [x] 3.2 修改 run_test 方法，遍历所有模型进行测试
- [x] 3.3 添加刷新模型列表的逻辑（当模型 not found 时）
- [x] 3.4 确保每个模型的测试结果正确记录到数据库

## 4. Web API 扩展

- [x] 4.1 添加 /api/models 接口，返回所有模型及其最新状态
- [x] 4.2 修改 /api/availability 接口，按模型分组返回
- [x] 4.3 添加 /api/models/<model_name>/availability 接口，返回指定模型的统计
- [x] 4.4 添加 /api/models/<model_name>/history 接口，返回指定模型的历史数据

## 5. 前端看板改造

- [x] 5.1 修改主页展示为模型卡片列表
- [x] 5.2 每个模型卡片显示名称、在线/离线状态
- [x] 5.3 点击模型卡片显示该模型的详情弹窗/面板
- [x] 5.4 详情面板显示该模型的 6 个时间窗口可用性
- [x] 5.5 详情面板显示该模型的 24 小时趋势图
