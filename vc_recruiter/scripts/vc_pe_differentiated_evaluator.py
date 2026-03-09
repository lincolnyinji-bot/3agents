#!/usr/bin/env python3
"""
VC vs PE 差异化评估系统
基于投资阶段差异
"""

import csv

print("="*80)
print("VC vs PE 差异化评估系统")
print("根据投资阶段差异调整评估标准")
print("="*80)

class VCPEDifferentiatedEvaluator:
    def __init__(self):
        # VC专项评估标准
        self.vc_criteria = {
            '学历权重': {'STEM': 1.5, '商科': 1.0, '其他': 0.8},
            '经验偏好': {'技术研发': 1.3, '产业经验': 1.2, '券商行研': 1.0, '投行': 0.8},
            '案例要求': {'早期项目': 1.5, '成长期': 1.0, 'Pre-IPO': 0.7},
            '技术深度': {'硬科技': 1.5, '消费科技': 1.2, '传统行业': 0.8}
        }
        
        # PE专项评估标准
        self.pe_criteria = {
            '学历权重': {'商科': 1.3, 'STEM': 1.0, '其他': 0.9},
            '经验偏好': {'投行': 1.4, '四大': 1.3, '券商行研': 1.2, '产业经验': 1.0},
            '案例要求': {'Pre-IPO': 1.5, '并购': 1.4, '成长期': 1.2, '早期': 0.7},
            '财务能力': {'财务建模': 1.5, '尽调': 1.3, '估值': 1.3, '交易结构': 1.4}
        }
        
        # 通用级别标准
        self.level_hierarchy = {
            '投资分析实习生': 1,
            '投资分析师': 2,
            '投资经理': 3,
            '高级投资经理': 4,
            'SA': 5,
            'VP': 6,
            'D': 7,
            '总监': 7,
            'ED': 8,
            '合伙人': 9
        }
    
    def analyze_investment_focus(self, candidate, target_institution_type='VC'):
        """分析投资专注度"""
        project_desc = candidate.get('项目经验', '')
        position = candidate.get('当前职位', '')
        company = candidate.get('当前公司', '')
        
        # 投资阶段关键词
        vc_stage_keywords = ['天使', '早期', 'VC', '风险投资', '种子轮', 'A轮', 'B轮']
        pe_stage_keywords = ['PE', '成长期', 'Pre-IPO', '并购', 'C轮', 'D轮', '母基金', 'FoF']
        
        # 行业专注度
        industry_keywords = {
            '硬科技': ['AI', '人工智能', '半导体', '芯片', '机器人', '量子', '新能源', '新材料'],
            '消费科技': ['互联网', '电商', '消费', 'SaaS', '软件', '平台'],
            '生物医药': ['医药', '生物', '医疗', '健康', '器械'],
            '传统行业': ['制造', '能源', '材料', '化工', '汽车']
        }
        
        # 计算投资阶段匹配度
        vc_stage_count = sum(1 for kw in vc_stage_keywords if kw in project_desc)
        pe_stage_count = sum(1 for kw in pe_stage_keywords if kw in project_desc)
        
        # 行业专注度计算
        industry_counts = {}
        for industry, keywords in industry_keywords.items():
            count = sum(1 for kw in keywords if kw in project_desc)
            industry_counts[industry] = count
        
        # 判断投资阶段倾向
        if vc_stage_count > pe_stage_count:
            stage_tendency = 'VC倾向'
        elif pe_stage_count > vc_stage_count:
            stage_tendency = 'PE倾向'
        else:
            stage_tendency = '混合'
        
        # 判断行业专注度
        industry_focus = max(industry_counts.items(), key=lambda x: x[1]) if industry_counts else ('未知', 0)
        
        return {
            '投资阶段倾向': stage_tendency,
            'VC阶段关键词': vc_stage_count,
            'PE阶段关键词': pe_stage_count,
            '行业专注度': industry_focus,
            '各行业分布': industry_counts
        }
    
    def evaluate_for_vc(self, candidate):
        """VC专项评估"""
        name = candidate['姓名']
        vc_exp = float(candidate.get('VC投资经验年数', 0))
        deal_count = int(candidate.get('投成案例数', 0))
        
        print(f"\n🔍 VC专项评估：{name}")
        
        # 投资专注度分析
        focus_analysis = self.analyze_investment_focus(candidate, 'VC')
        print(f"  投资阶段：{focus_analysis['投资阶段倾向']} "
              f"(VC关键词:{focus_analysis['VC阶段关键词']}, PE关键词:{focus_analysis['PE阶段关键词']})")
        
        # STEM背景检查
        stem_background = candidate.get('STEM背景', '否')
        hardtech_major = candidate.get('硬科技相关专业', '否')
        
        print(f"  STEM背景：{stem_background}")
        print(f"  硬科技专业：{hardtech_major}")
        
        # VC适用性评分
        suitability_score = 0
        suitability_details = []
        
        # 1. STEM背景加分
        if stem_background == '是':
            suitability_score += 30
            suitability_details.append("STEM背景+30")
        
        # 2. 投资阶段匹配度
        if focus_analysis['投资阶段倾向'] == 'VC倾向':
            suitability_score += 25
            suitability_details.append("VC投资阶段匹配+25")
        elif focus_analysis['投资阶段倾向'] == '混合':
            suitability_score += 15
            suitability_details.append("混合投资阶段+15")
        else:
            suitability_score += 5
            suitability_details.append("PE倾向投资阶段+5")
        
        # 3. 案例数量和质量
        if deal_count >= 5:
            suitability_score += 25
            suitability_details.append(f"案例丰富({deal_count}个)+25")
        elif deal_count >= 2:
            suitability_score += 15
            suitability_details.append(f"案例适中({deal_count}个)+15")
        else:
            suitability_score += 5
            suitability_details.append(f"案例较少({deal_count}个)+5")
        
        # 4. 行业专注度
        industry_focus = focus_analysis['行业专注度']
        if industry_focus[0] in ['硬科技', '消费科技'] and industry_focus[1] >= 3:
            suitability_score += 20
            suitability_details.append(f"{industry_focus[0]}专注+20")
        
        # 总体评价
        if suitability_score >= 70:
            vc_suitability = '高度适合VC'
            recommendation = '强烈推荐给VC机构'
        elif suitability_score >= 50:
            vc_suitability = '适合VC'
            recommendation = '可推荐给VC机构'
        elif suitability_score >= 30:
            vc_suitability = '勉强适合VC'
            recommendation = '需谨慎匹配VC岗位'
        else:
            vc_suitability = '不适合VC'
            recommendation = '建议考虑PE或其他方向'
        
        return {
            'VC适用性': vc_suitability,
            '适用性得分': suitability_score,
            '得分详情': suitability_details,
            '推荐建议': recommendation,
            '投资阶段分析': focus_analysis
        }
    
    def evaluate_for_pe(self, candidate):
        """PE专项评估"""
        name = candidate['姓名']
        vc_exp = float(candidate.get('VC投资经验年数', 0))
        deal_count = int(candidate.get('投成案例数', 0))
        
        print(f"\n🏢 PE专项评估：{name}")
        
        # 投资专注度分析
        focus_analysis = self.analyze_investment_focus(candidate, 'PE')
        print(f"  投资阶段：{focus_analysis['投资阶段倾向']} "
              f"(VC关键词:{focus_analysis['VC阶段关键词']}, PE关键词:{focus_analysis['PE阶段关键词']})")
        
        # 检查财务相关经验
        project_desc = candidate.get('项目经验', '')
        financial_keywords = ['财务', '估值', '建模', '尽调', '并购', '交易', '投行', '四大']
        financial_count = sum(1 for kw in financial_keywords if kw in project_desc)
        
        print(f"  财务关键词：{financial_count}个")
        
        # PE适用性评分
        suitability_score = 0
        suitability_details = []
        
        # 1. 投资阶段匹配度
        if focus_analysis['投资阶段倾向'] == 'PE倾向':
            suitability_score += 30
            suitability_details.append("PE投资阶段匹配+30")
        elif focus_analysis['投资阶段倾向'] == '混合':
            suitability_score += 20
            suitability_details.append("混合投资阶段+20")
        else:
            suitability_score += 10
            suitability_details.append("VC倾向投资阶段+10")
        
        # 2. 案例规模和质量
        if deal_count >= 8:
            suitability_score += 30
            suitability_details.append(f"案例丰富({deal_count}个)+30")
        elif deal_count >= 4:
            suitability_score += 20
            suitability_details.append(f"案例适中({deal_count}个)+20")
        else:
            suitability_score += 10
            suitability_details.append(f"案例较少({deal_count}个)+10")
        
        # 3. 财务经验
        if financial_count >= 3:
            suitability_score += 25
            suitability_details.append(f"财务经验丰富({financial_count}个关键词)+25")
        elif financial_count >= 1:
            suitability_score += 15
            suitability_details.append(f"有财务经验({financial_count}个关键词)+15")
        else:
            suitability_score += 5
            suitability_details.append(f"财务经验有限+5")
        
        # 4. 学历背景（PE对商科更宽容）
        bachelor_major_type = candidate.get('本科专业类型', '其他')
        master_major_type = candidate.get('硕士专业类型', '其他')
        
        if '商科' in [bachelor_major_type, master_major_type]:
            suitability_score += 15
            suitability_details.append("商科背景+15")
        
        # 总体评价
        if suitability_score >= 70:
            pe_suitability = '高度适合PE'
            recommendation = '强烈推荐给PE机构'
        elif suitability_score >= 50:
            pe_suitability = '适合PE'
            recommendation = '可推荐给PE机构'
        elif suitability_score >= 30:
            pe_suitability = '勉强适合PE'
            recommendation = '需谨慎匹配PE岗位'
        else:
            pe_suitability = '不适合PE'
            recommendation = '建议考虑VC或其他方向'
        
        return {
            'PE适用性': pe_suitability,
            '适用性得分': suitability_score,
            '得分详情': suitability_details,
            '推荐建议': recommendation,
            '投资阶段分析': focus_analysis
        }
    
    def comprehensive_evaluation(self, candidate, target_institution='VC'):
        """综合评估（根据目标机构类型）"""
        name = candidate['姓名']
        
        print(f"\n" + "="*80)
        print(f"综合评估：{name}")
        print(f"目标机构类型：{target_institution}")
        print("="*80)
        
        # 基础信息
        print(f"\n📋 候选人基本信息：")
        print(f"  姓名：{name}")
        print(f"  当前职位：{candidate.get('当前职位', '')}")
        print(f"  当前公司：{candidate.get('当前公司', '')}")
        print(f"  VC经验：{candidate.get('VC投资经验年数', 0)}年")
        print(f"  投成案例：{candidate.get('投成案例数', 0)}个")
        
        # 学历背景
        print(f"\n🎓 学历背景：")
        print(f"  本科：{candidate.get('本科学历', '')} ({candidate.get('本科专业', '')})")
        print(f"  硕士：{candidate.get('硕士学历', '')} ({candidate.get('硕士专业', '')})")
        if candidate.get('博士学历'):
            print(f"  博士：{candidate.get('博士学历', '')} ({candidate.get('博士专业', '')})")
        
        # 根据目标机构类型评估
        if target_institution.upper() == 'VC':
            vc_result = self.evaluate_for_vc(candidate)
            pe_result = self.evaluate_for_pe(candidate)
            
            # 对比分析
            print(f"\n⚖️ VC vs PE 对比分析：")
            print(f"  VC适用性：{vc_result['VC适用性']} ({vc_result['适用性得分']}分)")
            print(f"  PE适用性：{pe_result['PE适用性']} ({pe_result['适用性得分']}分)")
            
            # 推荐结论
            if vc_result['适用性得分'] > pe_result['适用性得分'] + 10:
                conclusion = "✅ 更适合VC机构"
            elif pe_result['适用性得分'] > vc_result['适用性得分'] + 10:
                conclusion = "✅ 更适合PE机构"
            else:
                conclusion = "🔄 VC和PE都适合，取决于具体岗位"
            
            print(f"\n🎯 推荐结论：{conclusion}")
            
            return {
                'VC评估': vc_result,
                'PE评估': pe_result,
                '推荐结论': conclusion
            }
        
        elif target_institution.upper() == 'PE':
            pe_result = self.evaluate_for_pe(candidate)
            vc_result = self.evaluate_for_vc(candidate)
            
            print(f"\n⚖️ PE vs VC 对比分析：")
            print(f"  PE适用性：{pe_result['PE适用性']} ({pe_result['适用性得分']}分)")
            print(f"  VC适用性：{vc_result['VC适用性']} ({vc_result['适用性得分']}分)")
            
            # 推荐结论
            if pe_result['适用性得分'] > vc_result['适用性得分'] + 10:
                conclusion = "✅ 更适合PE机构"
            elif vc_result['适用性得分'] > pe_result['适用性得分'] + 10:
                conclusion = "✅ 更适合VC机构"
            else:
                conclusion = "🔄 PE和VC都适合，取决于具体岗位"
            
            print(f"\n🎯 推荐结论：{conclusion}")
            
            return {
                'PE评估': pe_result,
                'VC评估': vc_result,
                '推荐结论': conclusion
            }
        
        else:
            # 通用评估
            vc_result = self.evaluate_for_vc(candidate)
            pe_result = self.evaluate_for_pe(candidate)
            
            print(f"\n📊 双视角评估结果：")
            print(f"  VC视角：{vc_result['VC适用性']} ({vc_result['适用性得分']}分)")
            print(f"  PE视角：{pe_result['PE适用性']} ({pe_result['适用性得分']}分)")
            
            return {
                'VC评估': vc_result,
                'PE评估': pe_result,
                '综合建议': '需明确目标机构类型'
            }

def test_zhisheng():
    """测试郅胜案例（VC vs PE视角）"""
    print("\n" + "="*80)
    print("测试案例：郅胜（CV_Sheng_Zhi.pdf）")
    print("VC vs PE 差异化评估")
    print("="*80)
    
    # 创建郅胜候选人数据
    candidate = {
        '姓名': '郅胜',
        '当前职位': '副总裁（VP）',
        '当前公司': '中国华融国际控股有限公司（香港）',
        'VC投资经验年数': 4.0,
        '总工作经验年数': 8.0,
        '投成案例数': 12,
        '本科学历': '中国矿业大学',
        '本科专业': '矿业工程',
        '本科专业类型': '工程类',
        '硕士学历': '宾夕法尼亚州立大学',
        '硕士专业': '能源与矿物工程',
        '硕士专业类型': '工程类',
        '博士学历': '宾夕法尼亚州立大学',
        '博士专业': '能源与矿物工程',
        'STEM背景': '是',
        '硬科技相关专业': '是',
        '项目经验': """2020年至今 中国华融国际控股有限公司（香港）副总裁（VP）
1. 负责高新科技一级市场的行业调研、财务分析、模型估值、投后管理等，投资标的包括商汤（AI）、菜鸟、哈啰出行、易点天下（互联网）、安普隆（半导体）、欣旺达、中科电气（电池）、复星、国药（医药）、前海母基金（产业基金）等；
2. 与中信证券、易方达、IDG、前海方舟等团队共同研究投资策略和存量二级市场退出，投放、管理12个股权项目共计资产约40亿人民币，已有2个IPO；
3. 曾轮岗至风险管理部，负责项目投后管理审查，负责对接境内监管机构，审查公司关联交易业务，管理关联方200余家，有效防止内部违规利益输送；
4. 曾轮岗至战略规划部，协助公司CEO与各部门沟通，制定公司十四五战略规划，全程参与中信集团开展特殊机遇投资的战略合作业务。
2015年-2019年 宾州立大学/EMS能源研究院（美国）博士|讲师|博后级研究员
1. 新能源项目：研究因地制宜的风-光-地热-生物质多能互补综合发电方式和储能解决方案，解决新能源间歇性发电造成的垃圾电问题；
2. 新能源项目：研究优化地质结构提升地下有机质沼气化的生物质发电效率；
3. 碳捕捉项目：研究大型油气和采矿企业的CO2排放模型，研究CO2大规模封存的可行性方案,率先提出了基于W模型渗透率的超临界CO2地质储存模式。"""
    }
    
    # 初始化评估器
    evaluator = VCPEDifferentiatedEvaluator()
    
    print("\n🎯 测试1：作为VC候选人评估")
    print("-"*40)
    vc_result = evaluator.evaluate_for_vc(candidate)
    
    print("\n🎯 测试2：作为PE候选人评估")
    print("-"*40)
    pe_result = evaluator.evaluate_for_pe(candidate)
    
    print("\n" + "="*80)
    print("综合评估结论")
    print("="*80)
    
    print(f"\n📊 评估结果对比：")
    print(f"  VC适用性：{vc_result['VC适用性']} ({vc_result['适用性得分']}分)")
    print(f"    - {vc_result['推荐建议']}")
    print(f"  PE适用性：{pe_result['PE适用性']} ({pe_result['适用性得分']}分)")
    print(f"    - {pe_result['推荐建议']}")
    
    print(f"\n🔍 关键发现：")
    
    vc_score = vc_result['适用性得分']
    pe_score = pe_result['适用性得分']
    
    if pe_score > vc_score + 15:
        print(f"  ✅ 明显更适合PE机构（差距{pe_score-vc_score}分）")
        print(f"  📈 优势：投资阶段匹配、财务经验、案例规模")
    elif vc_score > pe_score + 15:
        print(f"  ✅ 明显更适合VC机构（差距{vc_score-pe_score}分）")
        print(f"  📈 优势：STEM背景、技术深度、早期项目经验")
    else:
        print(f"  🔄 两者都适合，差距不大（{abs(vc_score-pe_score)}分）")
        print(f"  💡 建议：根据具体岗位需求推荐")
    
    print(f"\n🎯 猎头实操建议：")
    
    if pe_score > vc_score:
        print(f"  1. 优先推荐给PE机构（特别是专注成长期/Pre-IPO的PE）")
        print(f"  2. 推荐职位：投资总监/VP（PE方向）")
        print(f"  3. 目标公司：华平、KKR、高瓴等PE，或产业资本战投部")
        print(f"  4. 卖点突出：12项目经验、2IPO、40亿规模、财务风控经验")
    else:
        print(f"  1. 优先推荐给VC机构")
        print(f"  2. 推荐职位：投资总监/VP（硬科技方向）")
        print(f"  3. 目标公司：红杉、高榕、源码等VC，或硬科技专项基金")
        print(f"  4. 卖点突出：新能源博士、技术深度、早期项目判断力")
    
    print(f"\n📋 系统改进要点：")
    print(f"  1. 增加VC/PE机构类型识别")
    print(f"  2. 区分投资阶段评估标准")
    print(f"  3. 调整STEM/商科背景权重")
    print(f"  4. 优化案例质量评估维度")

def main():
    print("VC vs PE 差异化评估系统演示")
    
    # 测试郅胜案例
    test_zhisheng()
    
    print("\n" + "="*80)
    print("系统能力总结")
    print("="*80)
    
    print("""
✅ 新增能力：
1. VC vs PE 机构类型识别
2. 投资阶段倾向分析
3. 差异化评估标准
4. 双视角对比评估

🎯 评估维度：
1. 投资阶段匹配度（VC关键词 vs PE关键词）
2. 背景偏好（VC:STEM vs PE:商科）
3. 案例类型（早期 vs 成长期/Pre-IPO）
4. 技能侧重（技术深度 vs 财务能力）

🔧 下一步优化：
1. 细化行业专注度评估
2. 增加机构文化匹配度
3. 优化薪资期望合理性检查
4. 建立更精细的案例分类

💡 关键洞察：
- 郅胜案例证明：同一候选人在VC和PE视角下评估结果不同
- 必须明确目标机构类型才能准确评估
- 投资阶段匹配度是关键区分因素
    """)

if __name__ == "__main__":
    main()