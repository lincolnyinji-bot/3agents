#!/usr/bin/env python3
"""
集成化泛硬科技投资人评估系统
基于28位候选人的完整专业评估
"""

import csv
import re
import json

print("="*80)
print("集成化泛硬科技投资人评估系统")
print("基于28位候选人的完整专业评估")
print("="*80)

class IntegratedHardTechEvaluator:
    def __init__(self):
        # 你的专业评估数据库（28人完整数据）
        self.professional_assessments = {
            # 第一批11人（已有标注）
            '聂彩明': {'level_range': '总监', 'notes': '顶级投资总监，北大工科+财经硕博，10+投成案例，大量跟投，carry数百万'},
            '符晓': {'level_range': '总监', 'notes': '顶级投资总监，清华能源本硕，9个投成案例（已上市1个），海外经验'},
            '胡独巍': {'level_range': 'VP-总监', 'notes': '优秀VP级，北大微电子本硕，4年券商行研+3年产业资本，案例2个主导投成'},
            '何远迪': {'level_range': 'ED', 'notes': '优秀ED级，本科一般（辽宁工业），港中文MBA，17个项目，华为8年+投资8年'},
            '施忠鑫': {'level_range': 'VP-总监', 'notes': '优秀VP级，华南理工+中山大学+UCSD金融MBA，工业机器人/半导体方向'},
            '李垚慰': {'level_range': 'VP', 'notes': '优秀VP级，美国宾大本硕，多个高IRR案例（63.7%-334%），产业生态圈建设'},
            '黄心宇': {'level_range': 'VP', 'notes': '总监够不上，VP也勉强，硬条件好易获面试，难通过1面，北大材料本博，6案例'},
            '李世清': {'level_range': 'VP', 'notes': '汽车方向不错VP，前沿科技不合格，重庆大学汽车工程，5案例，产业+投资复合背景'},
            '竺笛': {'level_range': 'VP-总监', 'notes': '优秀VP级（对标VP/SA），华科数学+上交金融硕，6案例，AI专家，年轻有活力'},
            '姜玮常': {'level_range': '总监-ED', 'notes': '优秀总监级，川大计算机本科，20+案例，硬科技投资经验丰富，穿越多个周期'},
            '黄靖岚': {'level_range': 'SA-VP', 'notes': '易获面试但不一定通过，硬条件好但沉淀有限，牛津数学硕，工作内容宽泛'},
            
            # 第二批17人（刚刚补充）
            '何方仪': {'level_range': 'SA', 'notes': '优秀SA人选'},
            '刘少雄': {'level_range': 'SA-VP', 'notes': '勉强可以拿到面试机会的人选，针对专业方向（新能源投资）有拿到offer可能，针对不熟悉的领域（具身智能、量子通信等）经验尚浅，offer概率40%'},
            '刘皓天': {'level_range': '投资经理', 'notes': '优秀的投资经理候选人'},
            '孙培峰': {'level_range': '投资经理', 'notes': '顶尖的投资经理候选人'},
            '宁兆辉': {'level_range': 'VP', 'notes': '优秀的VP级候选人'},
            '徐帅': {'level_range': 'SA', 'notes': '优秀的SA级候选人'},
            '李义': {'level_range': 'D-ED', 'notes': '优秀的D或ED候选人'},
            '李新亮': {'level_range': 'D', 'notes': '优秀的D级候选人'},
            '王宁': {'level_range': 'SA', 'notes': '优秀的SA级候选人'},
            '王磊': {'level_range': 'ED+', 'notes': '适合ED或以上的候选人'},
            '王谟松': {'level_range': 'VP', 'notes': '优秀的VP级候选人'},
            '秦琰': {'level_range': '投资经理', 'notes': '优秀的投资经理候选人'},
            '胡真瀚': {'level_range': '投资经理-SA', 'notes': '优秀的投资经理或SA级候选人'},
            '赖宏坤': {'level_range': 'VP-D', 'notes': '优秀的VP或D级候选人'},
            '钱亚声': {'level_range': 'SA', 'notes': '优秀的SA级候选人'},
            '黄大庆': {'level_range': '投资经理', 'notes': '优秀的投资经理级候选人'},
            '黄润聪': {'level_range': 'SA', 'notes': '优秀的SA级候选人'}
        }
        
        # 级别映射（用于计算级别差距）
        self.level_hierarchy = {
            '投资分析实习生': 1,
            '投资分析师': 2,
            '投资经理': 3,
            '高级投资经理': 4,
            'SA': 5,           # Senior Associate
            'VP': 6,           # Vice President
            'D': 7,            # Director
            '总监': 7,         # Director (中文)
            'ED': 8,           # Executive Director
            '合伙人': 9,
            'ED+': 10          # ED及以上
        }
        
        # 硬科技行业分类
        self.hardtech_sectors = {
            'AI': ['AI', '人工智能', '机器学习', '深度学习', '大模型', '生成式AI'],
            '半导体': ['半导体', '芯片', '集成电路', 'IC', 'EDA', '封装', '测试'],
            '机器人': ['机器人', '具身智能', '工业机器人', '服务机器人', '自动化'],
            '新能源': ['新能源', '储能', '光伏', '风电', '氢能', '锂电池', '宁德时代'],
            '量子': ['量子', '量子计算', '量子通信', '量子科技'],
            '航空航天': ['航空航天', '低空经济', '无人机', 'eVTOL', '卫星'],
            '新材料': ['新材料', '先进材料', '复合材料', '纳米材料'],
            '智能制造': ['智能制造', '工业4.0', '数字化工厂', '工业互联网']
        }
        
        # 关键评分权重（根据你的评估调整）
        self.scoring_weights = {
            '学历': 0.25,      # 学校层级、专业匹配度
            '经验': 0.35,      # VC经验、总经验、产业经验折算
            '案例': 0.25,      # 数量、质量、主导程度
            '潜力': 0.15       # 年龄、成长性、可塑性
        }
    
    def parse_level_range(self, level_str):
        """解析级别范围字符串，如'VP-总监'"""
        if '-' in level_str:
            parts = level_str.split('-')
            return [part.strip() for part in parts]
        else:
            return [level_str.strip()]
    
    def calculate_level_score(self, level):
        """计算级别分数（用于比较）"""
        return self.level_hierarchy.get(level, 0)
    
    def get_level_range_score(self, level_range):
        """获取级别范围的最小和最大分数"""
        levels = self.parse_level_range(level_range)
        scores = [self.calculate_level_score(lvl) for lvl in levels if lvl in self.level_hierarchy]
        return min(scores) if scores else 0, max(scores) if scores else 0
    
    def assess_industry_match(self, candidate, target_industries=None):
        """评估行业匹配度（硬科技专项）"""
        project_desc = candidate.get('项目经验描述', '')
        position = candidate.get('当前职位', '')
        company = candidate.get('当前公司', '')
        
        industry_scores = {}
        
        for sector, keywords in self.hardtech_sectors.items():
            match_count = sum(1 for kw in keywords if kw in project_desc or kw in position or kw in company)
            if match_count > 0:
                industry_scores[sector] = min(match_count * 2, 10)  # 每个关键词2分，最多10分
        
        return industry_scores
    
    def evaluate_candidate(self, candidate, target_position=None, target_industries=None):
        """评估单个候选人（集成化评估）"""
        name = candidate['姓名']
        
        # 基础信息
        result = {
            '姓名': name,
            '基础信息': {
                '当前职位': candidate.get('当前职位', ''),
                '当前公司': candidate.get('当前公司', ''),
                'VC经验年数': float(candidate.get('VC投资经验年数', 0)),
                '投成案例数': int(candidate.get('投成案例数', 0)),
                '总经验年数': float(candidate.get('总工作经验年数', 0)),
                '推断年龄': candidate.get('推断年龄'),
                'STEM背景': candidate.get('STEM背景', '否'),
                '硬科技专业': candidate.get('硬科技相关专业', '否')
            },
            '专业评估': self.professional_assessments.get(name, {}),
            '评估结果': {}
        }
        
        # 1. 级别评估
        self._assess_level(candidate, result)
        
        # 2. 行业匹配度评估
        if target_industries:
            industry_scores = self.assess_industry_match(candidate, target_industries)
            result['评估结果']['行业匹配度'] = industry_scores
        
        # 3. 案例深度评估
        self._assess_case_depth(candidate, result)
        
        # 4. 综合评分
        self._calculate_composite_score(candidate, result)
        
        # 5. 猎头实操建议
        self._generate_recruiter_recommendations(candidate, result)
        
        return result
    
    def _assess_level(self, candidate, result):
        """级别评估（核心）"""
        name = candidate['姓名']
        vc_exp = float(candidate.get('VC投资经验年数', 0))
        deal_count = int(candidate.get('投成案例数', 0))
        
        # 基于经验数据的级别推断
        if vc_exp >= 10 and deal_count >= 10:
            system_level = 'D-ED'
        elif vc_exp >= 5 and deal_count >= 5:
            system_level = 'VP-D'
        elif vc_exp >= 3 and deal_count >= 3:
            system_level = 'SA-VP'
        elif vc_exp >= 1 and deal_count >= 1:
            system_level = '投资经理-SA'
        else:
            system_level = '投资分析实习生-投资经理'
        
        # 专业评估的级别范围
        pro_assessment = result['专业评估']
        pro_level_range = pro_assessment.get('level_range', '未知')
        
        # 计算匹配度
        system_min, system_max = self.get_level_range_score(system_level)
        pro_min, pro_max = self.get_level_range_score(pro_level_range)
        
        # 判断匹配情况
        if pro_min == 0 or pro_max == 0:
            match_status = '无法评估'
        elif system_min >= pro_min - 2 and system_max <= pro_max + 2:
            match_status = '在合理范围内'
        elif system_min > pro_max + 2:
            match_status = '系统明显高估'
        elif system_max < pro_min - 2:
            match_status = '系统明显低估'
        elif system_min > pro_max + 1:
            match_status = '系统可能高估'
        elif system_max < pro_min - 1:
            match_status = '系统可能低估'
        else:
            match_status = '部分匹配'
        
        result['评估结果']['级别评估'] = {
            '系统推断范围': system_level,
            '专业评估范围': pro_level_range,
            '匹配状态': match_status,
            '级别差距': f"系统({system_min}-{system_max}) vs 专业({pro_min}-{pro_max})"
        }
    
    def _assess_case_depth(self, candidate, result):
        """案例深度评估"""
        project_desc = candidate.get('项目经验描述', '')
        deal_count = int(candidate.get('投成案例数', 0))
        
        depth_indicators = {
            '主导案例': 0,
            '高价值案例': 0,
            '硬科技案例': 0,
            '退出案例': 0
        }
        
        # 检查主导案例
        lead_keywords = ['主导', '牵头', '独立挖掘', '独立推动', '全程负责', '主要负责']
        for kw in lead_keywords:
            if kw in project_desc:
                depth_indicators['主导案例'] += 1
        
        # 检查高价值案例
        value_keywords = ['独角兽', '上市', 'IPO', 'IRR', '高回报', '退出', 'carry']
        for kw in value_keywords:
            if kw in project_desc:
                depth_indicators['高价值案例'] += 1
        
        # 检查硬科技案例
        hardtech_count = 0
        for sector, keywords in self.hardtech_sectors.items():
            for kw in keywords:
                if kw in project_desc:
                    hardtech_count += 1
        depth_indicators['硬科技案例'] = min(hardtech_count // 3, 5)  # 每3个关键词算1分，最多5分
        
        result['评估结果']['案例深度'] = depth_indicators
    
    def _calculate_composite_score(self, candidate, result):
        """计算综合评分（0-100）"""
        base_info = result['基础信息']
        
        # 学历分 (0-25)
        bachelor_tier = candidate.get('本科学校层级', '其他')
        master_tier = candidate.get('硕士学校层级', '其他')
        
        tier_scores = {'T1': 25, 'T2': 20, 'T3': 15, '其他': 10}
        edu_score = (tier_scores.get(bachelor_tier, 10) + tier_scores.get(master_tier, 10)) / 2
        
        # 经验分 (0-35)
        vc_exp = base_info['VC经验年数']
        total_exp = base_info['总经验年数']
        stem_bonus = 5 if base_info['STEM背景'] == '是' else 0
        
        exp_score = min(vc_exp * 2 + total_exp * 0.5 + stem_bonus, 35)
        
        # 案例分 (0-25)
        deal_count = base_info['投成案例数']
        depth_score = sum(result['评估结果'].get('案例深度', {}).values())
        case_score = min(deal_count * 2 + depth_score * 1.5, 25)
        
        # 潜力分 (0-15)
        inferred_age = base_info['推断年龄']
        if inferred_age and inferred_age != 'None':
            try:
                age = float(inferred_age)
                # 年龄越小潜力分越高
                if age <= 25:
                    potential_score = 15
                elif age <= 28:
                    potential_score = 12
                elif age <= 32:
                    potential_score = 9
                elif age <= 35:
                    potential_score = 6
                else:
                    potential_score = 3
            except:
                potential_score = 8
        else:
            potential_score = 8
        
        total_score = edu_score + exp_score + case_score + potential_score
        
        result['评估结果']['综合评分'] = {
            '学历分': round(edu_score, 1),
            '经验分': round(exp_score, 1),
            '案例分': round(case_score, 1),
            '潜力分': round(potential_score, 1),
            '总分': round(total_score, 1),
            '评级': self._get_rating(total_score)
        }
    
    def _get_rating(self, score):
        """根据分数评级"""
        if score >= 85:
            return 'S级（顶尖候选人）'
        elif score >= 75:
            return 'A级（优秀候选人）'
        elif score >= 65:
            return 'B级（良好候选人）'
        elif score >= 50:
            return 'C级（合格候选人）'
        else:
            return 'D级（需要关注）'
    
    def _generate_recruiter_recommendations(self, candidate, result):
        """生成猎头实操建议"""
        name = candidate['姓名']
        base_info = result['基础信息']
        level_assessment = result['评估结果']['级别评估']
        pro_assessment = result['专业评估']
        
        recommendations = []
        
        # 基于匹配状态
        match_status = level_assessment['匹配状态']
        if '明显高估' in match_status:
            recommendations.append("⚠️ 注意：系统明显高估，猎头需重点核查实际案例深度")
        elif '明显低估' in match_status:
            recommendations.append("⚠️ 注意：系统明显低估，候选人可能有未体现的产业经验")
        elif '可能高估' in match_status:
            recommendations.append("🔍 关注：系统可能高估，建议进一步验证主导案例")
        elif '可能低估' in match_status:
            recommendations.append("🔍 关注：系统可能低估，建议挖掘产业背景价值")
        
        # 基于专业评估
        notes = pro_assessment.get('notes', '')
        if '优秀' in notes:
            recommendations.append("✅ 优秀候选人：可重点推荐")
        if '勉强' in notes or '概率' in notes:
            recommendations.append("⚠️ 选择性推荐：需匹配特定方向")
        
        # 基于VC经验
        vc_exp = base_info['VC经验年数']
        if vc_exp < 2:
            recommendations.append("📈 潜力型：经验较浅但潜力大，适合成长型机构")
        elif vc_exp >= 8:
            recommendations.append("🎯 资深型：经验丰富，适合需要立即产出的团队")
        
        result['评估结果']['猎头建议'] = recommendations

def main():
    print("\n加载标准化数据集...")
    
    # 读取数据
    data_file = '../data/hardtech_investors_standardized.csv'
    candidates = []
    
    with open(data_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append(row)
    
    print(f"共加载 {len(candidates)} 位候选人")
    
    # 初始化评估器
    evaluator = IntegratedHardTechEvaluator()
    
    # 评估所有候选人
    results = []
    
    print("\n" + "="*80)
    print("28位候选人集成评估结果")
    print("="*80)
    
    for candidate in candidates:
        name = candidate['姓名']
        result = evaluator.evaluate_candidate(candidate)
        results.append(result)
    
    # 汇总显示
    print(f"\n{'姓名':<6} {'VC经验':<6} {'案例':<6} {'系统级别':<15} {'专业级别':<15} {'匹配状态':<20} {'总分':<6} {'评级':<20}")
    print("-"*100)
    
    for result in results:
        name = result['姓名']
        base_info = result['基础信息']
        level_assessment = result['评估结果']['级别评估']
        score_info = result['评估结果']['综合评分']
        
        print(f"{name:<6} {base_info['VC经验年数']:<6.1f} {base_info['投成案例数']:<6} "
              f"{level_assessment['系统推断范围']:<15} {level_assessment['专业评估范围']:<15} "
              f"{level_assessment['匹配状态']:<20} {score_info['总分']:<6} {score_info['评级']:<20}")
    
    # 匹配度统计
    print("\n" + "="*80)
    print("匹配度统计分析")
    print("="*80)
    
    status_counts = {}
    for result in results:
        status = result['评估结果']['级别评估']['匹配状态']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n匹配状态分布:")
    for status, count in sorted(status_counts.items()):
        percentage = count / len(results) * 100
        names = [r['姓名'] for r in results if r['评估结果']['级别评估']['匹配状态'] == status]
        print(f"  {status}: {count}人 ({percentage:.1f}%) - {', '.join(names[:5])}{'...' if len(names) > 5 else ''}")
    
    # 问题分析
    print("\n" + "="*80)
    print("系统问题分析")
    print("="*80)
    
    problematic_candidates = []
    for result in results:
        status = result['评估结果']['级别评估']['匹配状态']
        if '明显' in status or '可能' in status:
            problematic_candidates.append(result)
    
    if problematic_candidates:
        print(f"\n需要关注的候选人 ({len(problematic_candidates)}人):")
        for result in problematic_candidates:
            name = result['姓名']
            status = result['评估结果']['级别评估']['匹配状态']
            system_level = result['评估结果']['级别评估']['系统推断范围']
            pro_level = result['评估结果']['级别评估']['专业评估范围']
            print(f"  {name}: {status} (系统:{system_level} vs 专业:{pro_level})")
    else:
        print("\n✅ 所有候选人级别评估都在合理范围内")
    
    # 保存详细结果
    output_file = '../output/integrated_evaluation_results.csv'
    
    fieldnames = ['姓名', '当前职位', 'VC经验年数', '投成案例数', 
                 '系统推断级别', '专业评估级别', '匹配状态',
                 '综合总分', '评级', '猎头建议']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                '姓名': result['姓名'],
                '当前职位': result['基础信息']['当前职位'],
                'VC经验年数': result['基础信息']['VC经验年数'],
                '投成案例数': result['基础信息']['投成案例数'],
                '系统推断级别': result['评估结果']['级别评估']['系统推断范围'],
                '专业评估级别': result['评估结果']['级别评估']['专业评估范围'],
                '匹配状态': result['评估结果']['级别评估']['匹配状态'],
                '综合总分': result['评估结果']['综合评分']['总分'],
                '评级': result['评估结果']['综合评分']['评级'],
                '猎头建议': ' | '.join(result['评估结果'].get('猎头建议', []))
            })
    
    print(f"\n详细评估结果已保存至: {output_file}")
    
    print("\n" + "="*80)
    print("系统总结与下一步")
    print("="*80)
    
    print("""
✅ 已完成：
1. 28位候选人的完整专业评估数据库
2. 级别区间评估（而非精准标签）
3. 匹配度分析（系统vs专业）
4. 猎头实操建议生成

🎯 当前系统表现：
- 匹配度分析可识别"明显高估/低估"
- 级别区间评估符合猎头实操需求
- 综合评分提供候选人分层参考

🔧 下一步优化方向：
1. 基于匹配度分析优化级别推断算法
2. 增加行业方向专项评估（如刘少雄的新能源vsAI）
3. 优化案例深度评估权重
4. 添加薪资期望合理性检查

💡 关键洞察：
1. 所有候选人都达到"推荐准入门槛"
2. 级别是动态范围，±1级正常
3. 系统需识别"明显不合理"而非追求精准
    """)

if __name__ == "__main__":
    main()