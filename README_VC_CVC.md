# 区域性VC和产业CVC识别系统

## 已完成

### 1. 极简索引文件
- 位置：`vc_institutions_index.md`
- 内容：包含头部VC、区域性VC、产业CVC完整列表
- 分类：按地域、产业、专业领域组织

### 2. Judge算法升级
- 文件：`optimized_judge_v3.py`
- 新增：机构类型识别（产业CVC/区域性VC/头部VC）
- 优化：机构类型差异化加分

### 3. 测试验证
- 脚本：`test_regional_cvc.py`
- 结果：5个测试用例全部通过
- 验证：产业CVC和区域性VC正确识别并加分

## 核心改进

### 机构识别
```python
# 产业CVC（最高优先级）
industry_cvc = ['华为哈勃', '小米长江', 'OPPO巡星', 'vivo投资', '比亚迪', '宁德时代']

# 区域性VC
regional_vc = ['深创投', '元禾', '上海科创', '浙江金控', '杭州高新']

# 头部VC
big_institutions = ['高瓴', '红杉', 'IDG', 'GGV', '源码']
```

### 加分规则
1. **投资经验分**（满分30）
   - 产业CVC：+8分（IM级别）
   - 区域性VC：+6分
   - 头部VC：+5分

2. **行业理解分**（满分25）
   - 产业CVC：额外+3分（深度行业理解）

3. **网络质量分**（满分20）
   - 产业CVC：+8分
   - 区域性VC：+7分
   - 头部VC：+6分

## 使用示例

### 候选人评估
```python
from optimized_judge_v3 import OptimizedJudgeV3

# 创建评估器
judge = OptimizedJudgeV3(position_level="IM")

# 评估候选人
result = judge.analyze_resume(简历文本, candidate_name="候选人姓名")

# 查看结果
print(f"机构类型: {result['basic_info']['institution_type']}")
print(f"总分: {result['total_score']}")
print(f"推荐: {result['recommendation']}")
```

### 测试用例
```python
# 产业CVC候选人（华为哈勃）
text = "姓名：张明\n工作经历：华为哈勃投资投资经理\n投资经验：3年"

# 区域性VC候选人（深创投）  
text = "姓名：李华\n工作经历：深创投投资总监\n投资经验：8年"

# 头部VC候选人（红杉）
text = "姓名：赵敏\n工作经历：红杉资本投资经理\n投资经验：4年"
```

## 匹配逻辑

### 优先级
1. **产业匹配**：候选人专业方向 + 机构投资领域
2. **地域匹配**：候选人所在地 + 机构区域布局  
3. **阶段匹配**：候选人经验年限 + 机构投资阶段

### 推荐策略
- **产业CVC背景**：优先推荐给相关产业职位
- **区域性VC背景**：优先推荐给当地职位
- **头部VC背景**：适合全国性职位

## 后续优化方向

### 短期（1-2周）
1. 增加更多产业CVC机构识别
2. 优化地域匹配算法
3. 添加机构投资阶段识别

### 中期（1个月）
1. 集成到AI-H Pipeline自动评估
2. 添加机构投资案例数据库
3. 实现智能推荐匹配

### 长期（3个月）
1. 建立机构画像系统
2. 实现动态机构评分
3. 集成外部数据源更新