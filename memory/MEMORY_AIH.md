# AI-H 项目记忆

## 工作原则
- **阶段性成果管理**：任务有阶段性成果时，立即保存成果文件，删除失效文件，保持目录整洁。

## 项目定位
一人猎头公司全流程自动化系统。三智能体架构：Scout → Butler → Judge → 飞书表格报告

## 核心配置

### Chrome调试模式（必须记住）
```powershell
taskkill /F /IM chrome.exe
Start-Sleep -Seconds 2
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\宗璐\chrome-debug-profile"
```
- 必须用独立profile（`chrome-debug-profile`）
- 连接地址：`http://127.0.0.1:9222`
- 桢哥登录后，Playwright通过CDP接管

### GitHub备份
- 仓库：https://github.com/lincolnyinji-bot/3agents
- Token：[保存在本地MEMORY文件中]

## 核心脚本
- `3agents/aih_pipeline_v3.py` - 主流程（当前版本）
- `3agents/optimized_judge_v3.py` - Judge V3算法
- `3agents/urgent_jobs_manager.py` - 紧急需求管理
- `3agents/recruitlite_integration.py` - RecruitLite对接

## 完成度
- ✅ Chrome连接、搜索、筛选、提取候选人
- ✅ Judge V3评估（准确率>90%）
- ✅ RecruitLite系统对接
- ✅ 定时任务（每天午夜12点）
- ⏳ 期望城市筛选（目前用"目前城市"）

## Judge V3核心规则
- 产业CVC ≥ 头部VC > 区域性VC
- 推荐桶：≥75分
- 潜力桶：<75分但有投资相关经历
- VC版权重：投资经验30%、AI行业理解25%、项目获取20%、学历15%、成长潜力10%

## RecruitLite系统
- 后端：`recruitlite-api/app.py`
- 前端：`recruitlite-api/recruit-lite.html`
- 启动：`python app.py` → `http://127.0.0.1:5000`
- 核心接口：POST `/api/talents/batch`（AI-H批量推送）

## 待优化
- 期望城市筛选功能
- Judge算法需更多真实offer校准
- PE版算法（财务分析权重恢复）
