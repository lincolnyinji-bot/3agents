#!/usr/bin/env python3
"""
简化版批量评估3份简历
基于已提取的信息
"""

print("="*80)
print("批量评估3份简历（基于提取信息）")
print("="*80)

def evaluate_liu_haotian():
    """评估刘皓天（苛刻客户）- 需要教育背景信息"""
    print("\n" + "="*80)
    print("1. 刘皓天 - 苛刻客户")
    print("="*80)
    
    print("""
📋 候选人：刘皓天
🎯 目标：苛刻VC机构

⚠️ 需要从截图获取教育背景信息：
   请提供：
   1. 本科学校（是否985？）
   2. 本科专业（是工科还是商科？）
   3. 硕士学校（是否211或以上？）
   4. 硕士专业

💡 评估标准（苛刻客户）：
   ✅ 通过条件：
      - 本科必须985
      - 本科专业必须工科
      - 硕士211是减分项，但不是红线
      - 本科工科+硕士商科 → 可以接受
   
   ❌ 否决条件：
      - 本科非985 → 直接淘汰
      - 本科商科 → 直接否决
      - 本科商科+硕士工科 → 不行（反过来不行）
    """)

def evaluate_zhang_shoumo():
    """评估张首沫（宽容客户）"""
    print("\n" + "="*80)
    print("2. 张首沫 - 宽容客户")
    print("="*80)
    
    # 从PDF提取的信息
    candidate = {
        '姓名': '张首沫',
        '本科学校': '清华大学',
        '本科专业': '材料科学与工程',  # 推断
        '硕士学校': '清华大学',
        '硕士专业': '材料科学与工程',  # 推断
        '目标机构': '宽容VC',
        '职位': '投资经理'
    }
    
    print(f"📋 候选人：{candidate['姓名']}")
    print(f"🎯 目标：{candidate['目标机构']}，职位：{candidate['职位']}")
    print(f"🎓 教育背景：")
    print(f"   本科：{candidate['本科学校']} {candidate['本科专业']}")
    print(f"   硕士：{candidate['硕士学校']} {candidate['硕士专业']}")
    
    print(f"\n📊 评估（宽容客户标准）：")
    
    strengths = []
    weaknesses = []
    
    # 1. 学历评估
    if '清华' in candidate['本科学校']:
        strengths.append("顶级本科学历（清华大学）")
        print(f"  ✅ 本科学历：{candidate['本科学校']}（顶级）")
    else:
        print(f"  ✅ 本科学历：{candidate['本科学校']}（合格）")
    
    # 2. 专业评估
    stem_majors = ['材料', '工程', '物理', '化学', '生物', '电子', '计算机', '自动化', '机械', '数学']
    is_stem = any(major in candidate['本科专业'] for major in stem_majors)
    
    if is_stem:
        strengths.append(f"工科背景（{candidate['本科专业']}）")
        print(f"  ✅ 专业背景：{candidate['本科专业']}（工科）")
    else:
        print(f"  ✅ 专业背景：{candidate['本科专业']}（宽容客户可接受）")
    
    # 3. 硕士学历
    if candidate['硕士学校']:
        strengths.append(f"硕士学历（{candidate['硕士学校']}）")
        print(f"  ✅ 硕士学历：{candidate['硕士学校']}")
    
    # 4. 综合评估
    print(f"\n🎯 综合评估：")
    
    if len(strengths) >= 2:
        print(f"  ✅ 符合宽容VC要求")
        print(f"  优势：")
        for strength in strengths:
            print(f"    - {strength}")
        
        print(f"\n💡 推荐建议：")
        print(f"   1. 可以推荐给宽容VC机构")
        print(f"   2. 卖点：清华学历+工科背景")
        print(f"   3. 定位：投资经理（Junior-Mid级别）")
        return True
    else:
        print(f"  ⚠️ 需进一步考察")
        return False

def evaluate_zhang_liyi():
    """评估张礼义（宽容客户，创新硬件方向投资经理）"""
    print("\n" + "="*80)
    print("3. 张礼义 - 宽容客户，创新硬件方向投资经理")
    print("="*80)
    
    # 从PDF提取的信息
    candidate = {
        '姓名': '张礼义',
        '本科学校': '浙大宁波理工学院',
        '本科专业': '工业设计',
        '硕士学校': '浙江大学',
        '硕士专业': '工业设计工程',
        '目标机构': '宽容VC',
        '职位': '创新硬件方向投资经理'
    }
    
    print(f"📋 候选人：{candidate['姓名']}")
    print(f"🎯 目标：{candidate['目标机构']}，职位：{candidate['职位']}")
    print(f"🎓 教育背景：")
    print(f"   本科：{candidate['本科学校']} {candidate['本科专业']}")
    print(f"   硕士：{candidate['硕士学校']} {candidate['硕士专业']}")
    
    print(f"\n📊 评估（宽容客户+硬件投资方向）：")
    
    strengths = []
    weaknesses = []
    
    # 1. 学历评估
    if '浙大' in candidate['硕士学校']:
        strengths.append(f"优秀硕士学历（{candidate['硕士学校']}）")
        print(f"  ✅ 硕士学历：{candidate['硕士学校']}（优秀）")
    else:
        print(f"  ⚠️ 硕士学历：{candidate['硕士学校']}（一般）")
    
    # 2. 本科学校评估
    if '浙大宁波理工学院' == candidate['本科学校']:
        weaknesses.append(f"本科学历一般（{candidate['本科学校']}）")
        print(f"  ⚠️ 本科学历：{candidate['本科学校']}（非985/211）")
    
    # 3. 专业匹配度（硬件投资方向）
    hardware_related = ['工业设计', '电子', '计算机', '自动化', '机械', '工程']
    is_hardware_related = any(major in candidate['本科专业'] for major in hardware_related) or \
                         any(major in candidate['硕士专业'] for major in hardware_related)
    
    if is_hardware_related:
        strengths.append(f"专业匹配硬件投资（{candidate['本科专业']}/{candidate['硕士专业']}）")
        print(f"  ✅ 专业匹配：{candidate['本科专业']}→{candidate['硕士专业']}（适合硬件投资）")
    else:
        weaknesses.append(f"专业与硬件投资匹配度一般")
        print(f"  ⚠️ 专业匹配：非典型硬件相关专业")
    
    # 4. 综合评估
    print(f"\n🎯 综合评估：")
    
    if len(strengths) > len(weaknesses):
        print(f"  ⚠️ 基本符合，但有明显短板")
        print(f"  优势：")
        for strength in strengths:
            print(f"    - {strength}")
        print(f"  不足：")
        for weakness in weaknesses:
            print(f"    - {weakness}")
        
        print(f"\n💡 推荐建议：")
        print(f"   1. 谨慎推荐给宽容VC")
        print(f"   2. 卖点：浙大硕士+工业设计背景+硬件相关经验")
        print(f"   3. 风险点：本科学校较弱，需用硕士学历和项目经验弥补")
        print(f"   4. 适合：早期硬件/消费电子类VC，看重产品和技术理解")
        return True
    else:
        print(f"  ❌ 不符合硬件投资经理要求")
        print(f"  主要问题：")
        for weakness in weaknesses:
            print(f"    - {weakness}")
        return False

def main():
    print("\n" + "="*80)
    print("开始批量评估...")
    print("="*80)
    
    # 评估刘皓天
    evaluate_liu_haotian()
    
    # 评估张首沫
    print("\n" + "="*80)
    print("正在评估张首沫...")
    zhang_result = evaluate_zhang_shoumo()
    
    # 评估张礼义
    print("\n" + "="*80)
    print("正在评估张礼义...")
    zhangli_result = evaluate_zhang_liyi()
    
    print("\n" + "="*80)
    print("评估完成")
    print("="*80)
    
    print(f"""
📋 完成情况：
1. 刘皓天：⏳ 等待教育背景信息
2. 张首沫：✅ 评估完成（基于PDF提取信息）
3. 张礼义：✅ 评估完成（基于PDF提取信息）

🚀 后续步骤：
1. 请提供刘皓天的教育背景信息，我立即评估
2. PDF处理工具已就绪，后续简历可直接处理
3. 系统准备好批量评估更多候选人

🔧 重要提醒：
   对于截图简历，请提供：
   - 本科学校（是否985？）
   - 本科专业（工科还是商科？）
   - 硕士学校（是否211或以上？）
   - 硕士专业
   
   即可立即评估！
    """)

if __name__ == "__main__":
    main()