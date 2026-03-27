#!/usr/bin/env python3
"""
优化后的Judge算法 V3
基于实际反馈优化：
1. 扩展方向识别：商业航天、低空经济、AI、机器人等
2. 优化潜力评估：AI方向潜力识别
3. 修正匹配逻辑：不再只看半导体/新材料
4. 泛硬科技识别：AI+制造、物联网+硬件等组合
"""

import re
from typing import Dict, List, Tuple


class OptimizedJudgeV3:
    """优化后的硬科技投资人评估算法"""
    
    # 方向配置
    DIRECTIONS = {
        "semiconductor": {
            "name": "半导体/新材料",
            "keywords": ['半导体', '芯片', '集成电路', '封装', '新材料', '复合材料', '纳米材料'],
            "weights": {"exp": 0.30, "insight": 0.25, "sourcing": 0.20, "edu": 0.15, "potential": 0.10}
        },
        "emerging_tech": {
            "name": "商业航天/低空经济", 
            "keywords": ['商业航天', '低空经济', '航空航天', '卫星', '无人机', 'eVTOL', '火箭', '飞行器'],
            "weights": {"exp": 0.28, "insight": 0.27, "sourcing": 0.20, "edu": 0.15, "potential": 0.10}
        },
        "ai_tech": {
            "name": "AI/人工智能",
            "keywords": ['AI', '人工智能', '大模型', '机器学习', '深度学习', '自然语言处理', '计算机视觉'],
            "weights": {"exp": 0.25, "insight": 0.30, "sourcing": 0.20, "edu": 0.15, "potential": 0.10}
        },
        "advanced_manufacturing": {
            "name": "先进制造/机器人",
            "keywords": ['先进制造', '智能制造', '工业4.0', '自动化', '机器人', '工业机器人', '增材制造'],
            "weights": {"exp": 0.28, "insight": 0.27, "sourcing": 0.20, "edu": 0.15, "potential": 0.10}
        },
        "broad_hard_tech": {
            "name": "泛硬科技综合",
            "keywords": ['新能源', '汽车电子', '智能驾驶', '5G', '物联网', '量子', '生物技术'],
            "weights": {"exp": 0.28, "insight": 0.27, "sourcing": 0.20, "edu": 0.15, "potential": 0.10}
        }
    }
    
    # 学历评分
    EDUCATION_SCORE = {
        "top":    15,    # 清北
        "c9":     14,    # C9 + 海外top50
        "985":    13,    # 985 + 海外top100  
        "211":    11,
        "other":  9,
    }
    
    def __init__(self, position_level: str = "IM"):
        """初始化
        position_level: IM | SIM | VP
        """
        self.level = position_level
        self.level_multiplier = {"IM": 1.0, "SIM": 1.1, "VP": 1.2}.get(position_level, 1.0)
    
    def analyze_resume(self, text: str, candidate_name: str = "") -> Dict:
        """分析简历"""
        # 1. 检测方向
        direction_info = self._detect_direction(text)
        
        # 2. 提取关键信息
        basic_info = self._extract_basic_info(text, candidate_name)
        
        # 3. 计算各维度分数
        dimension_scores = self._calculate_dimension_scores(basic_info, direction_info)
        
        # 4. 计算总分
        total_score = self._calculate_total_score(dimension_scores, direction_info)
        
        # 5. 生成推荐
        recommendation = self._generate_recommendation(total_score, basic_info, direction_info)
        
        return {
            "name": basic_info["name"],
            "direction": direction_info["name"],
            "detected_direction": direction_info["detected"],
            "total_score": round(total_score, 1),
            "recommendation": recommendation,
            "level": self.level,
            "dimension_scores": dimension_scores,
            "direction_keywords": direction_info["keyword_counts"],
            "basic_info": basic_info,
        }
    
    def _detect_direction(self, text: str) -> Dict:
        """检测候选人主要方向"""
        direction_scores = {}
        keyword_counts = {}
        
        # 计算各方向得分
        for dir_key, dir_info in self.DIRECTIONS.items():
            score = 0
            counts = {}
            for keyword in dir_info["keywords"]:
                count = text.lower().count(keyword.lower())
                if count > 0:
                    score += count * 3  # 关键词出现次数加权
                    counts[keyword] = count
            direction_scores[dir_key] = score
            keyword_counts[dir_key] = counts
        
        # 找到最高分方向
        if not direction_scores:
            main_direction = "broad_hard_tech"
        else:
            main_direction = max(direction_scores.items(), key=lambda x: x[1])[0]
        
        return {
            "key": main_direction,
            "name": self.DIRECTIONS[main_direction]["name"],
            "weights": self.DIRECTIONS[main_direction]["weights"],
            "score": direction_scores.get(main_direction, 0),
            "detected": direction_scores,
            "keyword_counts": keyword_counts.get(main_direction, {})
        }
    
    def _extract_basic_info(self, text: str, candidate_name: str) -> Dict:
        """提取基本信息"""
        # 姓名
        name_match = re.search(r'姓名[：:]\s*(\S+)', text)
        name = name_match.group(1) if name_match else candidate_name or "候选人"
        
        # 教育背景
        education_tier = "other"
        if any(kw in text for kw in ['清北', '清华', '北大']):
            education_tier = "top"
        elif any(kw in text for kw in ['C9', '985']):
            education_tier = "985"
        elif '211' in text:
            education_tier = "211"
        elif any(kw in text for kw in ['海外', 'QS', '常春藤']):
            education_tier = "c9"
        
        # 投资年限
        years_matches = re.findall(r'(\d+\.?\d*)\s*年', text)
        investment_years = 0
        if years_matches:
            for y in years_matches:
                try:
                    year_val = float(y)
                    if 1 <= year_val <= 20:
                        investment_years = max(investment_years, year_val)
                except:
                    pass
        
        # 项目数量
        project_count = 0
        for line in text.split('\n'):
            if '项目' in line or '案例' in line or '投资' in line:
                nums = re.findall(r'\d+', line)
                if nums:
                    for n in nums:
                        n_int = int(n)
                        if 1 <= n_int <= 50:
                            project_count += n_int
        
        # 机构背景识别
        # 头部VC
        big_institutions = ['高瓴', '红杉', 'IDG', 'GGV', '源码', '经纬', '启明', 
                           '华兴', '中信', '中金', '基石', '千乘', '歌斐', '华平']
        
        # 区域性VC
        regional_vc = ['深创投', '元禾', '上海科创', '浙江金控', '杭州高新', '苏州国发',
                      '广州金控', '粤科', '北京科创', '海河', '成都产投', '武汉光谷', '西安高新']
        
        # 产业CVC
        industry_cvc = ['华为哈勃', '小米长江', 'OPPO巡星', 'vivo投资', '比亚迪', '宁德时代',
                       '腾讯投资', '阿里战投', '字节战投', '美团龙珠', '京东战投',
                       '上汽投资', '吉利投资', '蔚来资本', '小鹏战投', '理想战投',
                       '复星医药', '华大基因', '药明康德', '迈瑞医疗',
                       '隆基投资', '通威投资', '金风投资', '恩捷投资']
        
        big_institution = any(inst in text for inst in big_institutions)
        regional_institution = any(inst in text for inst in regional_vc)
        industry_cvc_institution = any(inst in text for inst in industry_cvc)
        
        # 机构类型
        institution_type = "other"
        if industry_cvc_institution:
            institution_type = "industry_cvc"
        elif regional_institution:
            institution_type = "regional_vc"
        elif big_institution:
            institution_type = "big_vc"
        
        # 其他特征
        has_compound_background = '理工' in text and ('金融' in text or '经济' in text)
        has_exit_case = '退出' in text or '上市' in text or 'IPO' in text
        has_sourcing = 'sourcing' in text.lower() or '渠道' in text or '资源' in text
        has_tech_background = any(kw in text for kw in ['算法', '研发', '工程', '技术', '开发'])
        
        return {
            "name": name,
            "education_tier": education_tier,
            "investment_years": investment_years,
            "project_count": project_count,
            "big_institution": big_institution,
            "regional_institution": regional_institution,
            "industry_cvc_institution": industry_cvc_institution,
            "institution_type": institution_type,
            "has_compound_background": has_compound_background,
            "has_exit_case": has_exit_case,
            "has_sourcing": has_sourcing,
            "has_tech_background": has_tech_background,
            "text_length": len(text),
        }
    
    def _calculate_dimension_scores(self, info: Dict, direction_info: Dict) -> Dict:
        """计算各维度分数"""
        direction_key = direction_info["key"]
        
        # 1. 教育分 (满分15)
        edu_score = self.EDUCATION_SCORE.get(info["education_tier"], 9)
        if info["has_compound_background"]:
            edu_score = min(edu_score + 2, 15)
        
        # 2. 投资经验分 (满分30)
        exp_score = self._calculate_experience_score(info, direction_key)
        
        # 3. 行业理解分 (满分25)
        insight_score = self._calculate_insight_score(info, direction_info)
        
        # 4. 项目获取分 (满分20)
        sourcing_score = self._calculate_sourcing_score(info, direction_key)
        
        # 5. 成长潜力分 (满分10, VP不计)
        potential_score = 0 if self.level == "VP" else self._calculate_potential_score(info, direction_key)
        
        return {
            "education": edu_score,
            "investment_experience": exp_score,
            "industry_insight": insight_score,
            "project_sourcing": sourcing_score,
            "growth_potential": potential_score,
        }
    
    def _calculate_experience_score(self, info: Dict, direction: str) -> float:
        """计算投资经验分"""
        score = 0.0
        years = info["investment_years"]
        projects = info["project_count"]
        
        # 年限基础分 (0-12分)
        if years >= 8:   score += 12
        elif years >= 5: score += 10
        elif years >= 3: score += 8
        elif years >= 2: score += 6
        elif years >= 1: score += 4
        else:            score += 2
        
        # 项目经验分 (0-10分)
        if projects >= 20: score += 10
        elif projects >= 10: score += 8
        elif projects >= 5: score += 6
        elif projects >= 3: score += 4
        elif projects >= 1: score += 2
        
        # 退出案例加分 (0-3分)
        if info["has_exit_case"]:
            score += 3
        
        # 机构背书加分 (0-8分) - 修正规则：产业CVC ≥ 头部VC > 区域性VC
        if info["industry_cvc_institution"]:
            # 产业CVC：产业经验最相关，与头部VC同等或更高
            if self.level == "IM":
                score += 8  # 产业CVC最高分
            elif self.level == "SIM":
                score += 7
            else:
                score += 6
        elif info["big_institution"]:
            # 头部VC：全国性网络和品牌优势
            if self.level == "IM":
                score += 7  # 头部VC次高分
            elif self.level == "SIM":
                score += 6
            else:
                score += 5
        elif info["regional_institution"]:
            # 区域性VC：地域资源重要，但网络有限
            if self.level == "IM":
                score += 5  # 区域性VC基础分
            elif self.level == "SIM":
                score += 4
            else:
                score += 3
        
        # 方向特定调整
        if direction == "ai_tech" and info["has_tech_background"]:
            score += 2  # AI方向技术背景重要
        elif direction == "emerging_tech" and years < 2 and projects >= 3:
            score += 2  # 新兴方向经验少但项目多
        
        return min(score, 30)
    
    def _calculate_insight_score(self, info: Dict, direction_info: Dict) -> float:
        """计算行业理解分"""
        score = 0.0
        
        # 文本深度分 (0-8分)
        depth_score = min(info["text_length"] / 800, 8)  # 每800字1分，最多8分
        score += max(depth_score, 3)  # 至少3分
        
        # 关键词覆盖分 (0-10分)
        keyword_score = min(sum(direction_info["keyword_counts"].values()) * 2, 10)
        score += keyword_score
        
        # 方向匹配分 (0-7分)
        direction_score = min(direction_info["score"] / 5, 7)  # 每5分得1分，最多7分
        score += direction_score
        
        # 技术背景加分
        if info["has_tech_background"]:
            score += 2
        
        # 产业CVC行业深度加分
        if info["industry_cvc_institution"]:
            score += 3  # 产业CVC有深度行业理解
        
        return min(score, 25)
    
    def _calculate_sourcing_score(self, info: Dict, direction: str) -> float:
        """计算项目获取分"""
        score = 0.0
        
        # 项目数量分 (0-8分)
        if info["project_count"] >= 15: score += 8
        elif info["project_count"] >= 10: score += 6
        elif info["project_count"] >= 5: score += 4
        elif info["project_count"] >= 2: score += 2
        
        # 渠道能力分 (0-6分)
        if info["has_sourcing"]:
            score += 6
        else:
            score += 2  # 基础分
        
        # 网络质量分 (0-8分) - 修正规则：产业CVC ≥ 头部VC > 区域性VC
        if info["industry_cvc_institution"]:
            score += 8  # 产业CVC：最强产业网络
        elif info["big_institution"]:
            score += 7  # 头部VC：全国性网络优势
        elif info["regional_institution"]:
            score += 6  # 区域性VC：地域网络有限
        else:
            score += 3  # 基础分
        
        # AI方向技术网络加分
        if direction == "ai_tech" and info["has_tech_background"]:
            score += 2
        
        return min(score, 20)
    
    def _calculate_potential_score(self, info: Dict, direction: str) -> float:
        """计算潜力分"""
        score = 0.0
        
        # 年龄推断分 (0-4分)
        if info["investment_years"] <= 1:   score += 4  # 年轻有潜力
        elif info["investment_years"] <= 3: score += 3
        elif info["investment_years"] <= 5: score += 2
        else:                               score += 1
        
        # 学习能力分 (0-3分)
        if info["has_compound_background"]:
            score += 3
        elif info["has_tech_background"]:
            score += 2
        else:
            score += 1
        
        # 跨界能力分 (0-3分)
        feature_count = sum([info["has_compound_background"], info["has_tech_background"], 
                           info["has_sourcing"], info["big_institution"]])
        if feature_count >= 3:   score += 3
        elif feature_count >= 2: score += 2
        else:                    score += 1
        
        # 方向特定潜力
        if direction == "ai_tech":
            score += 2  # AI方向学习潜力大
        elif direction == "emerging_tech":
            score += 2  # 新兴方向成长空间大
        
        return min(score, 10)
    
    def _calculate_total_score(self, dimension_scores: Dict, direction_info: Dict) -> float:
        """计算总分"""
        weights = direction_info["weights"]
        
        # 各维度满分
        max_scores = {
            "education": 15,
            "investment_experience": 30,
            "industry_insight": 25,
            "project_sourcing": 20,
            "growth_potential": 10,
        }
        
        # 加权计算
        total = 0
        for dim in ["education", "investment_experience", "industry_insight", "project_sourcing", "growth_potential"]:
            if dim in dimension_scores:
                weight_key = {"education": "edu", "investment_experience": "exp", 
                            "industry_insight": "insight", "project_sourcing": "sourcing",
                            "growth_potential": "potential"}[dim]
                if weight_key in weights:
                    normalized = dimension_scores[dim] / max_scores[dim]
                    total += normalized * weights[weight_key]
        
        # 应用职级乘数
        total = total * 100 * self.level_multiplier
        
        return total
    
    def _generate_recommendation(self, score: float, info: Dict, direction_info: Dict) -> str:
        """生成推荐建议"""
        direction_name = direction_info["name"]
        
        # 检查硬条件
        has_experience = info["investment_years"] > 0 or info["project_count"] > 0
        has_education = info["education_tier"] in ["top", "c9", "985", "211"]
        
        if not has_experience:
            return "淘汰（无投资经验）"
        
        if not has_education and not (info["big_institution"] or info["regional_institution"] or info["industry_cvc_institution"]):
            return "淘汰（学历不足且无机构背书）"
        
        # 三桶分流
        if score >= 80:
            return f"强推（{direction_name}专家）"
        elif score >= 75:
            return f"推荐（{direction_name}方向）"
        elif score >= 70:
            if info["industry_cvc_institution"]:
                return "潜力（产业CVC背景）"
            elif info["big_institution"]:
                return "潜力（头部VC背书）"
            elif info["regional_institution"]:
                return "潜力（区域性VC背景）"
            else:
                return "潜力（可培养）"
        elif score >= 65:
            if direction_info["key"] in ["ai_tech", "emerging_tech"]:
                return "潜力（新兴方向）"
            else:
                return "待定（需进一步评估）"
        else:
            return "淘汰（综合评分不足）"


def test_with_real_cases():
    """用实际案例测试"""
    print("=" * 80)
    print("优化算法 V3 测试（基于实际反馈）")
    print("=" * 80)
    
