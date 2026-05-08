# RainFly NewAPI监控

一个基于 Python + Flask + SQLite 的多模型 NewAPI 监控看板。

它会在设定时间窗口内定时拉取模型列表，对每个模型执行最小化测活请求，记录可用性、延迟、错误信息，并通过 Web 看板展示各模型的最新状态、历史趋势和多时间窗口可用性。

![1778227850325](image/README/1778227850325.png)

![1778228544876](image/README/1778228544876.png)

## 功能特性

- 自动从 NewAPI `/models` 拉取模型列表
- 按模型逐个执行测活检查
- 支持工作时间窗口限制，默认仅在 `8:00 - 18:00` 执行
- 默认每 `3` 分钟执行一次监控
- 记录可用性、延迟、错误信息、重试次数到 SQLite
- 展示模型最新状态、延迟、最近测试时间
- 展示 `3分钟 / 30分钟 / 3小时 / 6小时 / 12小时 / 24小时` 可用性
- 展示单模型 24 小时可用性趋势与延迟趋势
- 支持模型名称点击复制
- 支持模型状态区按名称模糊搜索、按在线/离线筛选
- 自动清理过期历史数据

## 项目结构

```text
自动测活/
├─ monitor/
│  ├─ agent.py          # 定时监控主程序
│  ├─ adapter.py        # NewAPI 适配器
│  ├─ database.py       # SQLite 数据读写
│  └─ config.py         # 配置加载
├─ web/
│  ├─ app.py            # Flask Web 服务
│  └─ templates/
│     └─ index.html     # 监控看板页面
├─ data/
│  └─ monitor.db        # 监控数据数据库
├─ config.yaml          # 项目配置
├─ start.bat            # Windows 启动脚本
├─ stop.bat             # Windows 停止脚本
├─ start.sh             # Linux/macOS 启动脚本
├─ stop.sh              # Linux/macOS 停止脚本
└─ requirements.txt     # Python 依赖
```

## 运行原理

### 1. 模型发现

监控程序会调用 NewAPI 的：

- `GET /v1/models`

获取当前可用模型列表，并与数据库中已有历史模型合并，避免新增模型没被监控或历史模型直接丢失展示。

### 2. 测活请求

对每个模型发送最小请求进行探测，核心请求格式类似：

```json
{
  "model": "模型名",
  "messages": [{"role": "user", "content": "Hi"}],
  "max_tokens": 10
}
```

其中快速探测路径会使用更小的 `max_tokens`。

### 3. 数据存储

所有测试记录都会写入 SQLite：

- 默认数据库文件：`data/monitor.db`

记录内容包括：

- `timestamp`
- `model`
- `available`
- `latency_ms`
- `error_message`
- `retry_count`

### 4. 看板展示

Web 看板会读取数据库中的最新状态和历史记录，并提供：

- 模型总数 / 在线 / 离线统计
- 模型卡片列表
- 模型详情弹窗
- 多时间窗口可用性统计
- 历史趋势图
- 搜索与状态筛选

## 环境要求

- Python 3.9+（建议）
- 可访问目标 NewAPI 服务
- Windows / Linux / macOS

## 安装依赖

```bash
pip install -r requirements.txt
```

当前 `requirements.txt` 包含：

- `requests`
- `schedule`
- `PyYAML`

如果环境里没有 Flask，需要额外安装：

```bash
pip install flask
```

## 配置说明

编辑 `config.yaml`：

```yaml
newapi:
  endpoint: "http://192.168.1.21:3000/v1"
  api_key: "your-api-key"
  timeout: 60

scheduler:
  interval_minutes: 3
  time_window:
    start_hour: 8
    end_hour: 18

database:
  path: "data/monitor.db"

retention:
  days: 30

web:
  host: "0.0.0.0"
  port: 5000
```

### 配置项说明

#### `newapi`

- `endpoint`: NewAPI 服务地址，通常以 `/v1` 结尾
- `api_key`: 调用 NewAPI 的密钥
- `timeout`: 单次请求超时时间，单位秒

#### `scheduler`

- `interval_minutes`: 执行间隔，单位分钟
- `time_window.start_hour`: 允许执行的开始小时
- `time_window.end_hour`: 允许执行的结束小时

#### `database`

- `path`: SQLite 文件路径

#### `retention`

- `days`: 历史数据保留天数，启动时会清理旧记录

#### `web`

- `host`: Web 服务监听地址
- `port`: Web 服务端口

## 启动方式

### Windows

直接运行：

```bat
start.bat
```

脚本会自动：

1. 安装依赖
2. 启动监控 Agent
3. 启动 Web 看板

启动后访问：

- `http://localhost:5000`

### Linux / macOS

先给脚本执行权限：

```bash
chmod +x start.sh stop.sh
```

再启动：

```bash
./start.sh
```

启动后访问：

- `http://localhost:5000`

## 停止服务

### Windows

```bat
stop.bat
```

注意：当前脚本会停止所有 `python.exe` 进程，适合独立机器使用；如果机器上还有别的 Python 程序，建议后续改成更精确的停止方式。

### Linux / macOS

```bash
./stop.sh
```

## 单独运行

### 仅运行一次监控测试

```bash
python -m monitor.agent --config config.yaml
```

### 守护模式运行监控

```bash
python -m monitor.agent --config config.yaml --daemon
```

### 单独启动 Web 服务

```bash
python -m web.app
```

## 日志文件

启动脚本默认输出以下日志：

- `monitor.log`: 监控 Agent 日志
- `web.log`: Web 服务日志

## API 接口

### `GET /api/models`

返回所有模型的最新状态列表，按：

1. 在线优先
2. 延迟低优先

### `GET /api/status`

返回所有模型的实时状态映射。

### `GET /api/models/<model_name>/availability`

返回指定模型在多个时间窗口下的可用性统计。

### `GET /api/models/<model_name>/history`

返回指定模型最近 24 小时历史记录。

### `GET /api/availability`

返回所有模型分组后的多时间窗口可用性数据。

### `GET /api/history`

返回所有模型分组后的最近 24 小时历史数据。

## 前端使用说明

### 模型状态区

支持以下操作：

- 点击模型卡片打开详情
- 点击模型名称复制名称
- 输入关键词进行模型名称模糊检索
- 按全部 / 仅在线 / 仅离线筛选

### 模型详情弹窗

包含：

- 3分钟、30分钟、3小时、6小时、12小时、24小时可用性
- 可用性趋势图
- 延迟趋势图

## 常见问题

### 1. 页面没有数据

检查以下几项：

- `config.yaml` 中 `endpoint` 和 `api_key` 是否正确
- Agent 是否已经启动
- 当前时间是否在 `time_window` 范围内
- `monitor.log` 是否有报错

### 2. 某些模型显示离线

这通常是以下原因之一：

- `model_not_found`
- 当前 token 无该模型权限
- 上游渠道无可用通道
- 请求超时
- API key 状态异常

可以直接查看：

- 卡片状态
- 详情趋势
- `monitor.log`

### 3. 新增模型没有显示

正常情况下，系统会在每次执行任务时重新获取模型列表；如果仍未显示，可检查：

- `/v1/models` 是否已经返回该模型
- Agent 是否仍在运行
- 是否存在网络或鉴权问题

### 4. 趋势图为空

需要对应模型已有历史记录；如果是新启动项目，等待几轮测试后会逐步显示。

## 后续可优化项

- 更精确的 Windows 停止脚本，避免误杀全部 Python 进程
- 增加服务自恢复 / PID 管理
- 增加日志编码处理，避免 Windows 控制台乱码
- 增加异常模型告警能力
- 增加导出报表能力

## License

如需开源发布，建议补充具体 License。
