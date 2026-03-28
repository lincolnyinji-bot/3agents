# BD助理项目记忆

## 项目定位
猎头BD自动化工具，监控行业公众号获取创投机构招聘线索。

## 目录
`C:\Users\宗璐\.openclaw\workspace\bd_assistant\`

## 核心文件
- `bd_assistant.py` - 主流程（Tavily搜索 + 百度OCR）
- `baidu_ocr.py` - 百度OCR封装模块
- `vc_target_list.md` - 88家目标机构名单
- `bd_leads.db` - 结果数据库（运行后自动生成）

## 技术方案（已定型）
**Tavily搜索 + Browser滚动加载 + 百度OCR**

### 核心规则
1. 完整滚动页面，确保所有图片加载后再提取
2. 文本已含JD关键词则跳过OCR，节省额度
3. 无原始JD信息（职责/要求/联系方式）的线索视为无效，不保存
4. 百度OCR仅在必要时调用

### 百度OCR配置
- API_KEY: YkartzMn7Kyotzm5IUSafR3Q
- SECRET_KEY: sMwOXc9oimDXM4xxkxzgT6PZTStaSwW0
- 免费额度：1000次/天，准确率98%+

## 目标机构
88家（详见`vc_target_list.md`）：
- 头部美元/双币VC：23家
- 人民币精锐VC：31家
- 产业CVC：15家
- 家办/体外CVC：7家
- 具身智能公司：12家

## 待开发
1. **机构名单集成**：将88家机构名称作为精准搜索词替代通用关键词
2. **定时任务**：自动定期运行
3. **邮件监控模块**：监控招聘邮件
4. **智能匹配**：职位-候选人匹配

## 已废弃方案（勿再尝试）
- Tesseract OCR：中文识别率极低
- PaddleOCR本地：Windows无预编译包，安装失败
- 微信桌面自动化：OCR识别率低，已放弃
- 剪贴板方案：微信内容不支持全选
