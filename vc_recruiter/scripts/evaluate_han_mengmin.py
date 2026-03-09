#!/usr/bin/env python3
"""
评估：韩梦敏 (hmm-profile-2026.pdf)
针对：相对苛刻的VC机构
"""

print("="*80)
print("候选人评估：韩梦敏")
print("目标机构：相对苛刻的VC机构")
print("="*80)

def evaluate_for_demanding_vc():
    """针对苛刻VC机构的专项评估"""
    
    # 候选人数据
    candidate = {
        '姓名': '韩梦敏',
        '出生年月': '1999.03',  # 25岁
        '当前职位': '投资经理',
        '当前公司': '碧鸿投资（吉利家族基金）',
        '工作经验': 1.0,  # 2023.2至今
        'VC经验': 1.0,
        '投成案例数': 10,  # 参与项目
        '主导案例数': 2,   # 昆仑芯、Fadu
        '本科学历': '南京工业大学',
        '本科专业': '工程管理',
        '本科学校层级': 'T3',
        '硕士学历': '米兰理工大学',
        '硕士专业': '管理工程',
        '硕士学校层级': 'T1',  # QS 50-100，全额奖学金
        '专业方向': '半导体、机器人、AI',
        'STEM背景': '是',
        '硬科技相关专业': '是',
        '实习经历': '丰富（券商研究所+上市公司战投+咨询）',
        '项目经验': """
少数股权项目（参与）：
1. 英特模 - 汽车检测设备和服务（创业板申报）
2. 瑶芯微 - SiC Mos（港股申报）
3. 华源智信 - Mini-Led显示驱动IC（D轮）
4. 大普微 - eSSD主控芯片&模组（创业板上市）
5. 宇树科技 - 四足&人形机器人（科创板辅导）
6. 成都微光 - 工业、车载CIS（参与招拍挂、投后管理）
7. 智驾大陆 - 智能驾驶解决方案
8. 它石 - 人形机器人
9. 瑞发科 - 车载SerDes IC（科创板辅导）
10. 舞肌科技 - 灵巧手

主导项目：
1. 昆仑芯 - 国产GPU（港股申报）- 项目负责人
   - 挖掘一级标的、对接吉利内部资源、与投行&项目方洽谈基石锚定份额和定价、专项搭建等
2. Fadu - PMIC eSSD板载电源管理IC（待分拆）- 项目负责人
   - 挖掘标的、拉产业方搭建合作、尽调访谈、投资报告撰写、并购方案洽谈等

孵化项目：
1. 芯舟 - 甲醇船总包商
2. 一星 - 人形机器人
        """,
        '技能证书': '证券从业+基金从业，计算机二级，雅思6.5',
        '国际经验': '马来亚大学交换生，米兰理工硕士，英文流利'
    }
    
    print("\n📋 候选人基本信息：")
    print(f"姓名：{candidate['姓名']}")
    print(f"年龄：{candidate['出生年月']}（约25岁）")
    print(f"当前：{candidate['当前职位']} @ {candidate['当前公司']}")
    print(f"VC经验：{candidate['VC经验']}年")
    print(f"专业方向：{candidate['专业方向']}")
    
    print("\n🎓 教育背景：")
    print(f"本科：{candidate['本科学历']} {candidate['本科专业']}（{candidate['本科学校层级']}）")
    print(f"硕士：{candidate['硕士学历']} {candidate['硕士专业']}（{candidate['硕士学校层级']}，全额奖学金）")
    
    print("\n" + "="*80)
    print("针对'苛刻VC机构'的专项评估")
    print("="*80)
    
    # 苛刻VC机构的评估标准
    print("\n🎯 苛刻VC机构典型要求：")
    print("1. 顶级学历（清北复交/海外名校）")
    print("2. 技术深度（STEM专业，能和技术团队对话）")
    print("3. 早期项目经验（天使/A轮为主）")
    print("4. 独立挖掘项目能力")
    print("5. 快速学习能力和行业认知深度")
    
    # 评估维度
    assessment = {}
    
    print("\n" + "="*80)
    print("维度评估")
    print("="*80)
    
    # 1. 学历评估（苛刻VC非常看重）
    print(f"\n1. 📚 学历评估：")
    
    # 本科：南京工业大学（T3）
    bachelor_score = 5 if candidate['本科学校层级'] == 'T1' else 3 if candidate['本科学校层级'] == 'T2' else 1
    print(f"   本科：{candidate['本科学历']}（{candidate['本科学校层级']}）→ 得分：{bachelor_score}/5")
    
    # 硕士：米兰理工大学（T1，QS 50-100，全额奖学金）
    master_score = 8  # 海外名校，全额奖学金加分
    print(f"   硕士：{candidate['硕士学历']}（{candidate['硕士学校层级']}，全额奖学金）→ 得分：{master_score}/10")
    
    # 专业匹配度：工程管理 → 半导体/机器人/AI
    major_match = 7 if candidate['STEM背景'] == '是' else 3
    print(f"   专业匹配：{candidate['本科专业']}→{candidate['硕士专业']}→{candidate['专业方向']} → 得分：{major_match}/10")
    
    edu_total = bachelor_score + master_score + major_match
    edu_max = 25
    edu_percentage = edu_total / edu_max * 100
    
    print(f"   学历总分：{edu_total}/{edu_max} ({edu_percentage:.1f}%)")
    
    if edu_percentage >= 80:
        edu_assessment = "✅ 学历优秀，符合苛刻VC要求"
    elif edu_percentage >= 60:
        edu_assessment = "⚠️ 学历良好，但本科背景可能成为短板"
    else:
        edu_assessment = "❌ 学历不符合苛刻VC要求"
    
    print(f"   评估：{edu_assessment}")
    
    assessment['学历评估'] = {
        '总分': edu_total,
        '百分比': edu_percentage,
        '评估': edu_assessment,
        '短板': '本科学校层级(T3)可能成为问题'
    }
    
    # 2. 技术深度评估（苛刻VC核心）
    print(f"\n2. 🔬 技术深度评估：")
    
    # STEM背景
    stem_score = 8 if candidate['STEM背景'] == '是' else 2
    print(f"   STEM背景：{candidate['STEM背景']} → 得分：{stem_score}/10")
    
    # 专业方向匹配度
    target_industries = ['半导体', '机器人', 'AI']
    industry_match = 0
    for industry in target_industries:
        if industry in candidate['专业方向']:
            industry_match += 3
    
    print(f"   专业方向匹配：{candidate['专业方向']} → 得分：{industry_match}/9")
    
    # 技术理解能力（从项目描述推断）
    tech_keywords = ['芯片', 'IC', 'GPU', 'SiC', 'eSSD', '主控', '驱动', '机器人', 'AI']
    project_desc = candidate['项目经验']
    tech_count = sum(1 for kw in tech_keywords if kw in project_desc)
    tech_understanding = min(tech_count * 2, 10)
    
    print(f"   技术关键词：{tech_count}个 → 得分：{tech_understanding}/10")
    
    tech_total = stem_score + industry_match + tech_understanding
    tech_max = 29
    tech_percentage = tech_total / tech_max * 100
    
    print(f"   技术深度总分：{tech_total}/{tech_max} ({tech_percentage:.1f}%)")
    
    if tech_percentage >= 70:
        tech_assessment = "✅ 技术深度良好，能理解硬科技项目"
    elif tech_percentage >= 50:
        tech_assessment = "⚠️ 技术深度一般，需要进一步考察"
    else:
        tech_assessment = "❌ 技术深度不足"
    
    print(f"   评估：{tech_assessment}")
    
    assessment['技术深度'] = {
        '总分': tech_total,
        '百分比': tech_percentage,
        '评估': tech_assessment
    }
    
    # 3. 项目经验评估
    print(f"\n3. 📊 项目经验评估：")
    
    # 案例数量
    case_count = candidate['投成案例数']
    case_quantity = min(case_count * 3, 15)  # 每个案例3分，最多15分
    print(f"   案例数量：{case_count}个 → 得分：{case_quantity}/15")
    
    # 案例质量（阶段分布）
    # 分析项目阶段
    early_stage_keywords = ['天使', '种子', '早期', '孵化']
    growth_stage_keywords = ['A轮', 'B轮', 'C轮', 'D轮']
    late_stage_keywords = ['Pre-IPO', '上市', '申报', '辅导']
    
    early_count = sum(1 for kw in early_stage_keywords if kw in project_desc)
    growth_count = sum(1 for kw in growth_stage_keywords if kw in project_desc)
    late_count = sum(1 for kw in late_stage_keywords if kw in project_desc)
    
    print(f"   项目阶段分布：")
    print(f"     - 早期：{early_count}个")
    print(f"     - 成长期：{growth_count}个（D轮等）")
    print(f"     - 后期：{late_count}个（申报/辅导/上市）")
    
    # 苛刻VC偏好早期项目
    if early_count >= 2:
        stage_score = 10
    elif early_count >= 1:
        stage_score = 7
    elif growth_count >= 2:
        stage_score = 5  # 成长期项目，对VC来说偏晚
    else:
        stage_score = 3
    
    print(f"   阶段匹配度（VC偏好早期）→ 得分：{stage_score}/10")
    
    # 主导能力
    lead_count = candidate['主导案例数']
    lead_score = lead_count * 5  # 每个主导项目5分
    print(f"   主导项目：{lead_count}个（昆仑芯、Fadu）→ 得分：{lead_score}/10")
    
    # 案例行业分布
    industry_distribution = 8  # 半导体、机器人、AI全覆盖
    print(f"   行业分布：半导体/机器人/AI全覆盖 → 得分：{industry_distribution}/10")
    
    case_total = case_quantity + stage_score + lead_score + industry_distribution
    case_max = 45
    case_percentage = case_total / case_max * 100
    
    print(f"   案例经验总分：{case_total}/{case_max} ({case_percentage:.1f}%)")
    
    if case_percentage >= 70:
        case_assessment = "✅ 项目经验丰富，主导能力突出"
    elif case_percentage >= 50:
        case_assessment = "⚠️ 项目经验良好，但早期项目较少"
    else:
        case_assessment = "❌ 项目经验不足"
    
    print(f"   评估：{case_assessment}")
    print(f"   注意：案例多为'参与'角色，'主导'项目仅2个")
    
    assessment['项目经验'] = {
        '总分': case_total,
        '百分比': case_percentage,
        '评估': case_assessment,
        '弱点': '早期项目较少，多数为参与角色'
    }
    
    # 4. 潜力与成长性评估（25岁，1年经验）
    print(f"\n4. 📈 潜力与成长性评估：")
    
    # 年龄优势
    age = 25
    if age <= 25:
        age_score = 10
    elif age <= 28:
        age_score = 8
    elif age <= 32:
        age_score = 5
    else:
        age_score = 3
    
    print(f"   年龄：{age}岁 → 得分：{age_score}/10")
    
    # 学习能力（从实习经历推断）
    internship_count = 8  # 审计/咨询/战投+券商研究所丰富实习
    learning_score = min(internship_count, 10)
    print(f"   实习经历：{internship_count}段丰富实习 → 得分：{learning_score}/10")
    
    # 国际化视野
    international_score = 8  # 交换生+海外硕士+英文流利
    print(f"   国际视野：马来亚大学交换+米兰理工硕士+英文流利 → 得分：{international_score}/10")
    
    # 快速成长证据
    growth_evidence = 7  # 1年内从投资助理到投资经理，主导2个项目
    print(f"   成长速度：1年从助理到经理，主导2个项目 → 得分：{growth_evidence}/10")
    
    potential_total = age_score + learning_score + international_score + growth_evidence
    potential_max = 40
    potential_percentage = potential_total / potential_max * 100
    
    print(f"   潜力总分：{potential_total}/{potential_max} ({potential_percentage:.1f}%)")
    
    if potential_percentage >= 75:
        potential_assessment = "✅ 潜力巨大，成长速度快"
    elif potential_percentage >= 60:
        potential_assessment = "⚠️ 潜力良好，需考察持续成长性"
    else:
        potential_assessment = "❌ 潜力一般"
    
    print(f"   评估：{potential_assessment}")
    
    assessment['潜力评估'] = {
        '总分': potential_total,
        '百分比': potential_percentage,
        '评估': potential_assessment,
        '优势': '年轻、学习能力强、国际视野'
    }
    
    # 5. 综合评估
    print("\n" + "="*80)
    print("综合评估结果")
    print("="*80)
    
    # 加权总分
    weights = {
        '学历': 0.25,      # 苛刻VC非常看重学历
        '技术深度': 0.30,   # 硬科技VC核心要求
        '项目经验': 0.30,   # 实操能力
        '潜力': 0.15       # 年轻候选人的成长性
    }
    
    weighted_scores = {}
    total_weighted_score = 0
    
    for dimension, weight in weights.items():
        dim_key = {
            '学历': '学历评估',
            '技术深度': '技术深度',
            '项目经验': '项目经验',
            '潜力': '潜力评估'
        }[dimension]
        
        percentage = assessment[dim_key]['百分比'] / 100
        weighted_score = percentage * weight * 100
        weighted_scores[dimension] = weighted_score
        total_weighted_score += weighted_score
    
    print(f"\n📊 加权综合评分：")
    for dimension, score in weighted_scores.items():
        print(f"   {dimension}：{score:.1f}/{(weights[dimension]*100):.0f}")
    
    print(f"   总分：{total_weighted_score:.1f}/100")
    
    # 总体评估
    if total_weighted_score >= 85:
        overall_assessment = "✅ 强烈推荐：完全符合苛刻VC要求"
        recommendation = "可以放心推荐给顶级VC机构"
    elif total_weighted_score >= 70:
        overall_assessment = "⚠️ 谨慎推荐：部分符合，但有明显短板"
        recommendation = "可推荐，但需提前沟通可能被质疑的点"
    elif total_weighted_score >= 50:
        overall_assessment = "⚠️ 有限推荐：仅适合部分VC"
        recommendation = "建议推荐给对学历要求相对宽容的VC"
    else:
        overall_assessment = "❌ 不推荐：不符合苛刻VC要求"
        recommendation = "建议考虑其他类型机构"
    
    print(f"\n🎯 总体评估：{overall_assessment}")
    print(f"   推荐建议：{recommendation}")
    
    # 关键优缺点分析
    print(f"\n🔍 关键优缺点分析：")
    
    print(f"\n✅ 核心优势：")
    print(f"   1. 年轻有潜力（25岁，1年经验快速成长）")
    print(f"   2. 技术背景扎实（工程管理+STEM，理解硬科技）")
    print(f"   3. 项目经验丰富（10个项目，覆盖半导体/机器人/AI）")
    print(f"   4. 国际视野（交换生+海外硕士，英文流利）")
    print(f"   5. 主导能力初显（昆仑芯、Fadu两个主导项目）")
    
    print(f"\n⚠️ 潜在短板（对苛刻VC而言）：")
    print(f"   1. 本科学历（南京工业大学，T3层级）")
    print(f"   2. VC经验较短（仅1年）")
    print(f"   3. 早期项目经验较少（多为成长期/后期项目）")
    print(f"   4. 多数为'参与'角色，独立挖掘项目能力待验证")
    print(f"   5. 家族基金背景 vs 市场化VC文化差异")
    
    print(f"\n🎯 猎头实操建议：")
    
    if total_weighted_score >= 70:
        print(f"   1. 目标机构：对学历要求相对宽容的硬科技VC")
        print(f"   2. 推荐职位：投资经理（Junior级别）")
        print(f"   3. 卖点突出：年轻潜力、技术理解、项目广度、国际视野")
        print(f"   4. 提前准备：准备好解释本科背景和早期项目经验问题")
        print(f"   5. 匹配建议：专注半导体/机器人的早期VC，需要快速成长的团队")
    else:
        print(f"   1. 考虑其他机构类型：产业资本、企业战投、成长型PE")
        print(f"   2. 继续积累：建议再积累1-2年经验，增加早期项目经验")
        print(f"   3. 学历提升：考虑在职MBA或证书提升学历背景")
    
    # 系统改进建议
    print(f"\n🔧 系统改进建议（基于此案例）：")
    print(f"   1. 增加'本科学校层级'对苛刻VC的权重调整")
    print(f"   2. 细化'早期vs成长期'项目经验评估")
    print(f"   3. 增加'机构文化匹配度'评估（家族基金vs市场化VC）")
    print(f"   4. 优化'年轻候选人'的潜力评估模型")
    
    return {
        '候选人': candidate['姓名'],
        '综合评分': total_weighted_score,
        '总体评估': overall_assessment,
        '推荐建议': recommendation,
        '详细评估': assessment
    }

def main():
    print("开始评估韩梦敏候选人...")
    
    result = evaluate_for_demanding_vc()
    
    print("\n" + "="*80)
    print("评估总结")
    print("="*80)
    
    print(f"""
候选人：{result['候选人']}
目标机构：相对苛刻的VC机构
综合评分：{result['综合评分']:.1f}/100
总体评估：{result['总体评估']}
推荐建议：{result['推荐建议']}

💡 关键洞察：
1. 这是一个典型的"潜力型"候选人：年轻、学习能力强、技术背景好
2. 对苛刻VC而言，主要短板是本科学校和早期项目经验
3. 家族基金背景可能影响市场化VC的适配性
4. 半导体/机器人/AI的专业方向非常符合当前热点

🎯 最终建议：
  如果目标VC对学历要求相对宽容，且看重潜力和技术理解能力 → ✅ 可推荐
  如果目标VC是典型的"清北复交"学历控，且要求丰富早期经验 → ⚠️ 需谨慎
    """)

if __name__ == "__main__":
    main()