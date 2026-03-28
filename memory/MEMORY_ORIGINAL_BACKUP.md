# MEMORY.md 原版备份（2026-03-29）

> 注意：Token等敏感信息已移除，完整版保存在本地MEMORY_ORIGINAL_BACKUP.md

## AI-H 项目

### 项目定位
一人猎头公司全流程自动化系统。三智能体架构：Scout → Butler → Judge → 飞书表格报告

### 完成度
- Chrome连接：✅
- 关键词搜索：✅
- 筛选条件设置：✅
- 候选人提取：✅（30个/页）
- Judge V3评估：✅
- 定时任务：✅
- RecruitLite对接：✅
- 期望城市筛选：⏳

### Judge算法 V3
- 产业CVC ≥ 头部VC > 区域性VC
- 推荐桶：≥75分，潜力桶：<75分但有投资经历

### RecruitLite系统
- Flask后端 + SQLite
- 新增「待入职」状态
- Kanban内联备注
- AI-H对接完成

## BD助理项目

### 方案演进
1. Tesseract OCR - 失败
2. PaddleOCR - Windows安装失败
3. 微信桌面自动化 - 放弃
4. Tavily + 百度OCR - 最终方案✅

### 最终技术栈
- Tavily搜索微信公众号
- Browser滚动加载完整页面
- 百度OCR识别图片文字
- 无效JD过滤

### 百度OCR
- API_KEY/SECRET_KEY保存在本地
- 免费额度：1000次/天，准确率98%+
