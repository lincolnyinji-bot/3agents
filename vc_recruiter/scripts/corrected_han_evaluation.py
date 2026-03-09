#!/usr/bin/env python3
"""
修正版：韩梦敏评估（基于你的专业反馈）
"""

print("="*80)
print("修正版评估：韩梦敏")
print("基于专业反馈修正算法错误")
print("="*80)

def corrected_evaluation():
    """修正后的评估"""
    
    # 基础信息（修正工作年限）
    candidate = {
        '姓名': '韩梦敏',
        '出生年月': '1999.03',  # 25岁
        '当前职位': '投资经理',
        '当前公司': '碧鸿投资（吉利家族基金）',
        '工作时间': '2023.02-至今',  # 3年（2023-2024-2025-2026）
        'VC经验': 3.0,  # 修正：3年，不是1年
        '投成案例数': 10,
        '主导案例数': 2,
        '本科学历': '南京工业大学',
        '本科学校层级': 'T3',
        '硕士学历': '米兰理工大学',
        '硕士学校层级': 'T1',
        '专业方向': '半导体、机器人、AI'
    }
    
    print(f"\n📋 修正后的基础信息：")
    print(f"姓名：{candidate['姓名']}")
    print(f"VC经验：{candidate['VC经验']}年（2023.02-至今，3年）")
    print(f"投成案例：{candidate['投成案例数']}个（主导{candidate['主导案例数']}个）")
    print(f"学历：{candidate['本科学历']}（{candidate['本科学校层级']}）→ {candidate['硕士学历']}（{candidate['硕士学校层级']}）")
    
    print("\n" + "="*80)
    print("针对'相对苛刻的VC机构'修正评估")
    print("="*80)
    
    print("\n🎯 苛刻VC的核心门槛：")
    print("1. 学历门槛：本科必须T1/T2（清北复交/985）")
    print("2. 早期项目经验：天使/A轮主导经验")
    print("3. 独立挖掘能力：不是'参与'而是'主导'")
    print("4. VC相关经验：早期投资，非港股/并购")
    
    print("\n" + "="*80)
    print("逐项评估（修正版）")
    print("="*80)
    
    total_score = 100
    deduction_reasons = []
    
    # 1. 学历评估（苛刻VC一票否决项）
    print(f"\n1. 🎓 学历评估（权重：40%）")
    
    # 本科T3对苛刻VC是硬伤
    bachelor_deduction = 30  # 重大扣分
    deduction_reasons.append(f"本科学校T3（{candidate['本科学历']}）-30分")
    
    # 硕士T1部分弥补
    master_bonus = 10  # 米兰理工T1，全额奖学金
    deduction_reasons.append(f"硕士学校T1（{candidate['硕士学历']}）+10分")
    
    edu_score = total_score - bachelor_deduction + master_bonus
    print(f"   原始总分：100")
    print(f"   本科T3扣分：-30分（重大短板）")
    print(f"   硕士T1加分：+10分（部分弥补）")
    print(f"   学历得分：{edu_score}/100")
    print(f"   ❗ 结论：学历不符合苛刻VC要求")
    
    # 2. 项目经验评估
    print(f"\n2. 📊 项目经验评估（权重：35%）")
    
    project_score = 100
    project_deductions = []
    
    # 问题1：参与多，主导少
    participation_ratio = 8/10  # 8个参与，2个主导
    if participation_ratio >= 0.7:
        deduction = 20
        project_deductions.append(f"参与项目比例过高（80%）-20分")
    
    # 问题2：早期项目少
    early_projects = 1  # 只有孵化项目算早期
    if early_projects <= 2:
        deduction = 25
        project_deductions.append(f"早期项目经验不足（1个）-25分")
    
    # 问题3：港股锚定/跨境并购对VC价值有限
    vc_irrelevant_projects = 2  # 昆仑芯（港股锚定）、Fadu（跨境并购）
    if vc_irrelevant_projects >= 1:
        deduction = 15
        project_deductions.append(f"VC相关度低的项目（港股锚定/跨境并购）-15分")
    
    # 加分：案例数量多，行业覆盖广
    bonus = 10
    project_deductions.append(f"案例数量多（10个），行业覆盖广（半导体/机器人/AI）+10分")
    
    # 计算扣分
    total_deduction = sum([20, 25, 15]) - 10  # 扣分-加分
    project_score -= total_deduction
    
    print(f"   原始总分：100")
    for deduction in project_deductions:
        print(f"   {deduction}")
    print(f"   项目经验得分：{project_score}/100")
    print(f"   ❗ 结论：项目经验与VC需求不匹配")
    
    # 3. 工作年限评估（修正）
    print(f"\n3. ⏰ 工作年限评估（权重：15%）")
    
    tenure_score = 100
    
    # 3年经验对投资经理是合理的
    if candidate['VC经验'] >= 3:
        tenure_deduction = 0
        print(f"   工作年限：{candidate['VC经验']}年（合理）")
        print(f"   年限得分：{tenure_score}/100")
    else:
        tenure_deduction = 20
        tenure_score -= tenure_deduction
        print(f"   工作年限不足：-{tenure_deduction}分")
        print(f"   年限得分：{tenure_score}/100")
    
    # 4. 机构文化匹配度
    print(f"\n4. 🏢 机构文化匹配度（权重：10%）")
    
    culture_score = 100
    
    # 家族基金 vs 市场化VC
    family_office_penalty = 15
    culture_score -= family_office_penalty
    print(f"   家族基金背景可能不匹配市场化VC文化：-15分")
    print(f"   文化匹配得分：{culture_score}/100")
    
    # 综合计算
    print("\n" + "="*80)
    print("综合评估结果（修正版）")
    print("="*80)
    
    # 加权计算
    weights = {
        '学历': 0.40,      # 苛刻VC最看重
        '项目经验': 0.35,   # 早期经验关键
        '工作年限': 0.15,   # 基本要求
        '文化匹配': 0.10    # 软性要求
    }
    
    weighted_score = (
        edu_score * weights['学历'] +
        project_score * weights['项目经验'] +
        tenure_score * weights['工作年限'] +
        culture_score * weights['文化匹配']
    )
    
    print(f"\n📊 加权综合评分：")
    print(f"   学历（40%）：{edu_score} × 0.40 = {edu_score * weights['学历']:.1f}")
    print(f"   项目经验（35%）：{project_score} × 0.35 = {project_score * weights['项目经验']:.1f}")
    print(f"   工作年限（15%）：{tenure_score} × 0.15 = {tenure_score * weights['工作年限']:.1f}")
    print(f"   文化匹配（10%）：{culture_score} × 0.10 = {culture_score * weights['文化匹配']:.1f}")
    print(f"   总分：{weighted_score:.1f}/100")
    
    # 评估结论
    if weighted_score >= 80:
        assessment = "✅ 符合苛刻VC要求"
        recommendation = "可以推荐"
    elif weighted_score >= 60:
        assessment = "⚠️ 部分符合，有明显短板"
        recommendation = "谨慎推荐，需重点沟通短板"
    else:
        assessment = "❌ 不符合苛刻VC要求"
        recommendation = "不建议推荐给苛刻VC机构"
    
    print(f"\n🎯 评估结论：{assessment}")
    print(f"   推荐建议：{recommendation}")
    
    # 详细分析
    print(f"\n🔍 详细分析：")
    
    print(f"\n❌ 不符合苛刻VC的核心原因：")
    print(f"   1. 学历硬伤：本科T3（{candidate['本科学历']}）")
    print(f"   2. 早期项目经验不足：仅1个早期项目")
    print(f"   3. 主导案例少：2/10（20%主导率）")
    print(f"   4. VC相关度低：港股锚定/跨境并购经验")
    print(f"   5. 机构文化可能不匹配：家族基金背景")
    
    print(f"\n✅ 对宽容VC的卖点：")
    print(f"   1. 年轻有潜力：25岁，3年经验")
    print(f"   2. 技术理解深度：半导体/机器人/AI专业方向")
    print(f"   3. 项目经验丰富：10个项目快速积累")
    print(f"   4. 国际视野：海外硕士，英文流利")
    print(f"   5. 主导能力初显：昆仑芯、Fadu两个硬核项目")
    
    print(f"\n🎯 猎头实操建议：")
    
    if weighted_score < 60:
        print(f"   1. ❌ 不推荐给苛刻VC机构")
        print(f"   2. ✅ 可推荐给要求相对宽容的VC")
        print(f"   3. 🎯 目标机构类型：")
        print(f"      - 对学历要求宽容的硬科技VC")
        print(f"      - 专注半导体/机器人/AI的专项基金")
        print(f"      - 需要快速成长人才的团队")
        print(f"   4. 📢 推荐策略：")
        print(f"      - 强调：年轻潜力+技术深度+项目广度")
        print(f"      - 准备：解释本科背景，强调硕士学历")
        print(f"      - 突出：昆仑芯、Fadu两个主导案例")
        print(f"   5. ⚠️ 风险提示：")
        print(f"      - 早期项目经验可能被质疑")
        print(f"      - 家族基金文化适应问题")
    
    return {
        '候选人': candidate['姓名'],
        '修正后VC经验': candidate['VC经验'],
        '综合评分': weighted_score,
        '评估结论': assessment,
        '推荐建议': recommendation
    }

def main():
    print("开始修正评估...")
    
    result = corrected_evaluation()
    
    print("\n" + "="*80)
    print("最终评估结论")
    print("="*80)
    
    print(f"""
候选人：{result['候选人']}
VC经验：{result['修正后VC经验']}年（修正：2023.02-至今）
综合评分：{result['综合评分']:.1f}/100
评估结论：{result['评估结论']}
推荐建议：{result['推荐建议']}

💡 核心结论（基于你的专业判断）：
1. 对苛刻VC机构：❌ 不合适
   - 学历硬伤（本科T3）
   - 早期项目经验不足
   - 主导案例少
   - VC相关经验偏差

2. 对宽容VC机构：✅ 可以试一试
   - 年轻潜力（25岁，3年经验）
   - 技术理解深度（半导体/机器人/AI）
   - 项目经验丰富（10个项目）
   - 国际视野+英文流利

🎯 猎头行动建议：
   - 避免推荐给典型"清北复交"学历控的VC
   - 选择性推荐给对学历相对宽容的硬科技VC
   - 重点突出：年轻潜力+技术深度+两个主导硬核案例

🔧 系统算法修正要点：
   1. 工作年限计算：使用实际工作时间，而非年龄推断
   2. 学历权重：对苛刻VC，本科T3是重大扣分项
   3. 项目经验评估：区分"参与"vs"主导"，重视早期项目
   4. 经验相关性：港股锚定/跨境并购对VC价值有限
    """)

if __name__ == "__main__":
    main()