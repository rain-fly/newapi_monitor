## Context

当前模型卡片通过文字标签（`.tag-vendor`）展示厂商信息。虽然功能正常，但视觉上不够突出，厂商间区分度不高。需要为每个已知厂商添加对应的 Logo 图标，增强视觉辨识度。

## Goals / Non-Goals

**Goals:**
- 为每个已知的 15 个厂商添加对应的 Logo
- Logo 放置在模型卡片头部区域
- 保持与现有深色主题的视觉一致性
- 确保页面加载性能不受明显影响

**Non-Goals:**
- 不实现厂商官网外链
- 不实现动态切换 Logo 主题（深色/浅色）
- 不使用自定义上传的 Logo

## Decisions

### 1. Logo 来源：Iconfont 阿里图标库

使用 Iconfont（iconfont.cn）作为图标来源，这是阿里巴巴提供的免费图标库，包含众多国内外厂商的官方图标。

**为什么：**
- 国内访问速度快，CDN 稳定
- 包含众多国内 AI 厂商的官方图标（如阿里千问、字节豆包等）
- 支持 SVG 和 CDN 多格式
- 图标风格统一，支持多色图标

**替代方案考虑：**
- Simple Icons：国外 CDN，国内访问较慢，部分国内厂商图标缺失
- Font Awesome：AI 厂商 Logo 有限
- Emoji：视觉效果不够专业

### 2. Logo 映射表

| 厂商 | Iconfont 关键词 | 图标类型 |
|------|-----------------|----------|
| OpenAI | openai | 单色 |
| Anthropic | anthropic | 单色 |
| Google | google | 单色 |
| DeepSeek | deepseek | 单色 |
| 智谱 | zhipuai / glm | 单色 |
| MiniMax | minimax | 单色 |
| 美团 | meituan | 单色 |
| 字节跳动 | bytedance / doubao | 单色 |
| 月之暗面 | moonshot / kimi | 单色 |
| 千问 | qwen | 单色 |
| xAI | xai | 单色 |
| Mistral | mistral | 单色 |
| Meta | meta | 单色 |
| NVIDIA | nvidia | 单色 |
| 小米 | xiaomi | 单色 |
| unknown | question | 单色 |

**图标获取方式：**
从 `https://www.iconfont.cn/search/index?searchType=icon&q={关键词}` 搜索并下载 SVG 文件，存储到 `web/static/icons/` 目录。

### 3. Logo 存储结构

```
web/static/icons/
├── openai.svg
├── anthropic.svg
├── google.svg
├── deepseek.svg
├── zhipuai.svg
├── minimax.svg
├── meituan.svg
├── bytedance.svg
├── moonshot.svg
├── qwen.svg
├── xai.svg
├── mistral.svg
├── meta.svg
├── nvidia.svg
├── xiaomi.svg
└── unknown.svg
```

### 4. Logo 渲染方式

在模型卡片的 `.card-header` 区域添加 Logo 图标：

```html
<div class="card-header">
    <div class="model-info">
        <img class="vendor-logo" src="/static/icons/openai.svg" alt="OpenAI">
        <span class="model-name">...</span>
    </div>
    <span class="status-indicator ..."></span>
</div>
```

**为什么：**
- Logo 与模型名称组合显示，保持信息层次
- 状态指示器仍在右侧
- 不改变现有布局结构

### 4. CSS 样式

```css
.vendor-logo {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    margin-right: 8px;
    vertical-align: middle;
    filter: brightness(0) invert(1); /* 适配深色背景 */
}

.model-info {
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 0;
}
```

**为什么：**
- 固定尺寸 20x20，与文字大小协调
- `filter: brightness(0) invert(1)` 将白色图标变深色以适配深色背景
- 关键厂商使用 brand color filter

## Risks / Trade-offs

[Risk] CDN 不可用导致 Logo 无法加载 → Mitigation：设置 fallback 为纯文字显示，添加 error 处理

[Risk] 某些小众厂商 Logo 不存在于 Simple Icons → Mitigation：使用统一的 unknown/default 图标或纯文字显示

## Migration Plan

1. 在 `index.html` 的 `<style>` 中添加 `.vendor-logo` 样式
2. 创建 JavaScript `VENDOR_LOGOS` 映射对象
3. 修改 `renderModels()` 函数，在渲染标签前先渲染 Logo
4. 更新 HTML 模板，为 `.card-header` 增加 Logo 容器
5. 测试验证所有厂商 Logo 正常显示
6. 检查响应式布局是否正常
