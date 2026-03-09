#!/usr/bin/env python3
"""
🧪 小蜜蜂Agent测试脚本

测试内容：
1. 模块导入测试
2. 数据模型测试
3. JD解析测试
4. 初筛规则测试
5. 记忆系统测试
6. 完整流程测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
from scout_agent import (
    ScoutAgent, JDParser, DoubleScreener, CandidateMemory, SmartSearcher,
    SearchStrategy, CandidateCard, ScreeningType, ScreeningResult, ScreeningDecision
)

print("🧪 开始小蜜蜂Agent测试...")
print("=" * 60)

# ==================== 测试1：模块导入 ====================
print("\n📦 测试1：模块导入")
try:
    from scout_agent import ScoutAgent
    print("✅ 模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

# ==================== 测试2：数据模型 ====================
print("\n📊 测试2：数据模型")

# 测试SearchStrategy
print("  测试SearchStrategy...")
strategy = SearchStrategy(
    keywords=["AI", "投资经理"],
    filters={"city": "深圳", "experience": "3-5年"},
    sort_by="最新活跃",
    max_results=100
)
assert isinstance(strategy.keywords, list), "keywords应该是列表"
assert "深圳" in strategy.filters.get("city", ""), "城市筛选应该包含深圳"
print("  ✅ SearchStrategy测试通过")

# 测试CandidateCard
print("  测试CandidateCard...")
candidate = CandidateCard(
    id="test_123",
    name="测试候选人",
    current_position="AI投资经理",
    current_company="测试公司",
    education="清华大学硕士",
    experience="5年投资经验",
    location="深圳",
    expected_city="深圳",
    last_active="今天活跃",
    source_url="https://test.com"
)
assert candidate.name == "测试候选人", "候选人姓名应该正确"
assert "清华" in candidate.education, "教育背景应该正确"
print("  ✅ CandidateCard测试通过")

# 测试序列化
print("  测试数据序列化...")
strategy_dict = strategy.to_dict()
candidate_dict = candidate.to_dict()
assert isinstance(strategy_dict, dict), "应该能转换为字典"
assert isinstance(candidate_dict, dict), "应该能转换为字典"
print("  ✅ 数据序列化测试通过")

# ==================== 测试3：JD解析器 ====================
print("\n🧠 测试3：JD解析器")

jd_parser = JDParser(model_client=None)
test_jd = "寻找深圳的AI方向投资经理，3-5年经验，985/211优先，有硬科技投资经验"

print(f"  测试JD: {test_jd[:50]}...")
strategy = jd_parser.parse_jd(test_jd)

assert isinstance(strategy, SearchStrategy), "应该返回SearchStrategy"
assert len(strategy.keywords) > 0, "应该提取出关键词"
assert "深圳" in str(strategy.filters.get("city", "")), "应该提取出城市"
print(f"  ✅ JD解析测试通过，关键词: {strategy.keywords}")

# 测试缓存
print("  测试JD解析缓存...")
strategy2 = jd_parser.parse_jd(test_jd)
assert strategy.keywords == strategy2.keywords, "缓存应该返回相同结果"
print("  ✅ 缓存测试通过")

# ==================== 测试4：初筛器 ====================
print("\n🎯 测试4：双层初筛器")

screener = DoubleScreener()

# 创建测试候选人
test_candidates = [
    CandidateCard(
        id="candidate_1",
        name="张AI-985",
        current_position="AI投资经理",
        current_company="红杉资本",
        education="清华大学硕士（计算机）985",
        experience="5年投资经验",
        location="深圳",
        expected_city="深圳",
        last_active="今天活跃",
        source_url="https://test.com/1"
    ),
    CandidateCard(
        id="candidate_2", 
        name="李商科",
        current_position="投资总监",
        current_company="某基金",
        education="北京大学本科（金融学）",
        experience="8年投资经验",
        location="北京",
        expected_city="北京",
        last_active="1周内活跃",
        source_url="https://test.com/2"
    ),
    CandidateCard(
        id="candidate_3",
        name="王销售",
        current_position="销售总监",
        current_company="某科技公司",
        education="普通本科",
        experience="10年销售经验",
        location="广州",
        expected_city="广州",
        last_active="1月内活跃",
        source_url="https://test.com/3"
    )
]

print("  测试严格快筛...")
for i, candidate in enumerate(test_candidates):
    decision = screener.screen(candidate, ScreeningType.STRICT)
    print(f"    {candidate.name}: {decision.result.value} - {decision.reason}")
    
    # 验证规则
    if i == 1:  # 李商科，应该被拒绝
        assert decision.result == ScreeningResult.REJECT, "商科背景应该被拒绝"
    elif i == 2:  # 王销售，应该被拒绝
        assert decision.result == ScreeningResult.REJECT, "销售岗位应该被拒绝"

print("  测试宽松快筛...")
for candidate in test_candidates[:2]:  # 只测试前两个
    decision = screener.screen(candidate, ScreeningType.LOOSE)
    print(f"    {candidate.name}: {decision.result.value} - {decision.reason}")

print("  ✅ 初筛器测试通过")

# ==================== 测试5：记忆系统 ====================
print("\n💾 测试5：记忆系统")

# 使用临时文件测试
memory = CandidateMemory(memory_file="test_memory.json")

print("  测试重复检测...")
assert memory.should_process(test_candidates[0]), "第一次应该处理"
memory.record_processing(test_candidates[0], ScreeningDecision(
    candidate_id=test_candidates[0].get_fingerprint(),
    candidate_name=test_candidates[0].name,
    screening_type=ScreeningType.STRICT,
    result=ScreeningResult.PASS,
    reason="测试",
    rules_applied=[],
    timestamp=datetime.now()
))

# 短时间内不应该重复处理
assert not memory.should_process(test_candidates[0]), "短时间内不应该重复处理"

print("  测试统计信息...")
stats = memory.get_stats()
assert stats["total_processed"] > 0, "应该有处理记录"
print(f"    处理统计: {stats}")

# 清理测试文件
if os.path.exists("test_memory.json"):
    os.remove("test_memory.json")

print("  ✅ 记忆系统测试通过")

# ==================== 测试6：完整流程 ====================
print("\n🔄 测试6：完整流程")

print("  初始化ScoutAgent...")
agent = ScoutAgent(use_model=False)

print("  测试JD处理流程...")
result = agent.process_jd(test_jd, ScreeningType.STRICT)

assert result["success"], "处理应该成功"
assert "passed_candidates" in result, "结果应该包含通过候选人"
assert "search_strategy" in result, "结果应该包含搜索策略"

print(f"  处理结果:")
print(f"    总候选人: {result['total_candidates']}")
print(f"    处理候选人: {result['processed_candidates']}")
print(f"    通过初筛: {result['passed_candidates']}")

if result['passed_candidates'] > 0:
    print(f"\n  通过候选人详情:")
    for candidate in result['passed_list'][:2]:  # 显示前两个
        print(f"    - {candidate['candidate']['name']}")
        print(f"      职位: {candidate['candidate']['current_position']}")
        print(f"      公司: {candidate['candidate']['current_company']}")
        print(f"      原因: {candidate['decision']['reason']}")

print("  测试Agent状态...")
status = agent.get_status()
assert status["status"] == "running", "Agent状态应该是running"
print(f"    Agent状态: {status['status']}")
print(f"    已处理候选人: {status['stats']['total_candidates']}")

print("  ✅ 完整流程测试通过")

# ==================== 测试7：严格 vs 宽松对比 ====================
print("\n📊 测试7：严格/宽松模式对比")

print("  执行严格快筛...")
strict_result = agent.process_jd(test_jd, ScreeningType.STRICT)

print("  执行宽松快筛...")
loose_result = agent.process_jd(test_jd, ScreeningType.LOOSE)

print("  对比结果:")
print(f"    严格模式通过: {strict_result['passed_candidates']}")
print(f"    宽松模式通过: {loose_result['passed_candidates']}")

# 宽松模式应该不少于严格模式
assert loose_result['passed_candidates'] >= strict_result['passed_candidates'], \
    "宽松模式通过数应该不少于严格模式"

print("  ✅ 模式对比测试通过")

# ==================== 清理和总结 ====================
print("\n🧹 清理测试数据...")
if os.path.exists("candidate_memory.json"):
    os.remove("candidate_memory.json")
if os.path.exists("test_memory.json"):
    os.remove("test_memory.json")

print("\n" + "=" * 60)
print("🎉 所有测试通过！")
print("\n📋 测试总结:")
print(f"  1. ✅ 模块导入 - 通过")
print(f"  2. ✅ 数据模型 - 通过")
print(f"  3. ✅ JD解析器 - 通过")
print(f"  4. ✅ 初筛器 - 通过")
print(f"  5. ✅ 记忆系统 - 通过")
print(f"  6. ✅ 完整流程 - 通过")
print(f"  7. ✅ 模式对比 - 通过")
print("\n🚀 小蜜蜂Agent核心功能验证完成！")

# 生成测试报告
test_report = {
    "test_time": datetime.now().isoformat(),
    "agent_version": "1.0.0",
    "tests_passed": 7,
    "tests_failed": 0,
    "strict_passed": strict_result['passed_candidates'],
    "loose_passed": loose_result['passed_candidates'],
    "total_processed": status['stats']['total_candidates'],
    "memory_stats": memory.get_stats() if 'memory' in locals() else {}
}

with open("test_report.json", "w", encoding="utf-8") as f:
    json.dump(test_report, f, ensure_ascii=False, indent=2)

print(f"\n📄 测试报告已保存: test_report.json")