#!/usr/bin/env python3
"""
基于你提供的投资行业标准和11份简历进行深度分析
"""

import csv
import re
import json
from datetime import datetime

class VCCandidateAnalyzer:
    def __init__(self):
        # 加载学校数据
        with open('../data/schools.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.top_schools = set(data['985_universities'] + data['qs_top_100'])
        
        # 扩展专业列表（根据你的11份简历）
        self.stem_keywords = ['力学', '电子', '能源', '动力', '工程', '物理', '数学', '科学', 
                             '技术', '计算机', '软件', '硬件', '信息', '通信', '微电子', '自动化',
                             '航空航天', '材料', '化学', '生物', '机械', '土木', '建筑', '地质',
                             '应用力学', '理论与应用力学', '能源动力系统', '动力工程', '工程热物理',
                             '微电子学', '信息与计算科学', '信息工程', '电子与通信', '车辆工程',
                             '材料科学', '材料科学与工程', '先进材料', '力学', '数学与应用数学']
        
        self.business_keywords = ['金融', '经济', '工商管理', '财经', '传媒', '国际金融',
                                 '西方经济学', 'MBA', '金融MBA', '财经传媒', '经济师']
    
    def analyze_candidate(self, candidate):
        """分析单个候选人"""
        result = {
            'name': candidate['name'],
            'age': int(candidate['age'].replace('岁', '').replace('左右', '').strip()),
            'gender': candidate['gender'],
            'marital_status': candidate['marital_status'],
            'current_position': candidate['current_position'],
            'current_company': candidate['current_company'],
            'scores': {},
            'levels': {},
            'recommendation': ''
        }
        
        # 1. 学历分析
        edu_score, edu_reasons = self.score_education(candidate)
        result['scores']['education'] = edu_score
        result['edu_reasons'] = edu_reasons
        
        # 2. 经验分析（基于你提供的晋升标准）
        exp_score, exp_reasons, vc_years, deal_num = self.score_experience(candidate)
        result['scores']['experience'] = exp_score
        result['exp_reasons'] = exp_reasons
        result['vc_years'] = vc_years
        result['deal_num'] = deal_num
        
        # 3. 薪资分析
        salary_score, salary_reasons = self.score_salary(candidate)
        result['scores']['salary'] = salary_score
        result['salary_reasons'] = salary_reasons
        
        # 4. 技能分析
        skill_score, skill_reasons = self.score_skills(candidate)
        result['scores']['skill'] = skill_score
        result['skill_reasons'] = skill_reasons
        
        # 5. 案例专项
        case_score, case_reasons = self.score_cases(candidate)
        result['scores']['case'] = case_score
        result['case_reasons'] = case_reasons
        
        # 总分
        total_score = sum(result['scores'].values())
        result['scores']['total'] = total_score
        
        # 6. 级别评估（基于你的标准）
        level_assessment = self.assess_level(candidate, vc_years, deal_num, total_score)
        result['levels'] = level_assessment
        
        # 7. 推荐状态
        recommendation = self.make_recommendation(candidate, total_score, level_assessment)
        result['recommendation'] = recommendation
        
        return result
    
    def score_education(self, candidate):
        """学历评分 (0-40分)"""
        score = 0
        reasons = []
        
        # 学校评分 (20分)
        bachelor_school = candidate['bachelor_school']
        master_school = candidate['master_school']
        phd_school = candidate.get('phd_school', '')
        
        # 顶尖学校（北大、清华、牛津等）
        top_tier_schools = ['北京大学', '清华大学', '牛津大学', '剑桥大学', '斯坦福大学', '麻省理工']
        excellent_schools = ['上海交通大学', '复旦大学', '浙江大学', '南京大学', '华中科技大学', 
                           '中山大学', '华南理工大学', '香港中文大学', '加州大学', '宾夕法尼亚州立大学']
        
        # 本科学校
        if bachelor_school in top_tier_schools:
            score += 20
            reasons.append(f"顶尖本科学校({bachelor_school})(20分)")
        elif bachelor_school in excellent_schools or bachelor_school in self.top_schools:
            score += 15
            reasons.append(f"优秀本科学校({bachelor_school})(15分)")
        elif bachelor_school:
            score += 5
            reasons.append(f"普通本科学校({bachelor_school})(5分)")
        
        # 硕士学校
        if master_school in top_tier_schools:
            score += 20
            reasons.append(f"顶尖硕士学校({master_school})(20分)")
        elif master_school in excellent_schools or master_school in self.top_schools:
            score += 15
            reasons.append(f"优秀硕士学校({master_school})(15分)")
        elif master_school:
            score += 5
            reasons.append(f"普通硕士学校({master_school})(5分)")
        
        # 博士学校
        if phd_school in top_tier_schools:
            score += 10
            reasons.append(f"顶尖博士学校({phd_school})(10分)")
        elif phd_school:
            score += 5
            reasons.append(f"博士学校({phd_school})(5分)")
        
        # 专业匹配度 (20分)
        bachelor_major = candidate['bachelor_major']
        master_major = candidate['master_major']
        
        # 本科专业
        is_bachelor_stem = any(keyword in bachelor_major for keyword in self.stem_keywords)
        is_bachelor_business = any(keyword in bachelor_major for keyword in self.business_keywords)
        
        if is_bachelor_stem:
            score += 10
            reasons.append(f"本科理工科专业({bachelor_major})(10分)")
        elif is_bachelor_business:
            score += 5
            reasons.append(f"本科商科专业({bachelor_major})(5分)")
        else:
            score += 2
            reasons.append(f"本科其他专业({bachelor_major})(2分)")
        
        # 硕士专业
        is_master_stem = any(keyword in master_major for keyword in self.stem_keywords)
        is_master_business = any(keyword in master_major for keyword in self.business_keywords)
        
        if is_master_stem:
            score += 10
            reasons.append(f"硕士理工科专业({master_major})(10分)")
        elif is_master_business:
            score += 5
            reasons.append(f"硕士商科专业({master_major})(5分)")
        else:
            score += 2
            reasons.append(f"硕士其他专业({master_major})(2分)")
        
        # 博士专业
        if phd_school:
            phd_major = candidate.get('phd_major', '')
            if phd_major:
                score += 5
                reasons.append(f"博士专业({phd_major})(5分)")
        
        # 上限40分
        score = min(40, score)
        return score, reasons
    
    def score_experience(self, candidate):
        """经验评分 (0-30分) - 基于你的晋升标准"""
        score = 0
        reasons = []
        
        # 提取VC经验年数
        vc_exp = candidate['vc_experience']
        vc_years = self._extract_years(vc_exp)
        
        # 提取案例数
        deal_count = candidate['deal_count']
        deal_num = self._extract_deal_count(deal_count)
        
        # VC经验年数评分 (12分) - 基于硕士24岁毕业标准
        age = int(candidate['age'].replace('岁', '').replace('左右', '').strip())
        expected_years = max(0, age - 24)  # 硕士毕业算起
        
        # 实际经验与预期对比
        if vc_years >= 5:
            score += 12
            reasons.append(f"{vc_years}年VC经验，满足总监级要求(12分)")
        elif vc_years >= 3:
            score += 9
            reasons.append(f"{vc_years}年VC经验，满足VP级要求(9分)")
        elif vc_years >= 1:
            score += 6
            reasons.append(f"{vc_years}年VC经验，满足高级投资经理要求(6分)")
        elif vc_years > 0:
            score += 3
            reasons.append(f"{vc_years}年VC经验，入门级(3分)")
        
        # 投成案例评分 (15分)
        if deal_num >= 10:
            score += 15
            reasons.append(f"{deal_num}个投成案例，经验非常丰富(15分)")
        elif deal_num >= 5:
            score += 12
            reasons.append(f"{deal_num}个投成案例，经验丰富(12分)")
        elif deal_num >= 3:
            score += 8
            reasons.append(f"{deal_num}个投成案例，经验较好(8分)")
        elif deal_num >= 1:
            score += 5
            reasons.append(f"{deal_num}个投成案例，有实操经验(5分)")
        
        # 年龄与经验匹配度 (3分)
        if vc_years >= expected_years:
            score += 3
            reasons.append(f"经验与年龄匹配良好(+3分)")
        elif vc_years >= expected_years - 1:
            score += 1
            reasons.append(f"经验略低于年龄预期(+1分)")
        
        score = min(30, score)
        return score, reasons, vc_years, deal_num
    
    def score_salary(self, candidate):
        """薪资评分 (0-10分)"""
        score = 8  # 基础分
        reasons = ["薪资合理性基础分(8分)"]
        
        current_str = candidate['current_annual']
        expected_str = candidate['expected_annual']
        
        # 提取当前薪资
        current_match = re.search(r'(\d+)', str(current_str))
        if current_match:
            current = int(current_match.group(1))
            
            # 处理面议
            if '面议' in str(expected_str):
                # 根据职级推断合理期望
                position = candidate['current_position']
                if '总监' in position or 'VP' in position or 'ED' in position or 'MD' in position:
                    expected = int(current * 1.2)  # 20%涨幅
                    reasons.append(f"总监/VP级，期望面议推断合理涨幅20%({expected}万)")
                else:
                    expected = int(current * 1.3)  # 经理级30%涨幅
                    reasons.append(f"经理级，期望面议推断合理涨幅30%({expected}万)")
                
                score += 1  # 面议通常合理
                reasons.append("期望薪资面议，通常合理(+1分)")
            else:
                # 有具体期望值
                expected_match = re.search(r'(\d+)', str(expected_str))
                if expected_match:
                    expected = int(expected_match.group(1))
                    increase_rate = (expected - current) / current * 100 if current > 0 else 0
                    
                    if 0 <= increase_rate <= 30:
                        score += 2
                        reasons.append(f"期望涨幅合理({increase_rate:.0f}%)(+2分)")
                    elif 30 < increase_rate <= 50:
                        score += 1
                        reasons.append(f"期望涨幅偏高({increase_rate:.0f}%)(+1分)")
                    elif increase_rate > 50:
                        score -= 1
                        reasons.append(f"期望涨幅过高({increase_rate:.0f}%)(-1分)")
        
        score = min(10, max(0, score))
        return score, reasons
    
    def score_skills(self, candidate):
        """技能评分 (0-10分)"""
        score = 5  # 基础投资技能
        reasons = ["基础投资技能(5分)"]
        
        position = candidate['current_position']
        notes = candidate['notes']
        
        # 职级加分
        if '总监' in position or 'VP' in position:
            score += 2
            reasons.append("总监/VP级别技能(+2分)")
        elif '高级' in position or 'Senior' in position:
            score += 1
            reasons.append("高级职位技能(+1分)")
        
        # 特殊技能加分
        special_skills = ['硬科技', 'AI', '半导体', '机器人', '量子', '航空航天', '新能源', '汽车']
        if any(skill in notes for skill in special_skills):
            score += 2
            reasons.append("硬科技/AI领域专精(+2分)")
        
        # 海归/国际经验加分
        if '海归' in notes or '海外' in notes or '国际' in notes:
            score += 1
            reasons.append("国际视野/海归背景(+1分)")
        
        score = min(10, score)
        return score, reasons
    
    def score_cases(self, candidate):
        """案例专项评分 (0-10分)"""
        score = 0
        reasons = []
        
        deal_num = self._extract_deal_count(candidate['deal_count'])
        notes = candidate['notes']
        
        if deal_num >= 10:
            score = 10
            reasons.append(f"{deal_num}个投成案例，经验极其丰富(10分)")
        elif deal_num >= 5:
            score = 8
            reasons.append(f"{deal_num}个投成案例，经验丰富(8分)")
        elif deal_num >= 3:
            score = 6
            reasons.append(f"{deal_num}个投成案例，经验较好(6分)")
        elif deal_num >= 1:
            score = 4
            reasons.append(f"{deal_num}个投成案例，有实操经验(4分)")
        
        # 特殊案例加分（独角兽、上市等）
        if '独角兽' in notes or '上市' in notes or 'IPO' in notes:
            score = min(10, score + 2)
            reasons.append("有独角兽/上市案例加分(+2分)")
        
        return score, reasons
    
    def assess_level(self, candidate, vc_years, deal_num, total_score):
        """评估候选人级别 - 基于你的职级标准"""
        age = int(candidate['age'].replace('岁', '').replace('左右', '').strip())
        position = candidate['current_position']
        
        levels = {}
        
        # 1. 按经验和年龄评估（你的标准）
        # 硕士24岁毕业，2年SA(28+)，3年VP(30上下)，3-5年Director(35上下)
        expected_age_for_level = {
            '投资分析师/投资经理': 24-28,
            '高级投资经理': 28-30,
            '投资副总裁(VP)': 30-35,
            '投资总监(Director)': 35-40,
            '投资执行董事(ED)': 40-45,
            '投资董事总经理(MD)': 45+
        }
        
        # 实际级别推断
        if vc_years >= 8 and deal_num >= 10:
            levels['经验级别'] = '投资执行董事/董事总经理(ED/MD)级'
        elif vc_years >= 5 and deal_num >= 5:
            levels['经验级别'] = '投资总监(Director)级'
        elif vc_years >= 3 and deal_num >= 3:
            levels['经验级别'] = '投资副总裁(VP)级'
        elif vc_years >= 1 and deal_num >= 1:
            levels['经验级别'] = '高级投资经理(Senior Associate)级'
        else:
            levels['经验级别'] = '投资分析师/投资经理(Analyst/Associate)级'
        
        # 2. 按年龄评估
        if age >= 35:
            levels['年龄级别'] = '总监级年龄(35+)'
        elif age >= 30:
            levels['年龄级别'] = 'VP级年龄(30-35)'
        elif age >= 28:
            levels['年龄级别'] = '高级投资经理年龄(28-30)'
        else:
            levels['年龄级别'] = '投资经理年龄(<28)'
        
        # 3. 按职位名称评估
        position_lower = position.lower()
        if '总监' in position_lower or 'director' in position_lower:
            levels['职位级别'] = '总监级职位'
        elif 'vp' in position_lower or '副总裁' in position_lower:
            levels['职位级别'] = 'VP级职位'
        elif '高级' in position_lower or 'senior' in position_lower:
            levels['职位级别'] = '高级投资经理职位'
        elif '经理' in position_lower or 'manager' in position_lower:
            levels['职位级别'] = '投资经理职位'
        else:
            levels['职位级别'] = '其他职位'
        
        # 4. 综合评估
        # 检查级别一致性
        consistency_score = 0
        consistency_issues = []
        
        # 经验 vs 年龄
        if (levels['经验级别'] in ['投资总监(Director)级', '投资执行董事/董事总经理(ED/MD)级'] and 
            levels['年龄级别'] == '投资经理年龄(<28)'):
            consistency_issues.append("经验级别高但年龄偏小，可能职位虚高")
        elif (levels['经验级别'] == '投资分析师/投资经理(Analyst/Associate)级' and 
              levels['年龄级别'] == '总监级年龄(35+)'):
            consistency_issues.append("年龄偏大但经验级别低，可能发展缓慢")
        
        # 职位 vs 经验
        if (levels['职位级别'] == '总监级职位' and 
            levels['经验级别'] in ['投资分析师/投资经理(Analyst/Associate)级', '高级投资经理(Senior Associate)级']):
            consistency_issues.append("职位为总监但经验不足，可能职位虚高")
        
        levels['一致性检查'] = consistency_issues if consistency_issues else ["级别匹配良好"]
        
        return levels
    
    def make_recommendation(self, candidate, total_score, level_assessment):
        """生成推荐建议"""
        age = int(candidate['age'].replace('岁', '').replace('左右', '').strip())
        vc_years = level_assessment.get('vc_years', 0)
        deal_num = level_assessment.get('deal_num', 0)
        notes = candidate['notes']
        
        recommendation = []
        
        # 基于总分
        if total_score >= 85:
            recommendation.append("✅ 强烈推荐：综合素质优秀")
        elif total_score >= 75:
            recommendation.append("✅ 推荐：符合要求")
        elif total_score >= 60:
            recommendation.append("⚠️ 可考虑面试：有一定风险")
        else:
            recommendation.append("❌ 不推荐：不符合基本要求")
        
        # 基于级别一致性
        issues = level_assessment.get('一致性检查', [])
        if "级别匹配良好" not in issues:
            for issue in issues:
                recommendation.append(f"⚠️ {issue}")
        
        # 特殊备注
        if '硬条件好' in notes or '易获面试' in notes:
            recommendation.append("📝 备注：硬条件优秀，易获面试机会")
        if '沉淀有限' in notes or '宽而不深' in notes:
            recommendation.append("⚠️ 注意：工作内容宽泛，细分领域沉淀有限")
        if '培养' in notes:
            recommendation.append("🎯 建议：可作为培养对象，从高级投资经理开始")
        
        return recommendation
    
    def _extract_years(self, exp_str):
        """提取年数"""
        if not exp_str:
            return 0
        match = re.search(r'(\d+)', str(exp_str))
        return int(match.group(1)) if match else 0
    
    def _extract_deal_count(self, deal_str):
        """提取案例数"""
        if not deal_str:
            return 0
        match = re.search(r'(\d+)', str(deal_str))
        return int(match.group(1)) if match else 0

def main():
    print("="*80)
    print("11份面试级候选人深度分析报告")
    print("基于你提供的投资行业标准和晋升逻辑")
    print("="*80)
    
    # 读取数据
    candidates = []
    with open('../data/updated_assessment.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append(row)
    
    # 初始化分析器
    analyzer = VCCandidateAnalyzer()
    
    # 分析每个候选人
    results = []
    for candidate in candidates:
        print(f"\n{'='*60}")
        print(f"候选人: {candidate['name']} ({candidate['gender']}, {candidate['age']}岁)")
        print(f"当前职位: {candidate['current_position']} @ {candidate['current_company']}")
        print(f"标注: {candidate['notes']}")
        print('-'*60)
        
        result = analyzer.analyze_candidate(candidate)
        results.append(result)
        
        # 显示评分
        print("【评分详情】")
        scores = result['scores']
        print(f"学历: {scores.get('education', 0)}/40")
        print(f"经验: {scores.get('experience', 0)}/30")
        print(f"薪资: {scores.get('salary', 0)}/10")
        print(f"技能: {scores.get('skill', 0)}/10")
        print(f"案例: {scores.get('case', 0)}/10")
        print(f"总分: {scores.get('total', 0)}/100")
        
        # 显示级别评估
        print("\n【级别评估】")
        levels = result['levels']
        for key, value in levels.items():
            if isinstance(value, list):
                print(f"{key}: {', '.join(value)}")
            else:
                print(f"{key}: {value}")
        
        # 显示推荐建议
        print("\n【推荐建议】")
        for rec in result['recommendation']:
            print(rec)
    
    # 汇总统计
    print("\n" + "="*80)
    print("分析结果汇总")
    print("="*80)
    
    print(f"\n{'姓名':<6} {'年龄':<4} {'VC经验':<6} {'案例数':<6} {'总分':<6} {'经验级别':<20} {'一致性':<15}")
    print("-"*70)
    
    for result in results:
        name = result['name']
        age = result['age']
        vc_years = result.get('vc_years', 0)
        deal_num = result.get('deal_num', 0)
        total_score = result['scores'].get('total', 0)
        
        # 获取经验级别
        exp_level = result['levels'].get('经验级别', '')
        
        # 获取一致性
        consistency = result['levels'].get('一致性检查', [])
        if consistency and "级别匹配良好" not in consistency:
            consistency_status = "⚠️ 不一致"
        else:
            consistency_status = "✅ 一致"
        
        print(f"{name:<6} {age:<4} {vc_years:<6} {deal_num:<6} {total_score:<6} {exp_level:<20} {consistency_status:<15}")
    
    # 分类统计
    print("\n" + "="*80)
    print("分类统计")
    print("="*80)
    
    strong_recommend = sum(1 for r in results if r['scores'].get('total', 0) >= 85)
    recommend = sum(1 for r in results if 75 <= r['scores'].get('total', 0) < 85)
    consider_interview = sum(1 for r in results if 60 <= r['scores'].get('total', 0) < 75)
    not_recommend = sum(1 for r in results if r['scores'].get('total', 0) < 60)
    
    print(f"✅ 强烈推荐(≥85分): {strong_recommend}人")
    print(f"✅ 推荐(75-84分): {recommend}人")
    print(f"⚠️ 可考虑面试(60-74分): {consider_interview}人")
    print(f"❌ 不推荐(<60分): {not_recommend}人")
    
    # 按级别统计
    print("\n按经验级别统计:")
    level_counts = {}
    for result in results:
        level = result['levels'].get('经验级别', '')
        level_counts[level] = level_counts.get(level, 0) + 1
    
    for level, count in sorted(level_counts.items()):
        print(f"{level}: {count}人")
    
    # 保存详细结果
    output_file = '../output/detailed_analysis_11_candidates.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'age', 'gender', 'current_position', 'vc_years', 'deal_num',
                     'education_score', 'experience_score', 'salary_score', 'skill_score',
                     'case_score', 'total_score', 'experience_level', 'age_level',
                     'position_level', 'consistency_issues', 'recommendation']
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'name': result['name'],
                'age': result['age'],
                'gender': result['gender'],
                'current_position': result.get('current_position', ''),
                'vc_years': result.get('vc_years', 0),
                'deal_num': result.get('deal_num', 0),
                'education_score': result['scores'].get('education', 0),
                'experience_score': result['scores'].get('experience', 0),
                'salary_score': result['scores'].get('salary', 0),
                'skill_score': result['scores'].get('skill', 0),
                'case_score': result['scores'].get('case', 0),
                'total_score': result['scores'].get('total', 0),
                'experience_level': result['levels'].get('经验级别', ''),
                'age_level': result['levels'].get('年龄级别', ''),
                'position_level': result['levels'].get('职位级别', ''),
                'consistency_issues': '; '.join(result['levels'].get('一致性检查', [])),
                'recommendation': ' | '.join(result['recommendation'])
            })
    
    print(f"\n详细结果已保存至: {output_file}")
    print("="*80)

if __name__ == "__main__":
    main()