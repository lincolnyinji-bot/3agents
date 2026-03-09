#!/usr/bin/env python3
# VC投资经理简历筛选系统 - 增强版
# 支持年薪评估、案例数量评分、离职动机分析

import json
import csv
import re
from datetime import datetime
from typing import Dict, List, Tuple

class EnhancedResumeFilter:
    def __init__(self):
        """初始化增强版筛选器"""
        self.load_schools()
        self.threshold = 75  # 推荐阈值
        
        # 新增权重配置
        self.weights = {
            'education': 40,    # 学历
            'experience': 30,   # 经验
            'salary': 10,       # 薪资
            'skills': 10,       # 技能
            'cases': 10         # 案例数量（新增）
        }
    
    def load_schools(self):
        """加载学校数据库"""
        with open('../data/schools.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.top_schools = set(data['985_universities'] + data['qs_top_100'])
            self.stem_programs = set(data['理工科_programs'])
            self.business_programs = set(data['商科_programs'])
    
    def score_education(self, bachelor_school: str, bachelor_major: str,
                       master_school: str, master_major: str) -> Tuple[int, str]:
        """学历评分 (0-40分) - 增强版"""
        score = 0
        reasons = []
        
        # 1. 检查本科专业（硬性排除）
        if self._is_business_major(bachelor_major):
            return 0, "本科为商科专业，直接排除"
        
        # 2. 学校评分 (20分)
        bachelor_school_score = 20 if self._is_top_school(bachelor_school) else 0
        master_school_score = 20 if self._is_top_school(master_school) else 0
        school_score = min(20, (bachelor_school_score + master_school_score) / 2)
        score += school_score
        
        if school_score > 0:
            reasons.append(f"学校符合要求({school_score}分)")
        
        # 3. 本科专业评分 (10分)
        if self._is_stem_major(bachelor_major):
            score += 10
            reasons.append("本科理工科专业(10分)")
        elif bachelor_major:  # 其他专业
            score += 2
            reasons.append("本科非理工科专业(2分)")
        
        # 4. 硕士专业评分 (10分)
        master_major_lower = master_major.lower()
        if self._is_stem_major(master_major):
            score += 10
            reasons.append("硕士理工科专业(10分)")
        elif self._is_business_major(master_major):
            score += 5
            reasons.append("硕士商科专业(5分)")
        elif "国际金融" in master_major_lower or "金融" in master_major_lower or "经济" in master_major_lower:
            score += 5  # 国际金融是商科，不是"其他"
            reasons.append("硕士商科专业(国际金融)(5分)")
        elif master_major:  # 其他专业
            score += 2
            reasons.append("硕士其他专业(2分)")
        
        return min(self.weights['education'], score), "; ".join(reasons)
    
    def score_experience_enhanced(self, total_exp: str, vc_exp: str, 
                                 case_info: str, deal_count: str = "0",
                                 is_intern: bool = False, intern_months: str = "0") -> Tuple[int, str]:
        """
        增强版经验评分 (0-30分)
        包含应届生培养价值评估和实习深度识别
        """
        score = 0
        reasons = []
        
        # 提取工作经验年数
        total_years = self._extract_years(total_exp)
        vc_years = self._extract_years(vc_exp)
        
        # 检查是否为实习岗位或应届生
        intern_keywords = ["实习", "实习生", "intern", "trainee", "助理", "助理分析师"]
        is_intern_role = any(keyword in case_info.lower() for keyword in intern_keywords) or is_intern
        
        # 1. 应届生/实习生专项评估（看重培养价值）
        if is_intern_role or total_years == 0 or vc_years == 0:
            # 1.1 实习时长基础分
            try:
                months = int(intern_months) if intern_months.isdigit() else 0
                if months >= 12:
                    score += 10  # 12个月实习，显示坚持和深度
                    reasons.append(f"{months}个月长期实习显示坚持性(10分)")
                elif months >= 6:
                    score += 7   # 6个月以上，有足够学习周期
                    reasons.append(f"{months}个月实习经验(7分)")
                elif months >= 3:
                    score += 5   # 3个月基础实习
                    reasons.append(f"{months}个月实习经验(5分)")
            except:
                pass
            
            # 1.2 实习项目深度评估（秦琰案例：参与5个以上项目全流程）
            project_keywords = ["立项", "尽调", "尽职调查", "交割", "跟投", "过会", "全流程", "执行"]
            project_stages = []
            for keyword in project_keywords:
                if keyword in case_info:
                    project_stages.append(keyword)
            
            if len(project_stages) >= 3:  # 参与至少3个不同阶段
                score += 8
                reasons.append(f"参与{len(project_stages)}个项目阶段({','.join(project_stages)})(8分)")
            elif len(project_stages) >= 1:
                score += 5
                reasons.append(f"参与项目{project_stages[0]}阶段(5分)")
            
            # 1.3 具体项目成果识别
            if "完成跟投" in case_info or "跟投数千万" in case_info:
                score += 6
                reasons.append("完成跟投数千万显示实操能力(6分)")
            
            if "参与5个以上项目" in case_info or "5个以上项目" in case_info:
                score += 5
                reasons.append("参与多个项目显示广度(5分)")
            
            # 1.4 高质量实习机构加分，但同时检查专注度
            top_institutions = ["国投", "中金", "中信", "华泰", "招商", "红杉", "高瓴", "IDG", "腾讯", "阿里", 
                               "深创投", "GGV", "黑蚁", "和暄", "华为", "深创投"]
            
            # 统计顶级机构数量
            inst_count = sum(1 for inst in top_institutions if inst in case_info)
            
            if inst_count >= 1:
                if inst_count == 1:
                    score += 4  # 1家顶级机构，深度实习
                    reasons.append(f"1家顶级机构实习显示深度(4分)")
                elif inst_count == 2:
                    score += 3  # 2家机构，可能有合理轮换
                    reasons.append(f"{inst_count}家顶级机构实习(3分)")
                else:
                    score += 1  # 3+家机构，可能过于分散
                    reasons.append(f"{inst_count}家顶级机构但可能分散(1分)")
            
            # 1.5 检查实习分散度问题（杨子毅案例）
            # 关键词：多家、累计、等、分散
            dispersion_keywords = ["多家", "累计", "多个", "分散", "比较分散", "不同"]
            if any(keyword in case_info for keyword in dispersion_keywords) and inst_count >= 3:
                score -= 3  # 实习过于分散扣分
                reasons.append("实习机构过多可能分散注意力(-3分)")
            
            # 1.6 检查行业专注度（硬科技沉淀）
            hard_tech_keywords = ["半导体", "芯片", "AI", "人工智能", "硬科技", "高端制造", "设备", "材料"]
            hard_tech_count = sum(1 for keyword in hard_tech_keywords if keyword in case_info)
            
            if hard_tech_count >= 3:
                score += 3  # 明确硬科技方向
                reasons.append(f"专注{hard_tech_count}个硬科技方向(3分)")
            elif "硬科技" in case_info and hard_tech_count == 0:
                score -= 2  # 提到硬科技但无具体方向
                reasons.append("提到硬科技但无具体方向显示认知不足(-2分)")
        
        # 2. 正式投资经验评分（非应届生）
        else:
            if vc_years >= 1 and vc_years <= 5:
                score += min(15, vc_years * 3)  # 每多1年+3分，上限15分
                reasons.append(f"{vc_years}年VC经验({score}分)")
            elif vc_years == 0 and total_years > 0:
                # 如果没有明确投资经验年数，但从项目经验推断
                if any(keyword in case_info for keyword in ["投资", "投出", "尽职调查", "DD", "deal", "项目投资"]):
                    inferred_years = min(3, total_years)  # 推断最多3年
                    score += min(12, inferred_years * 4)  # 每多1年+4分
                    reasons.append(f"推断{inferred_years}年投资经验({score}分)")
        
        # 3. 投成案例数量评分 (15分)
        deal_num = self._extract_deal_count(deal_count)
        if deal_num >= 5:
            score += 15
            reasons.append(f"{deal_num}个投成案例(15分)")
        elif deal_num >= 3:
            score += 12
            reasons.append(f"{deal_num}个投成案例(12分)")
        elif deal_num >= 1:
            score += 8
            reasons.append(f"{deal_num}个投成案例(8分)")
        elif "投成" in case_info or "deal" in case_info.lower():
            score += 5
            reasons.append("有投成案例描述(5分)")
        else:
            reasons.append("无明确投成案例(0分)")
        
        # 4. 应届生培养潜力评估
        if (is_intern_role or total_years == 0) and score < 15:
            # 即使没有很多经验，但学历背景优秀有培养价值
            if "985" in case_info or "211" in case_info or "哈工大" in case_info or "计算机" in case_info:
                score += 5
                reasons.append("优秀学历背景显示培养潜力(5分)")
        
        return min(self.weights['experience'], score), "; ".join(reasons)
    
    def score_salary_annual(self, current_annual: str, expected_annual: str, 
                           position: str = "", vc_exp: str = "0", 
                           total_exp: str = "0", is_international: bool = False) -> Tuple[int, str]:
        """
        增强版年薪评分 (0-10分)
        根据工作经验、职位级别、海归背景等因素综合评估
        """
        score = 0
        reasons = []
        
        # 先提取工作经验年数
        vc_years = self._extract_years(vc_exp)
        total_years = self._extract_years(total_exp)
        
        # 提取年薪数字（单位：万），处理"面议"情况
        current_match = re.search(r'(\d+)', str(current_annual))
        
        current = int(current_match.group(1)) if current_match else 0
        
        # 处理"面议"情况
        expected_str = str(expected_annual).strip()
        if "面议" in expected_str or "面谈" in expected_str or expected_str == "":
            # 根据当前薪资和职位推断合理期望
            if current > 0:
                # 有当前薪资，期望合理涨幅为20-50%
                if vc_years <= 3:
                    expected = int(current * 1.3)  # 30%涨幅
                else:
                    expected = int(current * 1.2)  # 20%涨幅
                reasons.append(f"期望薪资面议，推断为{expected}万进行评分")
            else:
                # 无当前薪资，根据经验推断
                expected = 0
                reasons.append("期望薪资面议且无当前薪资参考(0分)")
        else:
            expected_match = re.search(r'(\d+)', expected_str)
            expected = int(expected_match.group(1)) if expected_match else 0
        
        # 1. 根据工作经验确定基准薪资范围
        # 应届生/初级（0-1年经验）：20-35万
        # 初级投资经理（1-2年）：25-45万
        # 投资经理（2-3年）：35-55万
        # 高级投资经理（3-5年）：50-80万
        # 投资副总裁（5+年）：70-120万
        
        # 确定经验级别
        if total_years == 0 and vc_years == 0:
            # 应届生/初级
            if 20 <= expected <= 35:
                score += 10
                reasons.append(f"应届生期望年薪{expected}万合理(10分)")
            elif expected < 20:
                score += 8
                reasons.append(f"应届生期望年薪{expected}万偏低(8分)")
            elif expected <= 40:
                score += 5
                reasons.append(f"应届生期望年薪{expected}万偏高但可谈判(5分)")
            else:
                score += 3
                reasons.append(f"应届生期望年薪{expected}万明显偏高(3分)")
        
        elif vc_years <= 1 and total_years <= 2:
            # 初级投资经理（1年以内经验）
            if 25 <= expected <= 45:
                score += 10
                reasons.append(f"初级投资经理期望年薪{expected}万合理(10分)")
            elif expected < 25:
                score += 7
                reasons.append(f"初级投资经理期望年薪{expected}万偏低(7分)")
            elif expected <= 50:
                score += 5
                reasons.append(f"初级投资经理期望年薪{expected}万偏高但可理解(5分)")
            else:
                score += 2
                reasons.append(f"初级投资经理期望年薪{expected}万明显偏高(2分)")
        
        elif vc_years <= 3:
            # 投资经理（2-3年经验）
            if 35 <= expected <= 55:
                score += 10
                reasons.append(f"投资经理期望年薪{expected}万合理(10分)")
            elif expected < 35:
                score += 7
                reasons.append(f"投资经理期望年薪{expected}万偏低(7分)")
            elif expected <= 65:
                score += 5
                reasons.append(f"投资经理期望年薪{expected}万偏高(5分)")
            else:
                score += 2
                reasons.append(f"投资经理期望年薪{expected}万明显偏高(2分)")
        
        else:
            # 高级职位
            senior_keywords = ["高级", "Senior", "VP", "副总裁", "总监", "Director"]
            is_senior = any(keyword in position for keyword in senior_keywords) if position else False
            
            if is_senior or vc_years >= 3:
                if 50 <= expected <= 100:
                    score += 10
                    reasons.append(f"高级职位期望年薪{expected}万合理(10分)")
                elif expected < 50:
                    score += 7
                    reasons.append(f"高级职位期望年薪{expected}万偏低(7分)")
                elif expected <= 120:
                    score += 5
                    reasons.append(f"高级职位期望年薪{expected}万偏高(5分)")
                else:
                    score += 2
                    reasons.append(f"高级职位期望年薪{expected}万明显偏高(2分)")
        
        # 2. 海归背景调整（根据你的洞察，不应过度溢价）
        if is_international:
            # 海归背景，但不大幅溢价（最多+1分）
            if score >= 5:  # 只有薪资合理时才给予小幅溢价
                score += 1
                reasons.append("海归背景小幅溢价(+1分)")
            else:
                reasons.append("海归背景但薪资不合理，不予溢价")
        
        # 3. 实习经验丰富度调整（秦琰案例）
        # 如果实习经验特别丰富，可适当上浮期望
        # 这个需要在外部逻辑中判断
        
        # 4. 当前薪资合理性检查
        if current > 0 and expected > 0:
            increase_rate = (expected - current) / current * 100
            if 15 <= increase_rate <= 40:
                score += 2  # 合理涨幅加分
                reasons.append(f"期望涨幅{increase_rate:.0f}%合理(+2分)")
            elif increase_rate > 60:
                score -= 1  # 过高涨幅扣分
                reasons.append(f"期望涨幅{increase_rate:.0f}%过高(-1分)")
        
        return min(self.weights['salary'], score), "; ".join(reasons)
    
    def score_cases(self, deal_count: str, case_info: str, 
                   target_industry: str = "AI/前沿科技") -> Tuple[int, str]:
        """
        案例数量专项评分 (0-10分)，考虑行业方向匹配度
        """
        score = 0
        reasons = []
        
        try:
            deal_num = int(deal_count) if deal_count.isdigit() else 0
            
            # 基础案例分（不考虑方向）
            if deal_num >= 5:
                score += 10
                reasons.append(f"{deal_num}个投成案例，经验丰富(10分)")
            elif deal_num >= 3:
                score += 8
                reasons.append(f"{deal_num}个投成案例，经验较好(8分)")
            elif deal_num >= 1:
                score += 5
                reasons.append(f"{deal_num}个投成案例，有实操经验(5分)")
            elif "投成" in case_info or "deal" in case_info.lower():
                score += 3
                reasons.append("有投成案例描述(3分)")
            else:
                score += 0
                reasons.append("无明确投成案例(0分)")
            
            # 行业方向匹配度调整（刘少雄问题：能源案例转AI方向）
            if deal_num > 0:
                industry_keywords = {
                    "AI/前沿科技": ["AI", "人工智能", "智能", "具身", "量子", "计算", "硬件", "半导体", "芯片"],
                    "新能源": ["能源", "动力", "电池", "储能", "光伏", "风电", "绿色", "燃料", "电动", "热物理"],
                    "半导体": ["半导体", "芯片", "集成电路", "封装", "材料", "设备", "传感器"],
                    "航空航天": ["航天", "航空", "飞行", "卫星", "无人机", "低空", "空间", "商业航天"]
                }
                
                target_keywords = industry_keywords.get(target_industry, [])
                other_industries = [k for k in industry_keywords.keys() if k != target_industry]
                
                # 检查案例描述中的行业关键词
                target_match = 0
                other_match = 0
                
                for keyword in target_keywords:
                    if keyword in case_info:
                        target_match += 1
                
                for industry in other_industries:
                    for keyword in industry_keywords[industry]:
                        if keyword in case_info:
                            other_match += 1
                
                if target_match == 0 and other_match > 0:
                    # 有案例但与目标行业不匹配（刘少雄情况）
                    score -= 3
                    reasons.append(f"但案例与目标行业{target_industry}不匹配(-3分)")
                elif target_match > 0 and other_match == 0:
                    # 案例与目标行业高度匹配
                    score += 1
                    reasons.append(f"案例与目标行业匹配(+1分)")
                elif target_match > 0 and other_match > 0:
                    # 混合案例，部分匹配
                    score += 0
                    reasons.append(f"部分案例匹配目标行业")
                    
        except:
            # 从文本推断
            deal_keywords = ["投成", "deal", "投资金额", "投出", "项目投资", "投资近", "主导", "参与投资"]
            if any(keyword in case_info for keyword in deal_keywords):
                score += 3
                reasons.append("文本提及投资案例(3分)")
            else:
                reasons.append("无投资案例信息(0分)")
        
        return min(self.weights['cases'], max(0, score)), "; ".join(reasons)
    
    def score_skills(self, resume_text: str, case_info: str = "", deal_count: str = "0",
                       position: str = "", project_desc: str = "",
                       is_intern: bool = False, total_years: str = "0",
                       bachelor_major: str = "", master_major: str = "") -> Tuple[int, str]:
        """
        增强版技能评分 (0-10分)
        基于项目经验、案例数量、职位等进行智能推断
        特别优化应届生实习技能识别
        """
        score = 0
        reasons = []
        
        # 1. 基础关键词匹配 (3分)
        base_skills = {
            "行研": 2, "行业研究": 2, "研究": 1, "行业分析": 2,
            "项目挖掘": 2, "项目获取": 2, "sourcing": 1, "项目开发": 1,
            "尽职调查": 2, "尽调": 2, "DD": 1, "due diligence": 1, "调查": 1,
            "交易执行": 2, "投后": 1, "post-investment": 1, "交易": 1, "执行": 1,
            "投资": 1, "股权": 1, "VC": 1, "风险投资": 1, "创业投资": 1
        }
        
        text_lower = resume_text.lower()
        for skill, points in base_skills.items():
            if skill in resume_text or skill.lower() in text_lower:
                score += points
                reasons.append(f"{skill}({points}分)")
        
        # 2. 基于案例数量的技能推断 (3分)
        try:
            deal_num = int(deal_count) if deal_count.isdigit() else 0
            if deal_num >= 3:
                score += 3
                reasons.append(f"{deal_num}个成功案例显示全面技能(3分)")
            elif deal_num >= 1:
                score += 2
                reasons.append(f"{deal_num}个成功案例显示实操能力(2分)")
            elif deal_num == 0 and "实习" in resume_text:
                # 实习生/应届生无案例，技能分上限控制
                if score > 7:
                    score = 7  # 无案例的实习生技能分不超过7
                    reasons.append("实习生无投成案例，技能分上限7分")
        except:
            pass
        
        # 3. 基于"主导"关键词的技能推断 (2分)
        if "主导" in case_info or "主导" in project_desc or "lead" in text_lower:
            score += 2
            reasons.append("主导项目经验显示全流程能力(2分)")
        
        # 4. 基于职位级别的技能推断 (2分)
        senior_keywords = ["高级", "Senior", "VP", "副总裁", "总监", "Director", "经理"]
        if any(keyword in position for keyword in senior_keywords):
            score += 2
            reasons.append("高级职位隐含全面技能要求(2分)")
        
        # 5. 基于详细项目描述的技能推断 (2分)
        if any(keyword in project_desc for keyword in ["尽调", "尽职调查", "交易", "谈判", "条款"]):
            score += 2
            reasons.append("项目描述显示具体投资技能(2分)")
        
        # 6. 专业影响力加分 (2分)
        if any(keyword in resume_text for keyword in ["书籍", "作者", "出版", "发起", "夜校", "生态"]):
            score += 2
            reasons.append("专业影响力显示深度认知(2分)")
        
        # 7. 应届生实习项目技能推断（秦琰案例）
        # 提取total_years
        try:
            total_years_num = int(total_years) if total_years.isdigit() else 0
        except:
            total_years_num = 0
        
        if (is_intern or total_years_num == 0) and score < 5:
            # 从实习描述中推断技能
            project_desc = resume_text + case_info + (project_desc or "")
            if any(keyword in project_desc for keyword in ["立项", "尽调", "交割", "跟投", "全流程", "参与5个"]):
                inferred_score = 6  # 参与多个项目全流程，至少6分
                if "完成跟投数千万" in project_desc:
                    inferred_score = 8  # 完成具体跟投，显示实操能力
                
                if score < inferred_score:
                    score = inferred_score
                    reasons.append(f"实习项目显示{inferred_score}分技能水平({inferred_score}分)")
        
        # 8. 确保最低技能分（有成功案例必有基本技能）
        if int(deal_count or 0) >= 1 and score < 5:
            score = 5
            reasons.append("有成功案例保证基本投资技能(5分)")
        
        # 限制总分
        score = min(self.weights['skills'], score)
        
        # 9. 方向转换时间沉淀评估（刘少雄问题）
        # 检查是否为跨行业转行且时间短
        target_industry_keywords = ["AI", "人工智能", "智能", "具身", "量子", "计算", "硬件", "半导体"]
        candidate_industry_keywords = []
        
        # 从专业推断原行业
        if "能源" in bachelor_major or "动力" in bachelor_major or "热物理" in master_major:
            candidate_industry_keywords.extend(["能源", "动力", "电池", "储能", "光伏"])
        
        # 10. 技术背景转投资评估（王宁案例）
        # 检查是否为技术背景转投资（无投成案例但有技术深度）
        tech_background_keywords = ["算法", "工程", "技术", "研发", "开发", "计算机", "软件", "硬件", "AI", "人工智能"]
        has_tech_background = any(keyword in bachelor_major or keyword in master_major for keyword in tech_background_keywords)
        
        if has_tech_background and deal_num == 0 and score < 8:
            # 技术背景转投资，即使无投成案例也有技术优势
            tech_experience_keywords = ["腾讯", "AI算法", "机器人", "技术", "研发", "产品", "市场", "交付"]
            tech_experience_count = sum(1 for keyword in tech_experience_keywords if keyword in resume_text)
            
            if tech_experience_count >= 3:
                score = 8  # 技术背景转投资，有深度技术经验
                reasons.append(f"技术背景转投资，{tech_experience_count}项技术经验显示深度认知(8分)")
        
        # 从案例描述推断目标行业接触时间
        time_keywords = ["近1年", "近一年", "最近1年", "近半年", "时间短", "沉淀不够", "不够"]
        target_industry_time = 0
        for keyword in time_keywords:
            if keyword in resume_text or keyword in case_info:
                target_industry_time = 1  # 短时间
        
        # 如果是跨行业转行且时间短，技能分上限控制
        if candidate_industry_keywords and target_industry_time == 1:
            # 检查是否有目标行业关键词
            target_match = sum(1 for keyword in target_industry_keywords if keyword in case_info)
            if target_match > 0:
                # 有目标行业经验但时间短
                if score > 7:
                    score = 7  # 跨行业短时间，技能分上限7分
                    reasons.append("跨行业转行时间短，技能深度有限(上限7分)")
        
        # 11. 潜力加分（胡真瀚案例：年轻有活力，有潜力）
        # 检查是否为年轻有潜力候选人
        if score < 9 and int(deal_count or 0) >= 1:
            potential_keywords = ["年轻", "活力", "潜力", "热情", "巨大潜力", "优秀投资人", "德扑", "聪明"]
            potential_count = sum(1 for keyword in potential_keywords if keyword in resume_text)
            
            if potential_count >= 2:
                score = min(self.weights['skills'], score + 2)
                reasons.append(f"年轻有潜力候选人(+2分)")
        
        # 12. 家境背景加分（胡真瀚案例：家庭条件好支持投资工作）
        family_keywords = ["家境", "殷实", "父辈", "当地知名", "政府", "支持", "无经济压力"]
        if any(keyword in resume_text for keyword in family_keywords):
            score = min(self.weights['skills'], score + 1)
            reasons.append(f"良好家庭背景支持投资工作(+1分)")
        
        # 13. 如果没有识别到任何技能，但案例数量显示有能力
        if score == 0 and int(deal_count or 0) >= 1:
            score = 6
            reasons = ["案例数量显示投资技能(6分)"]
        
        return min(self.weights['skills'], score), "; ".join(set(reasons)) if reasons else "需进一步评估技能(0分)"
    
    def evaluate_enhanced(self, resume: Dict) -> Dict:
        """增强版评估"""
        # 提取字段
        bachelor_school = resume.get('本科学历', '')
        bachelor_major = resume.get('本科专业', '')
        master_school = resume.get('硕士学历', '')
        master_major = resume.get('硕士专业', '')
        total_exp = resume.get('工作经验', '')
        vc_exp = resume.get('投资经验', '')
        position = resume.get('当前职位', '')
        current_annual = resume.get('当前年薪(万)', '0')
        expected_annual = resume.get('期望年薪(万)', '0')
        deal_count = resume.get('投成案例数', '0')
        case_info = resume.get('项目经验', '')
        resume_text = ' '.join([str(v) for v in resume.values()])
        
        # 各项评分
        edu_score, edu_reason = self.score_education(bachelor_school, bachelor_major,
                                                     master_school, master_major)
        
        # 判断是否为实习岗位
        intern_keywords = ["实习", "实习生", "intern", "trainee", "助理"]
        is_intern = any(keyword in position.lower() for keyword in intern_keywords)
        
        exp_score, exp_reason = self.score_experience_enhanced(total_exp, vc_exp, case_info, deal_count,
                                                              is_intern, resume.get('实习时长(月)', '0'))
        
        # 判断是否为海归背景
        international_keywords = ["帝国理工", "哥伦比亚", "哥大", "海外", "留学", "海归", "国际"]
        is_international = any(keyword in str(bachelor_school) + str(master_school) for keyword in international_keywords)
        
        salary_score, salary_reason = self.score_salary_annual(current_annual, expected_annual, position, 
                                                               vc_exp, total_exp, is_international)
        skill_score, skill_reason = self.score_skills(resume_text, case_info, deal_count, 
                                                      position, resume.get('项目经验', ''),
                                                      is_intern, total_exp,
                                                      bachelor_major, master_major)
        # 假设目标岗位是AI/前沿科技方向
        target_industry = "AI/前沿科技"
        case_score, case_reason = self.score_cases(deal_count, case_info, target_industry)
        
        # 计算顶级机构数量（用于边缘案例识别）
        top_institutions = ["国投", "中金", "中信", "华泰", "招商", "红杉", "高瓴", "IDG", "腾讯", "阿里", 
                           "深创投", "GGV", "黑蚁", "和暄", "华为"]
        inst_count = sum(1 for inst in top_institutions if inst in case_info)
        
        # 计算投成案例数
        try:
            deal_num = int(deal_count) if deal_count.isdigit() else 0
        except:
            deal_num = 0
        
        # 计算总年数
        total_years_num = self._extract_years(total_exp)
        
        # 总分（包含案例分）
        total_score = edu_score + exp_score + salary_score + skill_score + case_score
        
        # 推荐决策（三级分类）
        if total_score >= self.threshold:
            status = "推荐"
        elif total_score >= 50:  # 边缘案例：可以面试但有风险
            # 检查是否"漂亮简历但深度不足"（杨子毅类型）
            if (is_intern or total_years_num == 0) and inst_count >= 3 and deal_num == 0:
                status = "可面试（漂亮简历但有风险）"
            else:
                status = "可面试"
        else:
            status = "不推荐"
        
        # 级别评估
        level = self._assess_level(vc_exp, deal_count, position, total_exp, is_intern)
        
        return {
            **resume,
            '学历评分': edu_score,
            '经验评分': exp_score,
            '薪资评分': salary_score,
            '技能评分': skill_score,
            '案例评分': case_score,
            '总分': total_score,
            '评估级别': level,
            '推荐理由': f"学历:{edu_reason}; 经验:{exp_reason}; 薪资:{salary_reason}; 技能:{skill_reason}; 案例:{case_reason}",
            '状态': status,
            '操作时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def score_industry_match(self, bachelor_major: str, master_major: str, 
                           case_info: str, target_industry: str = "AI/前沿科技") -> Tuple[int, str]:
        """
        评估专业与目标行业的匹配度（0-10分）
        用于识别刘少雄类型的问题：能源背景转AI沉淀不足
        """
        score = 0
        reasons = []
        
        # 定义行业关键词映射
        industry_keywords = {
            "AI/前沿科技": ["AI", "人工智能", "智能", "机器学习", "深度学习", "算法", "数据科学", 
                          "计算机", "软件", "信息", "电子", "通信", "半导体", "芯片", "硬件"],
            "新能源": ["能源", "动力", "电动", "电池", "储能", "光伏", "风电", "清洁能源"],
            "医疗健康": ["医疗", "医药", "生物", "健康", "器械", "诊断", "基因"],
            "半导体": ["半导体", "芯片", "集成电路", "IC", "封装", "测试", "材料"],
            "航空航天": ["航天", "航空", "飞行", "卫星", "无人机", "低空", "空间"]
        }
        
        # 获取目标行业关键词
        target_keywords = industry_keywords.get(target_industry, [])
        
        # 检查专业背景匹配度
        all_majors = bachelor_major + " " + master_major
        major_match_count = 0
        
        for keyword in target_keywords:
            if keyword in all_majors:
                major_match_count += 1
        
        if major_match_count >= 2:
            score += 8
            reasons.append(f"专业背景与{target_industry}高度匹配(8分)")
        elif major_match_count >= 1:
            score += 4
            reasons.append(f"专业背景与{target_industry}部分匹配(4分)")
        else:
            score += 0
            reasons.append(f"专业背景与{target_industry}不匹配(0分)")
        
        # 检查项目经验匹配度
        case_match_count = 0
        for keyword in target_keywords:
            if keyword in case_info:
                case_match_count += 1
        
        if case_match_count >= 3:
            score += 2
            reasons.append(f"项目经验与{target_industry}深度匹配(2分)")
        elif case_match_count >= 1:
            score += 1
            reasons.append(f"项目经验与{target_industry}有接触(1分)")
        else:
            score += 0
            reasons.append(f"项目经验与{target_industry}无相关(0分)")
        
        # 特殊扣分：跨行业转行时间短（刘少雄类型）
        if major_match_count == 0 and case_match_count >= 1:
            # 专业不匹配但有相关经验，检查时间沉淀
            if "1年" in case_info or "近1年" in case_info or "时间短" in case_info:
                score -= 3
                reasons.append("跨行业转行时间短，沉淀不足(-3分)")
        
        return max(0, score), "; ".join(reasons)
    
    def _assess_level(self, vc_exp: str, deal_count: str, position: str, 
                      total_exp: str = "0", is_intern: bool = False) -> str:
        """评估候选人级别，考虑职位名称和综合条件"""
        vc_years = self._extract_years(vc_exp)
        total_years = self._extract_years(total_exp)
        deal_num = int(deal_count) if deal_count.isdigit() else 0
        
        # 从职位名称提取级别信息
        senior_keywords = ["VP", "副总裁", "总监", "Director", "高级总监", "合伙人", "Partner"]
        manager_keywords = ["经理", "Manager", "投资经理", "高级经理", "Senior"]
        analyst_keywords = ["分析师", "Analyst", "助理", "Associate"]
        
        # 检查职位名称中的级别关键词
        position_lower = position.lower() if position else ""
        is_senior_by_title = any(keyword.lower() in position_lower for keyword in senior_keywords)
        is_manager_by_title = any(keyword.lower() in position_lower for keyword in manager_keywords)
        is_analyst_by_title = any(keyword.lower() in position_lower for keyword in analyst_keywords)
        
        # 应届生/实习生特殊分级
        if is_intern or total_years == 0 or vc_years == 0:
            if deal_num >= 1 or vc_years >= 0.5:
                return "优秀应届生（推荐投资经理）"
            else:
                return "应届生/投资分析师"
        
        # 1. 总监级（需满足多项条件）
        if (vc_years >= 5 and deal_num >= 5) or is_senior_by_title:
            # 总监需要有足够的经验和案例支撑
            if vc_years >= 5 and deal_num >= 5:
                return "投资副总裁/总监"
            elif vc_years >= 3 and deal_num >= 5 and is_senior_by_title:
                return "投资副总裁/总监（经验稍短但案例多）"
            elif is_senior_by_title and deal_num >= 1 and vc_years >= 3:
                return "投资副总裁/总监（职位为总监但案例较少）"
            else:
                # 职位是总监但经验/案例不足，降级
                return "高级投资经理（职位为总监但经验不足）"
        
        # 2. 高级投资经理（3-5年经验或3+案例）
        if vc_years >= 3 or deal_num >= 3:
            # 但检查是否职位只是普通经理
            if is_manager_by_title and not is_senior_by_title:
                return "高级投资经理"
            else:
                return "高级投资经理/投资总监"
        
        # 3. 投资经理（1-3年经验或有案例）
        if vc_years >= 1 or deal_num >= 1:
            return "投资经理"
        
        # 4. 投资分析师（无投资经验）
        if is_analyst_by_title or vc_years == 0:
            return "投资分析师"
        
        # 默认
        return "投资经理"
    
    def _is_top_school(self, school: str) -> bool:
        """检查是否顶级学校"""
        if not school:
            return False
        return any(top in school for top in self.top_schools)
    
    def _is_stem_major(self, major: str) -> bool:
        """检查是否理工科专业（增强版）"""
        if not major:
            return False
        
        # 扩展理工科专业范围
        stem_keywords = ["工程", "技术", "科学", "物理", "化学", "生物", "数学", "统计", 
                        "计算机", "软件", "信息", "电子", "机械", "材料", "能源", "动力",
                        "自动化", "电气", "通信", "网络", "人工智能", "AI", "芯片", "半导体",
                        "封装", "制造", "航天", "航空", "船舶", "土木", "建筑", "环境"]
        
        # 排除明显的非理工科
        non_stem_keywords = ["管理", "经济", "金融", "会计", "贸易", "商务", "市场", "营销",
                            "语言", "文学", "历史", "哲学", "艺术", "设计", "教育", "法律"]
        
        # 检查是否包含非理工关键词（但某些复合专业如"财务管理"是双学位的一部分）
        major_lower = major.lower()
        
        # 电子封装技术、材料加工工程等明确是理工科
        if any(stem in major_lower for stem in stem_keywords):
            # 特殊处理双学位情况
            if "财务" in major_lower and "管理" in major_lower:
                # 如果是"电子封装技术+财务管理"，这是双学位，技术部分是理工科
                if "电子" in major_lower or "封装" in major_lower:
                    return True
                else:
                    return False
            return True
        
        return False
    
    def _is_business_major(self, major: str) -> bool:
        """检查是否商科专业"""
        if not major:
            return False
        return any(biz in major for biz in self.business_programs)
    
    def _extract_years(self, exp_str: str) -> int:
        """从经验字符串中提取年数，支持多种格式如'8年+'、'7年+', '10+年'等"""
        if not exp_str:
            return 0
        
        # 去除空白字符
        exp_str = exp_str.strip()
        
        # 处理"8年+"、"7年+"格式
        if '年+' in exp_str:
            match = re.search(r'(\d+)\s*年\+', exp_str)
            if match:
                return int(match.group(1))
        
        # 处理"10+年"格式
        if '+年' in exp_str:
            match = re.search(r'(\d+)\+\s*年', exp_str)
            if match:
                return int(match.group(1))
        
        # 处理标准"8年"、"10年"格式
        match = re.search(r'(\d+)\s*年', exp_str)
        if match:
            return int(match.group(1))
        
        # 如果还是没有匹配到，尝试提取数字
        match = re.search(r'(\d+)', exp_str)
        return int(match.group(1)) if match else 0
    
    def _extract_deal_count(self, deal_str: str) -> int:
        """从案例字符串中提取数字，支持'10+'、'5-7'等格式"""
        if not deal_str:
            return 0
        
        # 去除空白字符
        deal_str = deal_str.strip()
        
        # 处理"10+"格式
        if '+' in deal_str:
            match = re.search(r'(\d+)\+', deal_str)
            if match:
                return int(match.group(1))
        
        # 处理"5-7"格式，取最小值
        if '-' in deal_str:
            match = re.search(r'(\d+)\s*-\s*\d+', deal_str)
            if match:
                return int(match.group(1))
        
        # 处理纯数字
        match = re.search(r'(\d+)', deal_str)
        return int(match.group(1)) if match else 0

def main():
    """主函数"""
    print("=" * 70)
    print("VC投资经理简历筛选系统 - 增强版 v2.0")
    print("=" * 70)
    
    # 初始化筛选器
    filter = EnhancedResumeFilter()
    
    # 输入输出文件路径
    input_file = "../data/updated_assessment.csv"
    output_file = "../output/enhanced_evaluation.csv"
    
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"推荐阈值: {filter.threshold}分")
    print(f"权重配置: 学历{filter.weights['education']} + 经验{filter.weights['experience']} + "
          f"薪资{filter.weights['salary']} + 技能{filter.weights['skills']} + 案例{filter.weights['cases']}")
    print("-" * 70)
    
    try:
        candidates = []
        recommended = []
        
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                result = filter.evaluate_enhanced(row)
                candidates.append(result)
                if result['状态'] == '推荐':
                    recommended.append(result)
        
        # 保存完整结果
        if candidates:
            output_fields = list(candidates[0].keys())
            with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=output_fields)
                writer.writeheader()
                writer.writerows(candidates)
        
        # 保存推荐列表
        if recommended:
            rec_file = output_file.replace('.csv', '_recommended.csv')
            with open(rec_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=output_fields)
                writer.writeheader()
                writer.writerows(recommended)
        
        # 输出统计
        total = len(candidates)
        rec_count = len(recommended)
        
        print(f"处理完成！")
        print(f"总简历数: {total}")
        print(f"推荐人数: {rec_count}")
        print(f"推荐率: {rec_count/total*100:.1f}%" if total > 0 else "推荐率: N/A")
        
        # 输出推荐候选人摘要
        if recommended:
            print("\n" + "=" * 70)
            print("推荐候选人摘要:")
            print("-" * 70)
            for i, candidate in enumerate(recommended, 1):
                print(f"{i}. {candidate['姓名']} - {candidate['评估级别']} - 总分: {candidate['总分']}")
                print(f"   当前: {candidate.get('当前年薪(万)', 'N/A')}万 → 期望: {candidate.get('期望年薪(万)', 'N/A')}万")
                print(f"   案例: {candidate.get('投成案例数', '0')}个 | 经验: {candidate.get('投资经验', 'N/A')}")
                print()
        
        if rec_count > 0:
            rec_file = output_file.replace('.csv', '_recommended.csv')
            print(f"详细推荐列表已保存至: {rec_file}")
        
        print("=" * 70)
        
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_file}")
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()