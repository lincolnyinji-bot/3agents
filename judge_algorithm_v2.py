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

    # 潜力权重按级别（VP不计潜力，权重转移给投资经验）
    LEVEL_POTENTIAL = {"IM": 0.10, "SIM": 0.10, "VP": 0.00}
    LEVEL_EXP_BONUS = {"IM": 0.00, "SIM": 0.00, "VP": 0.10}

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

    def __init__(self, position_level: str = "IM"):
        """
        position_level: IM | SIM | VP
        """
        assert position_level in ("IM", "SIM", "VP")
        self.level = position_level
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

        return round(score * discount, 1)

    def _score_industry_insight(self, insight: Dict) -> float:
        """AI行业理解评分（满分25）"""
        score = 0.0
        # 技术深度（满10）：基础5分起
        score += max(min(insight.get("tech_depth", 5), 10), 5)
        # 覆盖广度（满8）：基础4分起
        coverage = max(min(insight.get("coverage_areas", 4), 8), 4)
        score += coverage
        # 公开影响力（满7）：基础2分起
        score += max(min(insight.get("public_influence", 0), 7), 0) + 2
        return round(min(score, 25), 1)

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
        """综合评估，返回评分报告"""
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
            "recommendation": self._recommend(weighted),
        }

    def _recommend(self, score: float) -> str:
        if score >= 88:   return "强推"
        elif score >= 80: return "推荐"
        elif score >= 70: return "可考虑"
        else:             return "不推荐"


# ─── 验证：用本次4位候选人测试 ────────────────────────────────────

def run_validation():
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
    ]

    levels = {"王谟松": "VP", "王梓兆": "SIM", "雷李澳洋": "SIM", "许元博": "IM"}

    print("=" * 60)
    print("Judge算法 V2 验证结果")
    print("=" * 60)
    results = []
    for c in candidates:
        judge = JudgeAlgorithmV2(position_level=levels[c["name"]])
        result = judge.evaluate(c)
        results.append(result)
        print(f"\n候选人: {result['name']} ({result['level']})")
        print(f"  综合得分: {result['total_score']}")
        print(f"  推荐结论: {result['recommendation']}")
        print(f"  各维度原始分: {result['raw_scores']}")

    print("\n" + "=" * 60)
    print("排名")
    results.sort(key=lambda x: x['total_score'], reverse=True)
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['name']} - {r['total_score']}分 - {r['recommendation']}")


if __name__ == "__main__":
    run_validation()
