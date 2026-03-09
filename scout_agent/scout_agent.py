#!/usr/bin/env python3
"""
🐝 小蜜蜂Agent - 智能候选人发现系统

功能：
1. JD理解 → 搜索策略（大模型驱动）
2. 智能搜索执行（猎聘平台）
3. 双层初筛（严格/宽松）
4. 记忆去重
5. 结构化输出

作者：OpenClaw助手
创建时间：2026-03-07
"""

import json
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ScoutAgent")

# ==================== 数据模型 ====================

class ScreeningType(Enum):
    STRICT = "strict"    # 严格快筛
    LOOSE = "loose"      # 宽松快筛

class ScreeningResult(Enum):
    PASS = "pass"        # 通过初筛
    REJECT = "reject"    # 否决
    NEED_DETAIL = "need_detail"  # 需要查看详情

@dataclass
class SearchStrategy:
    """搜索策略"""
    keywords: List[str]           # 搜索关键词
    filters: Dict[str, Any]      # 筛选条件
    sort_by: str                 # 排序方式
    max_results: int = 100       # 最大结果数
    source_jd: str = ""          # 原始JD文本
    
    def to_dict(self):
        return asdict(self)
    
    def get_search_id(self):
        """生成搜索ID（用于记忆去重）"""
        content = f"{self.keywords}{self.filters}{self.sort_by}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

@dataclass
class CandidateCard:
    """候选人卡片信息（从搜索结果页提取）"""
    id: str                      # 候选人ID（平台ID或生成ID）
    name: str                    # 姓名
    current_position: str        # 当前职位
    current_company: str         # 当前公司
    education: str               # 教育背景
    experience: str              # 工作经验/年限
    location: str                # 所在地
    expected_city: str           # 期望城市
    last_active: str             # 最后活跃时间
    source_url: str              # 来源URL
    platform: str = "liepin"     # 平台来源
    raw_data: Dict[str, Any] = None  # 原始数据
    
    def get_fingerprint(self):
        """生成候选人指纹（用于去重）"""
        content = f"{self.id}{self.name}{self.current_company}{self.current_position}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ScreeningDecision:
    """初筛决策结果"""
    candidate_id: str
    candidate_name: str
    screening_type: ScreeningType
    result: ScreeningResult
    reason: str                   # 决策原因
    rules_applied: List[str]      # 应用的规则
    timestamp: datetime
    
    def to_dict(self):
        return {
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "screening_type": self.screening_type.value,
            "result": self.result.value,
            "reason": self.reason,
            "rules_applied": self.rules_applied,
            "timestamp": self.timestamp.isoformat()
        }

# ==================== JD理解模块 ====================

class JDParser:
    """JD理解器 - 大模型驱动"""
    
    def __init__(self, model_client=None):
        """
        初始化JD解析器
        
        Args:
            model_client: 大模型客户端（如OpenAI/DeepSeek）
                        如果为None，使用模拟数据
        """
        self.model_client = model_client
        self.cache = {}  # JD缓存，避免重复解析
        
    def parse_jd(self, jd_text: str) -> SearchStrategy:
        """
        解析JD文本，生成搜索策略
        
        示例JD: "寻找深圳的AI方向投资经理，3-5年经验，985/211优先，有硬科技投资经验"
        """
        logger.info(f"开始解析JD: {jd_text[:50]}...")
        
        # 检查缓存
        jd_hash = hashlib.md5(jd_text.encode()).hexdigest()[:16]
        if jd_hash in self.cache:
            logger.info("使用缓存结果")
            return self.cache[jd_hash]
        
        if self.model_client:
            # 使用大模型解析
            strategy = self._parse_with_model(jd_text)
        else:
            # 模拟解析（开发测试用）
            strategy = self._parse_mock(jd_text)
        
        # 设置原始JD
        strategy.source_jd = jd_text
        
        # 缓存结果
        self.cache[jd_hash] = strategy
        
        return strategy
    
    def _parse_with_model(self, jd_text: str) -> SearchStrategy:
        """使用大模型解析JD"""
        # 这里应该调用大模型API
        # 为减少Token消耗，暂时使用模拟数据
        return self._parse_mock(jd_text)
    
    def _parse_mock(self, jd_text: str) -> SearchStrategy:
        """模拟JD解析（根据关键词简单规则）"""
        jd_lower = jd_text.lower()
        
        # 提取城市
        city = "深圳"  # 默认
        for c in ["北京", "上海", "广州", "深圳", "杭州"]:
            if c in jd_text:
                city = c
                break
        
        # 提取关键词
        keywords = []
        if "ai" in jd_lower or "人工智能" in jd_text:
            keywords.append("AI")
        if "投资" in jd_text:
            keywords.append("投资")
        if "经理" in jd_text:
            keywords.append("经理")
        if "总监" in jd_text:
            keywords.append("总监")
        
        if not keywords:
            keywords = ["投资经理"]
        
        # 构建搜索策略
        strategy = SearchStrategy(
            keywords=keywords,
            filters={
                "city": city,
                "experience": "3-5年",  # 默认
                "education": "本科",
                "salary": "",  # 待解析
            },
            sort_by="最新活跃",  # 猎头最关注新机会的候选人
            max_results=50
        )
        
        logger.info(f"JD解析完成: {strategy.keywords} @ {city}")
        return strategy

# ==================== 记忆系统 ====================

class CandidateMemory:
    """候选人记忆系统 - 避免重复处理"""
    
    def __init__(self, memory_file="candidate_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
        self.cleanup_days = 30  # 清理30天前的记录
        
    def _load_memory(self) -> Dict:
        """加载记忆数据"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "processed_candidates": {},  # 候选人ID -> 处理时间
                "screening_decisions": {},  # 候选人ID -> 决策历史
                "search_history": [],       # 搜索历史
                "stats": {
                    "total_processed": 0,
                    "total_passed": 0,
                    "total_rejected": 0
                }
            }
    
    def _save_memory(self):
        """保存记忆数据"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def should_process(self, candidate: CandidateCard) -> bool:
        """
        判断是否应该处理这个候选人
        
        规则：
        1. 从未处理过 → 处理
        2. 30天内处理过 → 不处理
        3. 30天前处理过 → 重新处理
        """
        candidate_id = candidate.get_fingerprint()
        
        if candidate_id not in self.memory["processed_candidates"]:
            return True
        
        last_processed = datetime.fromisoformat(
            self.memory["processed_candidates"][candidate_id]
        )
        days_passed = (datetime.now() - last_processed).days
        
        # 30天内处理过，跳过
        if days_passed < 30:
            logger.debug(f"候选人 {candidate.name} 在{days_passed}天前处理过，跳过")
            return False
        
        return True
    
    def record_processing(self, candidate: CandidateCard, decision: ScreeningDecision):
        """记录处理结果"""
        candidate_id = candidate.get_fingerprint()
        
        # 记录处理时间
        self.memory["processed_candidates"][candidate_id] = datetime.now().isoformat()
        
        # 记录决策历史
        if candidate_id not in self.memory["screening_decisions"]:
            self.memory["screening_decisions"][candidate_id] = []
        
        self.memory["screening_decisions"][candidate_id].append(decision.to_dict())
        
        # 更新统计
        if decision.result == ScreeningResult.PASS:
            self.memory["stats"]["total_passed"] += 1
        elif decision.result == ScreeningResult.REJECT:
            self.memory["stats"]["total_rejected"] += 1
        
        self.memory["stats"]["total_processed"] += 1
        
        # 定期清理
        self._cleanup_old_records()
        
        # 保存
        self._save_memory()
    
    def _cleanup_old_records(self):
        """清理过期记录"""
        cutoff_date = datetime.now() - timedelta(days=self.cleanup_days)
        
        # 清理processed_candidates
        to_remove = []
        for candidate_id, timestamp_str in self.memory["processed_candidates"].items():
            timestamp = datetime.fromisoformat(timestamp_str)
            if timestamp < cutoff_date:
                to_remove.append(candidate_id)
        
        for candidate_id in to_remove:
            del self.memory["processed_candidates"][candidate_id]
            if candidate_id in self.memory["screening_decisions"]:
                del self.memory["screening_decisions"][candidate_id]
        
        if to_remove:
            logger.info(f"清理了{len(to_remove)}条过期记录")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.memory["stats"]

# ==================== 双层初筛器 ====================

class DoubleScreener:
    """双层初筛器 - 严格/宽松规则"""
    
    def __init__(self, rules_config: Optional[Dict] = None):
        self.strict_rules = self._load_rules("strict", rules_config)
        self.loose_rules = self._load_rules("loose", rules_config)
        logger.info(f"加载规则: 严格{len(self.strict_rules)}条, 宽松{len(self.loose_rules)}条")
    
    def _load_rules(self, rule_type: str, config: Optional[Dict]) -> List[Dict]:
        """加载初筛规则"""
        # 默认规则（根据你的需求）
        default_rules = {
            "strict": [
                {
                    "name": "本科非985/QS100",
                    "condition": self._check_education_strict,
                    "action": ScreeningResult.REJECT,
                    "reason": "本科学校不符合要求（非985/非QS100）"
                },
                {
                    "name": "本科商科专业",
                    "condition": self._check_major_strict,
                    "action": ScreeningResult.REJECT,
                    "reason": "本科为商科专业（商业航天需要理工科）"
                },
                {
                    "name": "岗位明显不相关",
                    "condition": self._check_position_relevant,
                    "action": ScreeningResult.REJECT,
                    "reason": "当前职位与投资岗位不相关"
                },
                {
                    "name": "工作经验不足",
                    "condition": self._check_experience_strict,
                    "action": ScreeningResult.REJECT,
                    "reason": "相关工作经验不足3年"
                },
                {
                    "name": "地域不符合",
                    "condition": self._check_location_strict,
                    "action": ScreeningResult.REJECT,
                    "reason": "期望城市不包含目标城市"
                }
            ],
            "loose": [
                {
                    "name": "基础学历要求",
                    "condition": self._check_education_loose,
                    "action": ScreeningResult.PASS,
                    "reason": "满足基础学历要求（本科及以上）"
                },
                {
                    "name": "相关经验要求",
                    "condition": self._check_experience_loose,
                    "action": ScreeningResult.PASS,
                    "reason": "有一定相关经验"
                },
                {
                    "name": "地域宽松",
                    "condition": self._check_location_loose,
                    "action": ScreeningResult.PASS,
                    "reason": "地域要求可协商"
                },
                {
                    "name": "岗位相关性",
                    "condition": self._check_position_somewhat,
                    "action": ScreeningResult.NEED_DETAIL,
                    "reason": "需要查看详细简历判断岗位相关性"
                }
            ]
        }
        
        # 使用配置或默认规则
        if config and rule_type in config:
            return config[rule_type]
        return default_rules[rule_type]
    
    # ========== 严格规则条件函数 ==========
    
    def _check_education_strict(self, candidate: CandidateCard) -> bool:
        """严格教育背景检查：非985/QS100 → True（拒绝）"""
        education = candidate.education.lower()
        # 这里应该是复杂的学校判断逻辑
        # 简化：包含"985"或"qs"则通过
        return not ("985" in education or "qs" in education)
    
    def _check_major_strict(self, candidate: CandidateCard) -> bool:
        """严格专业检查：本科商科 → True（拒绝）"""
        education = candidate.education.lower()
        business_majors = ["金融", "经济", "会计", "工商管理", "mba", "business"]
        for major in business_majors:
            if major in education:
                return True
        return False
    
    def _check_position_relevant(self, candidate: CandidateCard) -> bool:
        """严格岗位相关性：完全不相关 → True（拒绝）"""
        position = candidate.current_position.lower()
        irrelevant = ["销售", "市场", "行政", "人事", "财务", "客服"]
        for word in irrelevant:
            if word in position:
                return True
        return False
    
    def _check_experience_strict(self, candidate: CandidateCard) -> bool:
        """严格经验检查：不足3年 → True（拒绝）"""
        exp_text = candidate.experience.lower()
        # 简单提取数字
        import re
        years = re.findall(r'\d+', exp_text)
        if years:
            return int(years[0]) < 3
        return True  # 无法判断时保守拒绝
    
    def _check_location_strict(self, candidate: CandidateCard) -> bool:
        """严格地域检查：不包含目标城市 → True（拒绝）"""
        # 这里需要知道目标城市，暂时返回False
        return False
    
    # ========== 宽松规则条件函数 ==========
    
    def _check_education_loose(self, candidate: CandidateCard) -> bool:
        """宽松教育检查：本科及以上 → True（通过）"""
        education = candidate.education.lower()
        return "本科" in education or "硕士" in education or "博士" in education
    
    def _check_experience_loose(self, candidate: CandidateCard) -> bool:
        """宽松经验检查：有经验 → True（通过）"""
        exp_text = candidate.experience.lower()
        return "年" in exp_text and "应届" not in exp_text
    
    def _check_location_loose(self, candidate: CandidateCard) -> bool:
        """宽松地域检查：可协商 → True（通过）"""
        return True  # 宽松模式下地域可协商
    
    def _check_position_somewhat(self, candidate: CandidateCard) -> bool:
        """宽松岗位检查：需要详情判断 → True（需要详情）"""
        position = candidate.current_position.lower()
        relevant = ["投资", "融资", "并购", "基金", "分析师", "经理", "总监"]
        for word in relevant:
            if word in position:
                return True
        return False
    
    def screen(self, candidate: CandidateCard, screening_type: ScreeningType) -> ScreeningDecision:
        """
        执行初筛
        
        Args:
            candidate: 候选人卡片
            screening_type: 筛选类型（严格/宽松）
        
        Returns:
            ScreeningDecision: 筛选决策
        """
        rules = self.strict_rules if screening_type == ScreeningType.STRICT else self.loose_rules
        
        applied_rules = []
        final_result = None
        final_reason = ""
        
        # 应用所有规则
        for rule in rules:
            condition_func = rule["condition"]
            if callable(condition_func) and condition_func(candidate):
                applied_rules.append(rule["name"])
                
                # 规则匹配，应用决策
                if final_result is None:
                    final_result = rule["action"]
                    final_reason = rule["reason"]
                elif rule["action"] == ScreeningResult.REJECT:
                    # 拒绝优先
                    final_result = ScreeningResult.REJECT
                    final_reason = rule["reason"]
        
        # 如果没有规则匹配，默认决策
        if final_result is None:
            if screening_type == ScreeningType.STRICT:
                final_result = ScreeningResult.REJECT
                final_reason = "严格模式下未匹配任何通过规则"
            else:
                final_result = ScreeningResult.NEED_DETAIL
                final_reason = "宽松模式下需要进一步判断"
        
        # 创建决策记录
        decision = ScreeningDecision(
            candidate_id=candidate.get_fingerprint(),
            candidate_name=candidate.name,
            screening_type=screening_type,
            result=final_result,
            reason=final_reason,
            rules_applied=applied_rules,
            timestamp=datetime.now()
        )
        
        logger.info(f"初筛完成: {candidate.name} -> {final_result.value} ({final_reason})")
        return decision

# ==================== 智能搜索器（模拟版） ====================

class SmartSearcher:
    """智能搜索器 - 猎聘平台适配（模拟版）"""
    
    def __init__(self, platform="liepin"):
        self.platform = platform
        self.session = None
        logger.info(f"初始化搜索器，平台: {platform}")
    
    def execute_search(self, strategy: SearchStrategy) -> List[CandidateCard]:
        """
        执行搜索（模拟版本）
        
        真实版本应该：
        1. 登录猎聘
        2. 构建搜索URL
        3. 发送HTTP请求
        4. 解析HTML响应
        5. 提取候选人卡片
        
        这里返回模拟数据用于测试
        """
        logger.info(f"执行搜索: {strategy.keywords} @ {strategy.filters.get('city', '未知')}")
        
        # 模拟搜索延迟
        time.sleep(0.5)
        
        # 生成模拟数据
        mock_candidates = self._generate_mock_candidates(strategy)
        
        logger.info(f"搜索完成，找到{len(mock_candidates)}个候选人")
        return mock_candidates
    
    def _generate_mock_candidates(self, strategy: SearchStrategy) -> List[CandidateCard]:
        """生成模拟候选人数据（用于测试）"""
        candidates = []
        
        # 示例数据
        mock_data = [
            {
                "name": "张AI",
                "position": "AI投资经理",
                "company": "深创投",
                "education": "清华大学硕士（计算机）",
                "experience": "5年投资经验",
                "location": "深圳",
                "expected": "深圳",
                "active": "3天内活跃"
            },
            {
                "name": "李商科",
                "position": "投资总监",
                "company": "某基金",
                "education": "北京大学本科（金融学）",  # 商科，应该被拒绝
                "experience": "8年投资经验",
                "location": "北京",
                "expected": "北京",
                "active": "1周内活跃"
            },
            {
                "name": "王理工",
                "position": "硬科技投资VP",
                "company": "红杉资本",
                "education": "上海交大本科（机械工程）",
                "experience": "6年投资经验",
                "location": "上海",
                "expected": "深圳,上海",
                "active": "今天活跃"
            },
            {
                "name": "赵销售",
                "position": "销售总监",  # 不相关岗位
                "company": "某科技公司",
                "education": "普通本科",
                "experience": "10年销售经验",
                "location": "广州",
                "expected": "广州",
                "active": "1月内活跃"
            },
            {
                "name": "刘应届",
                "position": "投资分析师",
                "company": "某券商",
                "education": "海外QS50硕士",
                "experience": "应届生",
                "location": "深圳",
                "expected": "深圳",
                "active": "今天活跃"
            }
        ]
        
        for i, data in enumerate(mock_data):
            candidate = CandidateCard(
                id=f"mock_{i}_{hashlib.md5(data['name'].encode()).hexdigest()[:8]}",
                name=data["name"],
                current_position=data["position"],
                current_company=data["company"],
                education=data["education"],
                experience=data["experience"],
                location=data["location"],
                expected_city=data["expected"],
                last_active=data["active"],
                source_url=f"https://www.liepin.com/candidate/mock_{i}",
                platform=self.platform,
                raw_data=data
            )
            candidates.append(candidate)
        
        return candidates

# ==================== 主Agent类 ====================

class ScoutAgent:
    """小蜜蜂Agent主类"""
    
    def __init__(self, use_model=False):
        """
        初始化小蜜蜂Agent
        
        Args:
            use_model: 是否使用大模型解析JD
        """
        logger.info("初始化小蜜蜂Agent...")
        
        # 初始化各模块
        self.jd_parser = JDParser(model_client=None)  # 暂时不用真实模型
        self.searcher = SmartSearcher(platform="liepin")
        self.screener = DoubleScreener()
        self.memory = CandidateMemory()
        
        # 运行统计
        self.stats = {
            "total_searches": 0,
            "total_candidates": 0,
            "passed_candidates": 0,
            "rejected_candidates": 0
        }
        
        logger.info("小蜜蜂Agent初始化完成")
    
    def process_jd(self, jd_text: str, screening_type: ScreeningType = ScreeningType.STRICT) -> Dict:
        """
        处理单个JD
        
        Args:
            jd_text: JD文本
            screening_type: 筛选类型
        
        Returns:
            处理结果
        """
        logger.info(f"开始处理JD，筛选类型: {screening_type.value}")
        
        try:
            # 1. JD解析
            strategy = self.jd_parser.parse_jd(jd_text)
            self.stats["total_searches"] += 1
            
            # 2. 执行搜索
            candidates = self.searcher.execute_search(strategy)
            self.stats["total_candidates"] += len(candidates)
            
            # 3. 初筛和去重
            passed_candidates = []
            decisions = []
            
            for candidate in candidates:
                # 检查是否需要处理
                if not self.memory.should_process(candidate):
                    continue
                
                # 执行初筛
                decision = self.screener.screen(candidate, screening_type)
                
                # 记录处理结果
                self.memory.record_processing(candidate, decision)
                
                # 统计
                if decision.result == ScreeningResult.PASS:
                    self.stats["passed_candidates"] += 1
                    passed_candidates.append({
                        "candidate": candidate.to_dict(),
                        "decision": decision.to_dict()
                    })
                elif decision.result == ScreeningResult.REJECT:
                    self.stats["rejected_candidates"] += 1
                
                decisions.append(decision.to_dict())
            
            # 4. 准备结果
            result = {
                "jd": jd_text,
                "search_strategy": strategy.to_dict(),
                "screening_type": screening_type.value,
                "total_candidates": len(candidates),
                "processed_candidates": len(decisions),
                "passed_candidates": len(passed_candidates),
                "passed_list": passed_candidates,
                "decisions": decisions,
                "stats": self.stats.copy(),
                "memory_stats": self.memory.get_stats(),
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"JD处理完成: 找到{len(passed_candidates)}个通过初筛的候选人")
            return result
            
        except Exception as e:
            logger.error(f"处理JD失败: {e}", exc_info=True)
            return {
                "jd": jd_text,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def daily_strict_screening(self, jd_texts: List[str]):
        """每日严格快筛"""
        logger.info("开始每日严格快筛...")
        results = []
        
        for jd_text in jd_texts:
            result = self.process_jd(jd_text, ScreeningType.STRICT)
            results.append(result)
        
        logger.info(f"严格快筛完成，处理了{len(jd_texts)}个JD")
        return results
    
    def daily_loose_screening(self, jd_texts: List[str]):
        """每日宽松快筛"""
        logger.info("开始每日宽松快筛...")
        results = []
        
        for jd_text in jd_texts:
            result = self.process_jd(jd_text, ScreeningType.LOOSE)
            results.append(result)
        
        logger.info(f"宽松快筛完成，处理了{len(jd_texts)}个JD")
        return results
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            "status": "running",
            "stats": self.stats,
            "memory_stats": self.memory.get_stats(),
            "timestamp": datetime.now().isoformat()
        }

# ==================== 使用示例 ====================

def main():
    """主函数 - 测试小蜜蜂Agent"""
    print("🧪 测试小蜜蜂Agent...")
    
    # 初始化Agent
    agent = ScoutAgent(use_model=False)
    
    # 测试JD
    test_jd = "寻找深圳的AI方向投资经理，3-5年经验，985/211优先，有硬科技投资经验"
    
    print(f"\n📋 测试JD: {test_jd}")
    print("=" * 60)
    
    # 测试严格快筛
    print("\n🔍 测试严格快筛模式...")
    strict_result = agent.process_jd(test_jd, ScreeningType.STRICT)
    
    if strict_result["success"]:
        print(f"✅ 严格快筛完成:")
        print(f"   总候选人: {strict_result['total_candidates']}")
        print(f"   处理候选人: {strict_result['processed_candidates']}")
        print(f"   通过初筛: {strict_result['passed_candidates']}")
        
        if strict_result['passed_candidates'] > 0:
            print("\n📋 通过候选人:")
            for candidate in strict_result['passed_list']:
                print(f"   - {candidate['candidate']['name']} ({candidate['candidate']['current_position']})")
                print(f"     教育: {candidate['candidate']['education']}")
                print(f"     公司: {candidate['candidate']['current_company']}")
                print(f"     决策原因: {candidate['decision']['reason']}")
    else:
        print(f"❌ 严格快筛失败: {strict_result['error']}")
    
    # 测试宽松快筛
    print("\n🔍 测试宽松快筛模式...")
    loose_result = agent.process_jd(test_jd, ScreeningType.LOOSE)
    
    if loose_result["success"]:
        print(f"✅ 宽松快筛完成:")
        print(f"   总候选人: {loose_result['total_candidates']}")
        print(f"   处理候选人: {loose_result['processed_candidates']}")
        print(f"   通过初筛: {loose_result['passed_candidates']}")
        
        # 显示宽松模式下新增的通过者
        strict_passed = {c['candidate']['id'] for c in strict_result.get('passed_list', [])}
        new_passed = []
        
        for candidate in loose_result['passed_list']:
            if candidate['candidate']['id'] not in strict_passed:
                new_passed.append(candidate)
        
        if new_passed:
            print(f"\n🎯 宽松模式新增通过: {len(new_passed)}人")
            for candidate in new_passed[:3]:  # 只显示前3个
                print(f"   - {candidate['candidate']['name']} ({candidate['decision']['reason']})")
    
    # 显示状态
    status = agent.get_status()
    print("\n📊 Agent状态:")
    print(f"   总搜索次数: {status['stats']['total_searches']}")
    print(f"   总候选人: {status['stats']['total_candidates']}")
    print(f"   通过候选人: {status['stats']['passed_candidates']}")
    print(f"   拒绝候选人: {status['stats']['rejected_candidates']}")
    
    print("\n🎉 小蜜蜂Agent测试完成!")

if __name__ == "__main__":
    main()