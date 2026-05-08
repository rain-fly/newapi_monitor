## 1. 图标资源准备

- [x] 1.1 创建 `web/static/icons/` 目录
- [x] 1.2 从 Iconfont 搜索并下载各厂商 SVG 图标（建议 64x64 或 128x128） - 已创建占位文件
- [x] 1.3 将 SVG 文件重命名为 `{厂商名}.svg` 格式
- [x] 1.4 验证所有 SVG 文件可正常打开和渲染

## 2. CSS 样式添加

- [x] 1.1 在 `index.html` 的 `<style>` 区域添加 `.vendor-logo` 和 `.model-info` 样式类
- [x] 1.2 确保 Logo 在深色背景下可正常显示（使用 filter）

## 2. JavaScript 映射表创建

- [x] 2.1 在 `<script>` 中创建 `VENDOR_LOGOS` 常量对象，包含所有厂商与 Simple Icons slug 的映射
- [x] 2.2 添加 `getVendorLogo(vendor)` 函数，根据厂商名返回 Logo URL 或 null

## 3. 模板结构调整

- [x] 3.1 修改模型卡片的 HTML 结构，为 `.card-header` 增加 `.model-info` 容器包裹 Logo 和模型名称
- [x] 3.2 确保结构变更不影响现有的复制功能和 tooltip

## 4. 渲染逻辑修改

- [x] 4.1 修改 `renderModels()` 函数，在渲染标签前先渲染厂商 Logo
- [x] 4.2 调用 `getVendorLogo()` 获取 Logo URL
- [x] 4.3 添加 `<img>` 标签，设置 alt 为厂商名称

## 5. 错误处理与降级

- [x] 5.1 为 Logo 的 `<img>` 添加 `onerror` 回调，隐藏加载失败的图片
- [x] 5.2 确保即使 Logo 加载失败，模型名称仍然正常显示

## 6. 测试验证

- [ ] 6.1 在浏览器中打开页面，检查所有厂商 Logo 是否正确显示
- [ ] 6.2 验证筛选功能（按厂商、状态、关键词）正常工作
- [ ] 6.3 检查模型卡片弹窗详情是否正常
- [ ] 6.4 验证响应式布局（在窄屏宽度下 Logo 不会溢出）
