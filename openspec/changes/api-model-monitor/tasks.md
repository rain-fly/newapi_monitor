## 1. 项目初始化

- [x] 1.1 创建项目目录结构（monitor/、web/、config/）
- [x] 1.2 创建 config.yaml 配置文件（API Endpoint、API Key、调度间隔等）
- [x] 1.3 创建 requirements.txt 依赖文件

## 2. 数据模型

- [x] 2.1 设计 SQLite 数据库表结构（test_records 表）
- [x] 2.2 创建数据库初始化模块
- [x] 2.3 实现数据持久化操作类

## 3. NewAPI 适配器

- [x] 3.1 实现 API 配置加载模块
- [x] 3.2 实现 NewAPI 调用封装（requests）
- [x] 3.3 实现重试机制
- [x] 3.4 实现响应解析和延迟计算

## 4. 定时调度 Agent

- [x] 4.1 实现时间窗口判断逻辑（8:00-18:00）
- [x] 4.2 实现 schedule 库调度循环
- [x] 4.3 实现最小 Token 测试函数
- [x] 4.4 实现守护进程模式运行
- [x] 4.5 实现30天数据清理逻辑

## 5. Web 看板

- [x] 5.1 创建 Flask Web 服务入口
- [x] 5.2 实现看板主页路由（/）
- [x] 5.3 实现多时间窗口可用性 API（/api/availability）
- [x] 5.4 实现实时状态 API（/api/status）
- [x] 5.5 实现历史数据 API（/api/history）
- [x] 5.6 前端页面：状态指示器和基本信息展示
- [x] 5.7 前端页面：ECharts 可用性趋势图
- [x] 5.8 前端页面：ECharts 延迟趋势图
- [x] 5.9 前端页面：多时间窗口可用性卡片

## 6. 启动脚本

- [x] 6.1 创建统一启动脚本（start.sh / start.bat）
- [x] 6.2 创建停止脚本（stop.sh / stop.bat）
