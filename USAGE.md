# JDdog-agent-LP 使用说明

## 快速开始

### 1. 安装依赖
```bash
cd jddog_agent
# 只需要Python 3.8+，无额外依赖
```

### 2. 运行示例
```bash
python3 main.py
```

### 3. 自定义使用
```python
from main import JDDogAgent

# 初始化
agent = JDDogAgent(platform="猎聘", strict_level="严格")

# 输入JD和补充说明
jd_text = "你的职位描述..."
supplement = "苛刻客户"  # 或其他补充说明

# 生成搜索条件
result = agent.generate_search_conditions(jd_text, supplement)

# 保存结果
agent.save_to_file(result, "my_search_plan.json")
agent.print_summary(result)
```

## 输出文件

### 1. 完整结果 (`jddog_output.json`)
```json
{
  "input": { ... },
  "parsed_jd": { ... },
  "search_keywords": {
    "core": ["脑科学 投资", "神经科学 投资"],
    "expanded": [...],  // 21个扩展组合
    "all": [...]        // 总计25+个组合
  },
  "filters": {
    "city": ["上海"],
    "experience": "5-12年",
    "education": ["博士"],
    "school_tier": ["985"]
  },
  "execution": {
    "execution_mode": "单日完成",
    "keywords_count": 25,
    "minimum_required": 25
  }
}
```

### 2. 单日搜索计划 (`single_day_search_plan.json`)
```json
{
  "day": "当天完成",
  "keywords": ["脑科学 投资", "神经科学 投资", ...],
  "count": 25,
  "note": "总计25个关键词组合，一天内全部搜索完成"
}
```

## 配置说明

### 平台支持
- `猎聘` (默认)
- `BOSS直聘` (部分支持)
- 可扩展其他平台

### 严格级别
- `严格`: 完全匹配JD要求
- `适中`: 适当放宽条件
- `宽松`: 大幅放宽条件

### 补充说明关键词
- `苛刻客户`: 最高标准筛选
- `放宽`: 放宽条件限制
- `不选`: 不选择某些条件

## 脑科学领域覆盖

### 核心领域
- 脑科学、神经科学、认知科学、神经工程

### 技术方向
- 脑机接口、神经接口、脑电控制

### 疾病相关
- 脑疾病、神经退行、帕金森、阿尔茨海默、癫痫、脑卒中

### 治疗方法
- 神经调控、深部脑刺激

### 检测技术
- 脑电图、磁共振、神经影像、脑成像

### 交叉学科
- 计算神经、人工智能+脑科学、系统神经科学

## 投资相关关键词
- 投资、投资经理、投资总监
- 基金投资、风险投资、PE、VC、私募股权

## 质量导向原则

1. **不以数量为标准**: 不因搜索结果少而否定关键词
2. **关注初筛通过率**: 一个高质量候选人胜过十个低质量
3. **关联扩展**: 脑科学相关概念全覆盖
4. **平台适配**: 精确匹配猎聘UI规则

## 扩展开发

### 1. 添加新平台
在 `platform_rules.py` 中添加新平台规则类

### 2. 集成大模型
在 `jd_parser.py` 中实现 `parse_with_llm()` 方法

### 3. 添加新领域
在 `config.py` 的 `BRAIN_SCIENCE_KEYWORDS` 中添加新领域

### 4. 添加执行器
创建 `executor.py` 实现自动化搜索

## 注意事项

1. 猎聘平台关键词用空格分隔，不用"+"
2. 工作年限可自定义输入"3-10年"格式
3. 学历和院校可多选
4. 不要选择JD未明确要求的条件（年龄、性别等）
5. 保存搜索条件便于重复执行

## 问题反馈

如有问题或建议，请提交Issue或联系开发者。