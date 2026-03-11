# JDdog-agent-LP

## 功能概述
根据JD和补充说明，生成猎聘平台搜索关键词和筛选条件

## 核心特性
1. **JD智能解析**：大模型解析职位描述
2. **平台适配**：精确匹配猎聘UI规则
3. **关键词扩展**：25个脑科学相关组合
4. **质量导向**：不以数量评判效果
5. **定期执行**：每天自动运行

## 文件结构
```
jddog_agent/
├── README.md          # 说明文档
├── config.py          # 配置文件
├── jd_parser.py       # JD解析模块
├── platform_rules.py  # 平台规则库
├── keyword_generator.py # 关键词生成器
├── filter_generator.py # 筛选条件生成器
├── main.py           # 主程序
└── requirements.txt   # 依赖列表
```

## 使用示例
```python
from jddog_agent import JDDogAgent

# 初始化
agent = JDDogAgent(platform="猎聘")

# 输入JD和补充说明
jd_text = "医健基金高级投资经理/投资总监 -（脑/神经科学）..."
supplement = "苛刻客户"

# 生成搜索条件
result = agent.generate_search_conditions(jd_text, supplement)
print(result)
```

## 输出格式
```json
{
  "search_keywords": ["脑神经 投资", "脑科学 投资", ...],
  "filters": {
    "city": "上海",
    "experience": "5-10年",
    "education": ["硕士", "博士"],
    "school_tier": ["985", "海外留学"]
  },
  "platform_notes": "猎聘平台注意事项..."
}
```