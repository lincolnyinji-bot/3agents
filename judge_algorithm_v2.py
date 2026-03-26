#!/usr/bin/env python3
"""
Judge算法 V2 - 基于桢哥反馈优化的VC投资人评估算法
优化日期: 2026-03-25
核心优化：
1. 财务分析权重降为0（VC不需要）
2. 投资经验+行业理解+项目获取权重提升
3. 学历：C9=顶级985，理工本硕=理工本+金融硕
4. 主导项目隐含sourcing能力
5. 项目后续融资验证投资眼光
6. 国资机构背景折扣
7. 潜力权重按职级动态调整（VP不计潜力）
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from typing import Dict, List, Optional


class JudgeAlgorithmV2:
    """VC投资人评估算法 V2"""

    # 权重配置（基础，VP用）
    BASE_WEIGHTS = {
        "investment_experience": 0.30,
        "industry_insight":      0.25,
        "project_sourcing":      0.20,
        "education":             0.15,
        "growth_potential":      0.10,
    }

    # IM/SIM级别权重：行研↑ 投资经验↓（王梓兆被offer验证：行研可替代部分经验）
    IM_SIM_WEIGHTS = {
        "investment_experience": 0.23,  # 下调7%
        "industry_insight":      0.32,  # 上调7%
        "project_sourcing":      0.20,
        "education":             0.15,
        "growth_potential":      0.10,
    }

    # 潜力权重分层：IM=高(0.15)，SIM=中(0.10)，VP=0，权重从投资经验补偿
    LEVEL_POTENTIAL = {"IM": 0.15, "SIM": 0.10, "VP": 0.00}
    LEVEL_EXP_BONUS = {"IM": -0.05, "SIM": 0.00, "VP": 0.15}  # 从投资经验补偿

    # 学历分（满分15）
    EDUCATION_SCORE = {
        "top":   15,   # 清北
        "c9":    14,   # C9其他（含西交大）+ 海外top50
        "985":   13,   # 其他985 + 海外top100
        "211":   11,
        "other": 9,
    }

    # 机构市场化折扣
    INSTITUTION_DISCOUNT = {
        "market_vc":    1.00,   # 纯市场化VC
        "cvc":          0.95,   # 产业CVC
        "family_office":0.90,   # 家办
        "state_owned":  0.85,   # 国资/政策性机构
    }

    def __init__(self, position_level: str = "IM", jd_direction_match: float = 1.0):
        """
        position_level: IM | SIM | VP
        jd_direction_match: JD方向匹配度系数 (0.0-1.0)，默认1.0表示完全匹配
        """
        assert position_level in ("IM", "SIM", "VP")
        assert 0.0 <= jd_direction_match <= 1.0
        self.level = position_level
        self.jd_direction_match = jd_direction_match
        
        # VP用BASE_WEIGHTS，IM/SIM用行研增强权重
        if position_level == "VP":
            self.weights = dict(self.BASE_WEIGHTS)
        else:
            self.weights = dict(self.IM_SIM_WEIGHTS)
        # 调整潜力与经验权重
        pot_w = self.LEVEL_POTENTIAL[position_level]
        exp_bonus = self.LEVEL_EXP_BONUS[position_level]
        self.weights["growth_potential"]      = pot_w
        self.weights["investment_experience"] += exp_bonus

    # ─── 子评分方法 ────────────────────────────────────────────────

    def _score_education(self, edu: Dict) -> float:
        """学历评分（满分15）"""
        base = self.EDUCATION_SCORE.get(edu.get("tier", "other"), 9)
        # 复合背景加成（理工+金融/商科）
        if edu.get("compound_background", False):
            base = min(base + 1, 15)
        return base

    def _score_investment_experience(self, exp: Dict) -> float:
        """投资经验评分（满分30）"""
        score = 0.0
        years = exp.get("years", 0)
        lead_count = exp.get("lead_projects", 0)
        follow_count = exp.get("follow_projects", 0)
        validated = exp.get("validated_projects", 0)
        total = lead_count + follow_count
        institution_type = exp.get("institution_type", "market_vc")
        discount = self.INSTITUTION_DISCOUNT.get(institution_type, 1.0)
        
        # 大机构实习背书加分（红杉/GGV/深创投等）
        big_institution_bonus = 0
        if exp.get("big_institution_intern", False):
            # IM级别大机构实习+2~3分
            if self.level == "IM":
                big_institution_bonus = 2.5  # IM级别加2.5分
            elif self.level == "SIM":
                big_institution_bonus = 2.0  # SIM级别加2分
            else:
                big_institution_bonus = 1.5  # VP级别加1.5分

        # 年限基础分（满10）- 更宽松的曲线
        if years >= 5:   score += 10
        elif years >= 3: score += 9
        elif years >= 2: score += 7.5
        elif years >= 1: score += 6
        else:            score += 4

        # 项目数量与质量（满12）- 前台主导1个=2.5分，参与1个=1.2分
        proj_score = min(lead_count * 2.5 + follow_count * 1.2, 12)
        # 中台/受限背景主导折扣（非0，仍有参与价值）
        if exp.get("limited_authority", False):
            proj_score = proj_score * 0.75
        score += proj_score

        # 投资眼光验证（满8）：后续融资/退出验证
        if total > 0:
            validate_rate = validated / total
        else:
            validate_rate = 0.5  # 无记录按平均值
        # 基础分5分（即使无验证），验证率加成最高3分
        score += 5 + validate_rate * 3
        
        # 应用大机构实习加分
        score += big_institution_bonus

        return round(score * discount, 1)

    def _score_industry_insight(self, insight: Dict) -> float:
        """AI行业理解评分（满分25），应用JD方向匹配度系数"""
        score = 0.0
        # 技术深度（满10）：基础5分起
        score += max(min(insight.get("tech_depth", 5), 10), 5)
        # 覆盖广度（满8）：基础4分起
        coverage = max(min(insight.get("coverage_areas", 4), 8), 4)
        score += coverage
        # 公开影响力（满7）：基础2分起
        score += max(min(insight.get("public_influence", 0), 7), 0) + 2
        
        # 应用JD方向匹配度系数（卜亮源案例：方向匹配60%，行业理解分应压低）
        # 完全匹配=1.0，完全不匹配=0.0，部分匹配=0.6等
        direction_match_score = score * self.jd_direction_match
        
        return round(min(direction_match_score, 25), 1)

    def _score_project_sourcing(self, sourcing: Dict) -> float:
        """项目获取能力评分（满分20）"""
        score = 0.0
        # 主导项目隐含sourcing能力（满10）：基础3分
        lead = sourcing.get("lead_projects_sourced", 0)
        score += min(3 + lead * 1.8, 10)
        # 自建渠道（满6）：有渠道基础3分
        channels = sourcing.get("own_channels", 0)
        score += min(channels, 6) if channels > 0 else 2
        # 资源网络（满4）
        score += min(sourcing.get("network_quality", 2), 4)
        return round(min(score, 20), 1)

    def _score_growth_potential(self, potential: Dict) -> float:
        """成长潜力评分（满分10，VP不计）"""
        if self.level == "VP":
            return 0.0
        score = 0.0
        age = potential.get("age", 30)
        # 年龄越小潜力分越高
        if age <= 26:   score += 5
        elif age <= 28: score += 4
        elif age <= 30: score += 3
        else:           score += 2
        # 学习能力证明（竞赛/专利/论文等）
        score += min(potential.get("learning_proof", 0), 3)
        # 跨界能力
        score += min(potential.get("cross_domain", 0), 2)
        return round(score, 1)

    # ─── 主评估方法 ───────────────────────────────────────────────

    def evaluate(self, candidate: Dict) -> Dict:
        """综合评估，返回评分报告（两层架构：硬条件筛选+三桶分流）"""
        # 第一层：硬条件筛选
        if not self.hard_filter(candidate):
            return {
                "name":          candidate.get("name", ""),
                "level":         self.level,
                "total_score":   0,
                "raw_scores":    {},
                "weights":       self.weights,
                "recommendation": "淘汰（硬条件不满足）",
                "hard_filter_failed": True,
            }
        
        # 第二层：详细评分
        raw = {
            "education":             self._score_education(candidate.get("education", {})),
            "investment_experience": self._score_investment_experience(candidate.get("investment_experience", {})),
            "industry_insight":      self._score_industry_insight(candidate.get("industry_insight", {})),
            "project_sourcing":      self._score_project_sourcing(candidate.get("project_sourcing", {})),
            "growth_potential":      self._score_growth_potential(candidate.get("growth_potential", {})),
        }

        # 各维度满分
        max_scores = {
            "investment_experience": 30,
            "industry_insight":      25,
            "project_sourcing":      20,
            "education":             15,
            "growth_potential":      10,
        }

        # 行研补偿机制：行研极强（>21/25）且投资经验偏弱时，行研可部分补偿
        insight_rate = raw["industry_insight"] / max_scores["industry_insight"]
        exp_rate = raw["investment_experience"] / max_scores["investment_experience"]
        if insight_rate >= 0.84 and exp_rate < 0.70:
            compensation = (insight_rate - 0.84) * 0.5 * self.weights["investment_experience"]
            raw["industry_insight_compensation"] = round(compensation * 100, 1)
        else:
            compensation = 0
            raw["industry_insight_compensation"] = 0

        # 加权总分（转换为百分制）
        weighted = sum(
            (raw[k] / max_scores[k]) * self.weights[k]
            for k in max_scores
        ) * 100 + compensation * 100

        return {
            "name":          candidate.get("name", ""),
            "level":         self.level,
            "total_score":   round(weighted, 1),
            "raw_scores":    raw,
            "weights":       self.weights,
            "recommendation": self._recommend(weighted, candidate),
            "hard_filter_failed": False,
        }

    def hard_filter(self, candidate: Dict) -> bool:
        """硬条件筛选（第一层）
        返回True表示通过硬条件，False表示淘汰
        硬条件包括：
        1. 学历要求：硕士+985/海外名校
        2. 工作年限：IM≥1年，SIM≥2年，VP≥3年
        3. 投资相关经历：必须有（全职/实习）
        """
        # 1. 学历检查
        edu = candidate.get("education", {})
        edu_tier = edu.get("tier", "other")
        # 要求至少985或海外top100
        if edu_tier not in ["top", "c9", "985"]:
            return False
        
        # 2. 工作年限检查
        exp = candidate.get("investment_experience", {})
        years = exp.get("years", 0)
        min_years = {"IM": 1, "SIM": 2, "VP": 3}.get(self.level, 1)
        if years < min_years:
            return False
        
        # 3. 投资相关经历检查
        lead_count = exp.get("lead_projects", 0)
        follow_count = exp.get("follow_projects", 0)
        if years == 0 and (lead_count + follow_count) == 0:
            return False
        
        return True
    
    def _recommend(self, score: float, candidate: Dict = None) -> str:
        """三桶分流规则重写（根据桢哥确认规则）
        规则：
        1. 🟢推荐桶：≥75分（下限放宽，原80分）
        2. 🟡潜力桶：60-74分 + 必须有投资相关经历（全职/实习）
        3. 🔴淘汰：<60分或无投资相关经历
        4. 王梓兆类（行研强+经验受限）直接进推荐桶
        5. 大机构实习IM级别特殊考虑
        """
        if candidate is None:
            candidate = {}
        
        # 检查是否有投资相关经历
        has_investment_exp = False
        if candidate:
            exp = candidate.get("investment_experience", {})
            years = exp.get("years", 0)
            lead_count = exp.get("lead_projects", 0)
            follow_count = exp.get("follow_projects", 0)
            has_investment_exp = (years > 0) or (lead_count + follow_count > 0)
        
        # 检查是否为大机构实习背书（红杉/GGV/深创投等）
        is_big_institution_intern = False
        if candidate:
            exp = candidate.get("investment_experience", {})
            is_big_institution_intern = exp.get("big_institution_intern", False)
        
        # 检查是否为王梓兆类（行研极强+经验受限）
        is_wang_zizhao_type = False
        if candidate:
            insight = candidate.get("industry_insight", {})
            exp = candidate.get("investment_experience", {})
            insight_score = insight.get("tech_depth", 0) + insight.get("coverage_areas", 0) + insight.get("public_influence", 0)
            is_limited_authority = exp.get("limited_authority", False)
            # 行研极强（>21/25）且经验受限
            is_wang_zizhao_type = (insight_score >= 21) and is_limited_authority
        
        # 三桶分流逻辑（重写）
        if score >= 75:
            # 推荐桶下限放宽到75分
            if is_wang_zizhao_type:
                return "推荐桶（行研强补偿）"
            return "推荐桶"
        elif score >= 60 and has_investment_exp:
            # 潜力桶必须有投资相关经历
            if is_big_institution_intern and self.level == "IM":
                return "潜力桶（大机构背书）"
            return "潜力桶"
        elif score >= 58 and is_big_institution_intern and self.level == "IM":
            # 大机构实习IM级别放宽到58分
            return "潜力桶（大机构放宽）"
        else:
            return "淘汰桶"


# ─── 验证：用本次4位候选人测试 ────────────────────────────────────

def run_validation():
    # 原始4位候选人
    candidates = [
        {
            "name": "王谟松",
            "education": {"tier": "985", "compound_background": True},
            "investment_experience": {
                "years": 4.5, "lead_projects": 7, "follow_projects": 2,
                "validated_projects": 4, "institution_type": "market_vc"
            },
            "industry_insight": {"tech_depth": 10, "coverage_areas": 8, "public_influence": 7},
            "project_sourcing": {"lead_projects_sourced": 7, "own_channels": 6, "network_quality": 4},
            "growth_potential": {"age": 31, "learning_proof": 0, "cross_domain": 0},
        },
        {
            "name": "王梓兆",
            "education": {"tier": "c9", "compound_background": False},
            "investment_experience": {
                # 2年战投+2.5年战略=4.5年相关经验；过会2个+参与2个；中台受限
                "years": 2, "lead_projects": 2, "follow_projects": 2,
                "validated_projects": 1, "institution_type": "cvc",
                "limited_authority": True
            },
            # 行研极强：Roofline/QFD/等效算力模型，覆盖10+细分领域，个人主页输出
            "industry_insight": {"tech_depth": 9, "coverage_areas": 8, "public_influence": 4},
            # 自建渠道5个+，但主导sourcing受限
            "project_sourcing": {"lead_projects_sourced": 1, "own_channels": 5, "network_quality": 3},
            "growth_potential": {"age": 30, "learning_proof": 3, "cross_domain": 2},
        },
        {
            "name": "雷李澳洋",
            "education": {"tier": "c9", "compound_background": True},
            "investment_experience": {
                # 宁德8个月正式+3段实习；6个项目多个已立项/过投决
                "years": 2, "lead_projects": 4, "follow_projects": 2,
                "validated_projects": 2, "institution_type": "cvc"
            },
            # AI4S+Agent+机器人系统研究，联合AI Lab落地Dify
            "industry_insight": {"tech_depth": 8, "coverage_areas": 7, "public_influence": 2},
            "project_sourcing": {"lead_projects_sourced": 4, "own_channels": 4, "network_quality": 3},
            "growth_potential": {"age": 25, "learning_proof": 3, "cross_domain": 2},
        },
        {
            "name": "许元博",
            "education": {"tier": "top", "compound_background": True},
            "investment_experience": {
                # 力合2年+前海1年；投资案例多但国资折扣；腾讯算法研究员加分
                "years": 3, "lead_projects": 3, "follow_projects": 3,
                "validated_projects": 2, "institution_type": "state_owned"
            },
            # 腾讯算法背景扎实，但投资侧行业判断验证有限
            "industry_insight": {"tech_depth": 8, "coverage_areas": 6, "public_influence": 2},
            "project_sourcing": {"lead_projects_sourced": 3, "own_channels": 3, "network_quality": 3},
            "growth_potential": {"age": 28, "learning_proof": 3, "cross_domain": 2},
        },
        # 新增：大机构实习案例（杨子毅类）- 调整后更接近实际
        {
            "name": "杨子毅（模拟）",
            "education": {"tier": "c9", "compound_background": True},  # 从985升级到c9，增加复合背景
            "investment_experience": {
                "years": 1.0, "lead_projects": 0, "follow_projects": 2,  # 增加年限和项目
                "validated_projects": 0, "institution_type": "market_vc",
                "big_institution_intern": True  # 大机构实习标记
            },
            "industry_insight": {"tech_depth": 7, "coverage_areas": 6, "public_influence": 2},  # 提升行业理解
            "project_sourcing": {"lead_projects_sourced": 0, "own_channels": 2, "network_quality": 3},  # 提升资源
            "growth_potential": {"age": 24, "learning_proof": 3, "cross_domain": 2},  # 更年轻，潜力更高
        },
        # 新增：方向匹配度测试案例（卜亮源类）
        {
            "name": "卜亮源（模拟）",
            "education": {"tier": "c9", "compound_background": True},
            "investment_experience": {
                "years": 2, "lead_projects": 3, "follow_projects": 2,
                "validated_projects": 1, "institution_type": "market_vc"
            },
            "industry_insight": {"tech_depth": 7, "coverage_areas": 6, "public_influence": 2},
            "project_sourcing": {"lead_projects_sourced": 3, "own_channels": 3, "network_quality": 3},
            "growth_potential": {"age": 27, "learning_proof": 2, "cross_domain": 1},
        },
    ]

    levels = {
        "王谟松": "VP", "王梓兆": "SIM", "雷李澳洋": "SIM", 
        "许元博": "IM", "杨子毅（模拟）": "IM", "卜亮源（模拟）": "SIM"
    }

    print("=" * 60)
    print("Judge算法 V2 验证结果（含三桶分流+大机构背书+方向匹配度）")
    print("=" * 60)
    
    # 测试1：原始候选人（完全匹配）
    print("\n1. 原始候选人测试（JD方向匹配度=1.0）：")
    results1 = []
    for c in candidates[:4]:  # 原始4位
        judge = JudgeAlgorithmV2(position_level=levels[c["name"]], jd_direction_match=1.0)
        result = judge.evaluate(c)
        results1.append(result)
        print(f"  {result['name']} ({result['level']}): {result['total_score']}分 → {result['recommendation']}")
    
    # 测试2：大机构实习案例
    print("\n2. 大机构实习案例测试（杨子毅类）：")
    yang_candidate = candidates[4]
    judge = JudgeAlgorithmV2(position_level=levels[yang_candidate["name"]], jd_direction_match=1.0)
    yang_result = judge.evaluate(yang_candidate)
    print(f"  {yang_result['name']}: {yang_result['total_score']}分 → {yang_result['recommendation']}")
    print(f"  投资经验原始分: {yang_result['raw_scores']['investment_experience']}")
    
    # 测试3：方向匹配度测试（卜亮源案例，匹配度60%）
    print("\n3. JD方向匹配度测试（卜亮源案例，匹配度60%）：")
    bu_candidate = candidates[5]
    # 完全匹配
    judge_full = JudgeAlgorithmV2(position_level=levels[bu_candidate["name"]], jd_direction_match=1.0)
    result_full = judge_full.evaluate(bu_candidate)
    # 部分匹配（60%）
    judge_partial = JudgeAlgorithmV2(position_level=levels[bu_candidate["name"]], jd_direction_match=0.6)
    result_partial = judge_partial.evaluate(bu_candidate)
    
    print(f"  {result_full['name']} - 完全匹配(1.0): {result_full['total_score']}分 → {result_full['recommendation']}")
    print(f"  {result_partial['name']} - 部分匹配(0.6): {result_partial['total_score']}分 → {result_partial['recommendation']}")
    print(f"  行业理解分变化: {result_full['raw_scores']['industry_insight']} → {result_partial['raw_scores']['industry_insight']}")
    
    # 测试4：硬条件筛选测试
    print("\n4. 硬条件筛选测试：")
    hard_filter_cases = [
        {
            "name": "学历不足（211）",
            "education": {"tier": "211", "compound_background": True},
            "investment_experience": {"years": 2, "lead_projects": 2},
            "level": "IM"
        },
        {
            "name": "年限不足（IM需1年）",
            "education": {"tier": "985", "compound_background": True},
            "investment_experience": {"years": 0.5, "lead_projects": 0},
            "level": "IM"
        },
        {
            "name": "无投资经历",
            "education": {"tier": "c9", "compound_background": True},
            "investment_experience": {"years": 0, "lead_projects": 0, "follow_projects": 0},
            "level": "IM"
        },
        {
            "name": "通过筛选",
            "education": {"tier": "985", "compound_background": True},
            "investment_experience": {"years": 1.5, "lead_projects": 1},
            "level": "IM"
        },
    ]
    
    for case in hard_filter_cases:
        mock_candidate = {
            "name": case["name"],
            "education": case["education"],
            "investment_experience": case["investment_experience"],
            "industry_insight": {"tech_depth": 6, "coverage_areas": 5, "public_influence": 1},
            "project_sourcing": {"lead_projects_sourced": 1, "own_channels": 1, "network_quality": 2},
            "growth_potential": {"age": 26, "learning_proof": 1, "cross_domain": 1},
        }
        judge = JudgeAlgorithmV2(position_level=case["level"], jd_direction_match=1.0)
        result = judge.evaluate(mock_candidate)
        print(f"  {case['name']}: {result['recommendation']}")
    
    # 测试5：三桶分流规则验证（更新后）
    print("\n5. 三桶分流规则验证（推荐桶≥75分）：")
    test_cases = [
        {"name": "无经验高学历", "score": 65, "has_exp": False, "is_wang_type": False, "big_intern": False},
        {"name": "有经验潜力(72)", "score": 72, "has_exp": True, "is_wang_type": False, "big_intern": False},
        {"name": "有经验推荐(76)", "score": 76, "has_exp": True, "is_wang_type": False, "big_intern": False},
        {"name": "王梓兆类(75)", "score": 75, "has_exp": True, "is_wang_type": True, "big_intern": False},
        {"name": "大机构实习(68)", "score": 68, "has_exp": True, "is_wang_type": False, "big_intern": True},
        {"name": "大机构实习低分(59)", "score": 59, "has_exp": True, "is_wang_type": False, "big_intern": True},
        {"name": "高分推荐(85)", "score": 85, "has_exp": True, "is_wang_type": False, "big_intern": False},
        {"name": "低分淘汰(55)", "score": 55, "has_exp": True, "is_wang_type": False, "big_intern": False},
    ]
    
    for case in test_cases:
        mock_candidate = {
            "investment_experience": {
                "years": 2 if case["has_exp"] else 0,
                "lead_projects": 1 if case["has_exp"] else 0,
                "limited_authority": case["is_wang_type"],
                "big_institution_intern": case["big_intern"]
            },
            "industry_insight": {"tech_depth": 9 if case["is_wang_type"] else 6, "coverage_areas": 8, "public_influence": 4}
        }
        judge = JudgeAlgorithmV2(position_level="IM", jd_direction_match=1.0)
        # 模拟评分
        recommendation = judge._recommend(case["score"], mock_candidate)
        print(f"  {case['name']}: {case['score']}分 → {recommendation}")

    print("\n" + "=" * 60)
    print("原始4位候选人排名：")
    results1.sort(key=lambda x: x['total_score'], reverse=True)
    for i, r in enumerate(results1, 1):
        print(f"  {i}. {r['name']} - {r['total_score']}分 - {r['recommendation']}")


if __name__ == "__main__":
    run_validation()
