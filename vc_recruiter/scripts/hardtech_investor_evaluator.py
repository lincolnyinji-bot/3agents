#!/usr/bin/env python3
"""
泛硬科技投资人评估系统
基于28位真实候选人数据和专业标准
覆盖投资经理→总监全级别
"""

import csv
import re
import json
from datetime import datetime

print("="*80)
print("泛硬科技投资人评估系统 v2.0")
print("基于28位真实候选人数据和专业评估标准")
print("="*80)

class HardTechInvestorEvaluator:
    def __init__(self):
        # 加载配置
        self.config = {
            # 年龄基准：硕士25岁毕业
            'master_graduation_age': 25,
            
            # 产业经验折算系数
            'industry_experience_conversion': {
                '券商行研': 0.5,      # 5折折算
                '产业战略投资': 1.0,   # 同等折算
                '技术研发': 0.3,       # 3折折算
                '产品管理': 0.5,       # 5折折算
                '销售市场': 0.2        # 2折折算
            },
            
            # 案例参与度权重
            'deal_participation_weight': {
                '主导': 1.5,    # 项目挖掘→投成全流程
                '承做': 1.0,    # 执行已立项项目
                '参与': 0.5     # 协助部分工作
            },
            
            # 学校层级权重
            'school_tier_weight': {
                'T1': 1.2,  # 顶尖学校（北大、清华、牛津等）
                'T2': 1.0,  # 优秀学校（985/211/QS100）
                'T3': 0.8,  # 普通本科
                '其他': 0.6
            },
            
            # 专业类型权重（硬科技专项）
            'major_type_weight': {
                '核心硬科技': 1.2,  # 计算机、电子、AI等
                '工程类': 1.0,      # 机械、材料、能源等
                '商科': 0.8,        # 金融、经济、MBA
                '其他': 0.6
            },
            
            # 晋升时间标准（基于你的标准）
            'promotion_timeline': {
                '投资经理': {'min_exp': 0, 'max_exp': 2, 'typical_age_min': 25, 'typical_age_max': 28},
                '高级投资经理': {'min_exp': 2, 'max_exp': 4, 'typical_age_min': 28, 'typical_age_max': 30},
                'VP': {'min_exp': 3, 'max_exp': 6, 'typical_age_min': 30, 'typical_age_max': 35},
                '总监': {'min_exp': 5, 'max_exp': 10, 'typical_age_min': 35, 'typical_age_max': 40},
                'ED/MD': {'min_exp': 8, 'max_exp': 15, 'typical_age_min': 40, 'typical_age_max': 50}
            }
        }
        
        # 硬科技方向关键词
        self.hardtech_keywords = [
            'AI', '人工智能', '半导体', '芯片', '机器人', '量子', '航空航天',
            '新能源', '新材料', '智能制造', '自动驾驶', '生物医药', '硬科技',
            '算力', 'GPU', 'CPU', 'EDA', '光刻', '封装', '测试', '设备'
        ]
        
    def evaluate_candidate(self, candidate):
        """评估单个候选人"""
        result = {
            '姓名': candidate['姓名'],
            '基础信息': {},
            '评分详情': {},
            '级别评估': {},
            '专业判断': {},
            '推荐建议': []
        }
        
        # 1. 基础信息提取
        self._extract_basic_info(candidate, result)
        
        # 2. 核心评估模块
        self._assess_education(candidate, result)        # 学历评估
        self._assess_experience(candidate, result)       # 经验评估
        self._assess_deals(candidate, result)            # 案例评估
        self._assess_skills(candidate, result)           # 技能评估
        self._assess_salary(candidate, result)           # 薪资评估
        
        # 3. 综合评估
        self._assess_level(candidate, result)            # 级别评估
        self._check_consistency(candidate, result)       # 一致性检查
        self._make_recommendation(candidate, result)     # 推荐建议
        
        return result
    
    def _extract_basic_info(self, candidate, result):
        """提取基础信息"""
        result['基础信息'] = {
            '当前职位': candidate.get('当前职位', ''),
            '推断职位级别': candidate.get('推断职位级别', ''),
            '当前公司': candidate.get('当前公司', ''),
            'VC经验年数': float(candidate.get('VC投资经验年数', 0)),
            '总经验年数': float(candidate.get('总工作经验年数', 0)),
            '投成案例数': int(candidate.get('投成案例数', 0)),
            '推断年龄': candidate.get('推断年龄'),
            'STEM背景': candidate.get('STEM背景', '否'),
            '硬科技专业': candidate.get('硬科技相关专业', '否')
        }
    
    def _assess_education(self, candidate, result):
        """学历评估（0-40分）"""
        score = 0
        reasons = []
        
        # 学校层级评分
        bachelor_tier = candidate.get('本科学校层级', '其他')
        master_tier = candidate.get('硕士学校层级', '其他')
        
        # 本科学校 (15分)
        bachelor_weight = self.config['school_tier_weight'].get(bachelor_tier, 0.6)
        bachelor_score = 15 * bachelor_weight
        score += bachelor_score
        reasons.append(f"本科学校({bachelor_tier}): {bachelor_score:.1f}分")
        
        # 硕士学校 (20分)
        if master_tier != '其他':  # 有硕士学历
            master_weight = self.config['school_tier_weight'].get(master_tier, 0.6)
            master_score = 20 * master_weight
            score += master_score
            reasons.append(f"硕士学校({master_tier}): {master_score:.1f}分")
        
        # 专业匹配度 (5分)
        bachelor_major_type = candidate.get('本科专业类型', '其他')
        master_major_type = candidate.get('硕士专业类型', '其他')
        
        major_weight = max(
            self.config['major_type_weight'].get(bachelor_major_type, 0.6),
            self.config['major_type_weight'].get(master_major_type, 0.6)
        )
        major_score = 5 * major_weight
        score += major_score
        reasons.append(f"专业匹配度({bachelor_major_type}+{master_major_type}): {major_score:.1f}分")
        
        result['评分详情']['学历评估'] = {
            '得分': round(score, 1),
            '满分': 40,
            '详细原因': reasons
        }
    
    def _assess_experience(self, candidate, result):
        """经验评估（0-30分）"""
        score = 0
        reasons = []
        
        vc_exp = float(candidate.get('VC投资经验年数', 0))
        total_exp = float(candidate.get('总工作经验年数', 0))
        inferred_age = candidate.get('推断年龄')
        
        # VC经验评分 (15分)
        if vc_exp >= 8:
            vc_score = 15
            exp_level = "总监/ED级经验"
        elif vc_exp >= 5:
            vc_score = 12
            exp_level = "总监级经验"
        elif vc_exp >= 3:
            vc_score = 9
            exp_level = "VP级经验"
        elif vc_exp >= 1:
            vc_score = 6
            exp_level = "高级经理级经验"
        else:
            vc_score = 3
            exp_level = "入门级经验"
        
        score += vc_score
        reasons.append(f"VC经验{vc_exp}年({exp_level}): {vc_score}分")
        
        # 总工作经验加分 (5分)
        if total_exp >= 10:
            total_score = 5
            reasons.append(f"总经验{total_exp}年(资深): +5分")
        elif total_exp >= 5:
            total_score = 3
            reasons.append(f"总经验{total_exp}年(丰富): +3分")
        elif total_exp >= 2:
            total_score = 1
            reasons.append(f"总经验{total_exp}年(有经验): +1分")
        else:
            total_score = 0
        
        score += total_score
        
        # 年龄-经验匹配度检查 (5分)
        if inferred_age and inferred_age != 'None':
            try:
                age_num = float(inferred_age)
                expected_vc_exp = max(0, age_num - self.config['master_graduation_age'] - 2)
                # 减2年：硕士毕业+2年基础学习期
                
                if vc_exp >= expected_vc_exp:
                    match_score = 5
                    reasons.append(f"经验与年龄匹配良好: +5分")
                elif vc_exp >= expected_vc_exp - 1:
                    match_score = 3
                    reasons.append(f"经验略低于年龄预期: +3分")
                else:
                    match_score = 1
                    reasons.append(f"经验明显低于年龄预期: +1分")
                
                score += match_score
            except:
                pass
        
        # STEM背景加分 (5分)
        if candidate.get('STEM背景') == '是':
            stem_score = 5
            score += stem_score
            reasons.append(f"STEM背景: +5分")
        
        result['评分详情']['经验评估'] = {
            '得分': round(score, 1),
            '满分': 30,
            '详细原因': reasons
        }
    
    def _assess_deals(self, candidate, result):
        """案例评估（0-20分）"""
        score = 0
        reasons = []
        
        deal_count = int(candidate.get('投成案例数', 0))
        project_desc = candidate.get('项目经验描述', '')
        
        # 案例数量评分 (12分)
        if deal_count >= 10:
            deal_score = 12
            deal_level = "案例极其丰富"
        elif deal_count >= 5:
            deal_score = 9
            deal_level = "案例丰富"
        elif deal_count >= 3:
            deal_score = 6
            deal_level = "案例较好"
        elif deal_count >= 1:
            deal_score = 3
            deal_level = "有实操经验"
        else:
            deal_score = 0
            deal_level = "无投成案例"
        
        score += deal_score
        reasons.append(f"{deal_count}个案例({deal_level}): {deal_score}分")
        
        # 案例质量评估 (8分)
        quality_score = 0
        
        # 检查主导案例关键词
        lead_keywords = ['主导', '牵头', '独立挖掘', '独立推动', '全程负责']
        if any(keyword in project_desc for keyword in lead_keywords):
            quality_score += 4
            reasons.append("有主导案例: +4分")
        
        # 检查高价值案例关键词
        value_keywords = ['独角兽', '上市', 'IPO', 'IRR', '高回报', '退出']
        if any(keyword in project_desc for keyword in value_keywords):
            quality_score += 2
            reasons.append("有高价值案例: +2分")
        
        # 检查硬科技相关案例
        hardtech_match = any(keyword in project_desc for keyword in self.hardtech_keywords)
        if hardtech_match:
            quality_score += 2
            reasons.append("硬科技领域案例: +2分")
        
        score += quality_score
        
        result['评分详情']['案例评估'] = {
            '得分': round(score, 1),
            '满分': 20,
            '详细原因': reasons
        }
    
    def _assess_skills(self, candidate, result):
        """技能评估（0-10分）"""
        score = 5  # 基础投资技能分
        reasons = ["基础投资技能: 5分"]
        
        project_desc = candidate.get('项目经验描述', '').lower()
        position = candidate.get('当前职位', '').lower()
        
        # 硬科技专项技能
        tech_skills = ['技术尽调', '技术研判', '技术壁垒', '专利分析', '技术路线']
        if any(skill in project_desc for skill in tech_skills):
            score += 2
            reasons.append("硬科技技术评估能力: +2分")
        
        # 行业研究能力
        research_skills = ['行业研究', '行研', '市场分析', '竞品分析', '产业链']
        if any(skill in project_desc for skill in research_skills):
            score += 1
            reasons.append("行业研究能力: +1分")
        
        # 项目管理能力
        management_skills = ['项目管理', '团队管理', '带团队', '指导', '培养']
        if any(skill in project_desc for skill in management_skills):
            score += 1
            reasons.append("项目管理能力: +1分")
        
        # 募资/投后能力
        extra_skills = ['募资', '投后', '退出', 'LP', '投资者关系']
        if any(skill in project_desc for skill in extra_skills):
            score += 1
            reasons.append("募资/投后能力: +1分")
        
        result['评分详情']['技能评估'] = {
            '得分': min(10, score),
            '满分': 10,
            '详细原因': reasons
        }
    
    def _assess_salary(self, candidate, result):
        """薪资评估（0-10分）"""
        score = 8  # 基础合理性分
        reasons = ["薪资合理性基础分: 8分"]
        
        current_salary = candidate.get('当前年薪(万)')
        expected_salary = candidate.get('期望年薪(万)')
        
        if current_salary and expected_salary:
            increase_rate = (expected_salary - current_salary) / current_salary * 100
            
            if 0 <= increase_rate <= 30:
                score += 2
                reasons.append(f"期望涨幅合理({increase_rate:.0f}%): +2分")
            elif increase_rate > 30:
                reasons.append(f"期望涨幅偏高({increase_rate:.0f}%)")
        
        result['评分详情']['薪资评估'] = {
            '得分': min(10, score),
            '满分': 10,
            '详细原因': reasons
        }
    
    def _assess_level(self, candidate, result):
        """级别评估"""
        vc_exp = float(candidate.get('VC投资经验年数', 0))
        deal_count = int(candidate.get('投成案例数', 0))
        inferred_age = candidate.get('推断年龄')
        
        # 基于经验的级别
        if vc_exp >= 8 and deal_count >= 10:
            exp_based_level = "投资执行董事/董事总经理(ED/MD)"
        elif vc_exp >= 5 and deal_count >= 5:
            exp_based_level = "投资总监(Director)"
        elif vc_exp >= 3 and deal_count >= 3:
            exp_based_level = "投资副总裁(VP)"
        elif vc_exp >= 1 and deal_count >= 1:
            exp_based_level = "高级投资经理(Senior Associate)"
        else:
            exp_based_level = "投资分析师/投资经理(Analyst/Associate)"
        
        # 基于年龄的合理级别
        if inferred_age:
            if inferred_age >= 40:
                age_appropriate_level = "投资执行董事/董事总经理(ED/MD)"
            elif inferred_age >= 35:
                age_appropriate_level = "投资总监(Director)"
            elif inferred_age >= 30:
                age_appropriate_level = "投资副总裁(VP)"
            elif inferred_age >= 28:
                age_appropriate_level = "高级投资经理(Senior Associate)"
            else:
                age_appropriate_level = "投资分析师/投资经理(Analyst/Associate)"
        else:
            age_appropriate_level = "未知"
        
        result['级别评估'] = {
            '经验级别': exp_based_level,
            '年龄合理级别': age_appropriate_level,
            '当前职位级别': candidate.get('推断职位级别', '')
        }
    
    def _check_consistency(self, candidate, result):
        """一致性检查"""
        issues = []
        
        exp_level = result['级别评估']['经验级别']
        age_level = result['级别评估']['年龄合理级别']
        position_level = result['级别评估']['当前职位级别']
        
        # 经验 vs 年龄
        if '总监' in exp_level and '经理' in age_level:
            issues.append("经验达到总监级但年龄偏小，可能职位虚高")
        elif '经理' in exp_level and '总监' in age_level:
            issues.append("年龄达到总监级但经验不足，可能发展缓慢")
        
        # 职位 vs 经验
        if '总监' in position_level and '经理' in exp_level:
            issues.append("职位为总监但经验仅为经理级，可能职位虚高")
        elif '经理' in position_level and '总监' in exp_level:
            issues.append("经验达到总监级但职位为经理，可能被低估")
        
        result['专业判断']['一致性检查'] = issues if issues else ["级别匹配良好"]
    
    def _make_recommendation(self, candidate, result):
        """生成推荐建议"""
        total_score = sum(score['得分'] for score in result['评分详情'].values())
        exp_level = result['级别评估']['经验级别']
        
        recommendations = []
        
        # 基于总分
        if total_score >= 85:
            recommendations.append("✅ 强烈推荐：综合素质优秀")
        elif total_score >= 75:
            recommendations.append("✅ 推荐：符合要求")
        elif total_score >= 60:
            recommendations.append("⚠️ 可考虑面试：有一定风险")
        else:
            recommendations.append("❌ 暂不推荐：不符合基本要求")
        
        # 基于级别
        if '总监' in exp_level or 'ED' in exp_level:
            recommendations.append(f"💼 级别：{exp_level}，适合总监级岗位")
        elif 'VP' in exp_level:
            recommendations.append(f"💼 级别：{exp_level}，适合VP级岗位")
        elif '高级' in exp_level:
            recommendations.append(f"💼 级别：{exp_level}，适合高级经理岗位")
        
        # 硬科技专项
        if candidate.get('硬科技相关专业') == '是':
            recommendations.append("🔧 硬科技专业背景匹配")
        
        result['推荐建议'] = recommendations
        result['总分'] = round(total_score, 1)
        result['满分'] = 110  # 40+30+20+10+10

def main():
    print("\n加载标准化数据集...")
    
    # 读取数据
    data_file = '../data/hardtech_investors_standardized.csv'
    candidates = []
    
    with open(data_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append(row)
    
    print(f"共加载 {len(candidates)} 位泛硬科技投资人")
    
    # 初始化评估器
    evaluator = HardTechInvestorEvaluator()
    
    # 评估所有候选人
    results = []
    for candidate in candidates:
        print(f"\n{'='*60}")
        print(f"评估: {candidate['姓名']} ({candidate.get('推断职位级别', '未知')})")
        print(f"当前: {candidate['当前职位']} @ {candidate['当前公司']}")
        print('-'*60)
        
        result = evaluator.evaluate_candidate(candidate)
        results.append(result)
        
        # 显示评分摘要
        scores = result['评分详情']
        for category, score_info in scores.items():
            print(f"{category}: {score_info['得分']}/{score_info['满分']}")
        
        print(f"总分: {result['总分']}/110")
        
        # 显示级别评估
        level = result['级别评估']
        print(f"\n级别评估:")
        print(f"  经验级别: {level['经验级别']}")
        print(f"  年龄合理级别: {level['年龄合理级别']}")
        print(f"  当前职位级别: {level['当前职位级别']}")
        
        # 显示一致性检查
        issues = result['专业判断']['一致性检查']
        if issues and "级别匹配良好" not in issues:
            print(f"  注意: {'; '.join(issues)}")
        
        # 显示推荐建议
        print(f"\n推荐建议:")
        for rec in result['推荐建议']:
            print(f"  {rec}")
    
    # 汇总统计
    print("\n" + "="*80)
    print("28位泛硬科技投资人评估汇总")
    print("="*80)
    
    print(f"\n{'姓名':<6} {'VC经验':<6} {'案例':<6} {'总分':<6} {'经验级别':<25} {'推荐建议'}")
    print("-"*80)
    
    for result in results:
        name = result['姓名']
        vc_exp = result['基础信息']['VC经验年数']
        deals = result['基础信息']['投成案例数']
        total_score = result['总分']
        exp_level = result['级别评估']['经验级别']
        rec = result['推荐建议'][0] if result['推荐建议'] else ""
        
        print(f"{name:<6} {vc_exp:<6.1f} {deals:<6} {total_score:<6} {exp_level:<25} {rec[:20]}")
    
    # 级别分布统计
    print("\n" + "="*80)
    print("级别分布统计")
    print("="*80)
    
    level_counts = {}
    for result in results:
        level = result['级别评估']['经验级别']
        level_counts[level] = level_counts.get(level, 0) + 1
    
    for level, count in sorted(level_counts.items()):
        names = [r['姓名'] for r in results if r['级别评估']['经验级别'] == level]
        print(f"{level}: {count}人 - {', '.join(names)}")
    
    # 保存详细结果
    output_file = '../output/hardtech_evaluation_detailed.csv'
    fieldnames = ['姓名', '当前职位', 'VC经验年数', '投成案例数', '推断年龄',
                 '学历得分', '经验得分', '案例得分', '技能得分', '薪资得分',
                 '总分', '经验级别', '年龄合理级别', '一致性检查', '推荐建议']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                '姓名': result['姓名'],
                '当前职位': result['基础信息']['当前职位'],
                'VC经验年数': result['基础信息']['VC经验年数'],
                '投成案例数': result['基础信息']['投成案例数'],
                '推断年龄': result['基础信息']['推断年龄'],
                '学历得分': result['评分详情']['学历评估']['得分'],
                '经验得分': result['评分详情']['经验评估']['得分'],
                '案例得分': result['评分详情']['案例评估']['得分'],
                '技能得分': result['评分详情']['技能评估']['得分'],
                '薪资得分': result['评分详情']['薪资评估']['得分'],
                '总分': result['总分'],
                '经验级别': result['级别评估']['经验级别'],
                '年龄合理级别': result['级别评估']['年龄合理级别'],
                '一致性检查': '; '.join(result['专业判断']['一致性检查']),
                '推荐建议': ' | '.join(result['推荐建议'])
            })
    
    print(f"\n详细评估结果已保存至: {output_file}")
    
    print("\n" + "="*80)
    print("系统特点总结")
    print("="*80)
    print("""
1. 基于真实数据：28位泛硬科技投资人真实简历
2. 专业标准整合：你的职级划分、晋升时间、评估标准
3. 硬科技专项：STEM背景、技术理解深度、产业经验折算
4. 全面评估：学历、经验、案例、技能、薪资、一致性检查
5. 灵活适配：从投资经理到总监的全级别覆盖
    """)

if __name__ == "__main__":
    main()