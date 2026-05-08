## Why

当前看板以纯文字标签形式展示厂商名称，视觉辨识度较低。用户难以快速区分不同厂商，特别是当模型列表较长时，厂商信息不够直观。添加厂商 Logo 可以提升视觉层次感和专业度，让用户一目了然地识别模型所属厂商。

## What Changes

- 在模型卡片上为每个厂商添加对应的 Logo 图标
- 保持响应式设计，Logo 在不同屏幕尺寸下均可正常显示
- 使用 CDN 托管的 SVG 图标或开源图标库，确保加载速度

## Capabilities

### New Capabilities

- `vendor-logo-display`: 厂商 Logo 展示能力，包括：
  - 在模型卡片头部显示厂商 Logo
  - Logo 与厂商标签配合使用，增强可读性
  - 支持 15+ 主流 AI 厂商的图标

### Modified Capabilities

- `model-list-display`: 现有模型列表展示能力需要支持 Logo 渲染

## Impact

- 前端：index.html 需要引入厂商 Logo 资源并修改卡片模板
- 样式：增加 `.vendor-logo` 和 `.model-info` CSS 样式类
- 资源：在 `web/static/icons/` 目录存储各厂商 SVG 图标文件

## Non-Goals

- 不实现厂商官网链接跳转
- 不实现可配置的 Logo 显示开关
- 不实现厂商自定义上传功能
