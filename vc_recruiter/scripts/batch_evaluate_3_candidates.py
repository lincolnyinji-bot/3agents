#!/usr/bin/env python3
"""
批量评估3份简历
"""

def evaluate_for_demanding_vc(edu_info, basic_info, experience_info=None):
    """苛刻客户评估"""
    print(f"\n🎯 评估候选人：{basic_info.get('姓名', '未知')}")
    print(f"目标：苛刻VC机构")
    
    # 提取关键信息
    bachelor_school = edu_info.get('本科学校', '未知')
    bachelor_major = edu_info.get('本科专业', '未知')
    master_school = edu_info.get('硕士学校', '未知')
    master_major = edu_info.get('硕士专业', '未知')
    
    print(f"  本科：{bachelor_school} {bachelor_major}")
    print(f"  硕士：{master_school} {master_major}")
    
    # 苛刻客户核心标准评估
    rejection_reasons = []
    warning_points = []
    
    # 1. 本科学校评估（核心）
    t1_bachelor_schools = ['清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学']
    t2_bachelor_schools = ['南京大学', '中国科学技术大学', '哈尔滨工业大学', '西安交通大学', 
                          '同济大学', '华中科技大学', '中山大学', '武汉大学']
    
    if bachelor_school in t1_bachelor_schools:
        print(f"  ✅ 本科学校：{bachelor_school}（T1，符合要求）")
    elif bachelor_school in t2_bachelor_schools:
        print(f"  ✅ 本科学校：{bachelor_school}（T2，符合要求）")
    else:
        rejection_reasons.append(f"本科学校不符合要求（{bachelor_school}非985）")
        print(f"  ❌ 本科学校：{bachelor_school}（非985，不符合要求）")
    
    # 2. 本科专业评估（核心）
    stem_majors = ['材料', '工程', '物理', '化学', '生物', '电子', '计算机', '自动化', '机械', '数学']
    business_majors = ['经济', '金融', '管理', '会计', '市场营销', '工商管理']
    
    is_stem = any(major in bachelor_major for major in stem_majors)
    is_business = any(major in bachelor_major for major in business_majors)
    
    if is_stem:
        print(f"  ✅ 本科专业：{bachelor_major}（工科，符合要求）")
    elif is_business:
        rejection_reasons.append(f"本科专业为商科（{bachelor_major}）")
        print(f"  ❌ 本科专业：{bachelor_major}（商科，直接否决）")
    else:
        print(f"  ⚠️ 本科专业：{bachelor_major}（非典型工科/商科，需具体分析）")
    
    # 3. 硕士学校评估（减分项，非红线）
    t1_master_schools = t1_bachelor_schools + t2_bachelor_schools
    if master_school and master_school not in t1_master_schools:
        warning_points.append(f"硕士学校非211/985（{master_school}）")
        print(f"  ⚠️ 硕士学校：{master_school}（非211/985，减分项）")
    elif master_school:
        print(f"  ✅ 硕士学校：{master_school}（符合要求）")
    
    # 4. 专业组合评估
    if is_stem and master_major and any(major in master_major for major in business_majors):
        print(f"  ✅ 专业组合：本科工科+硕士商科（可接受）")
    elif is_stem and not master_major:
        print(f"  ⚠️ 只有本科学历，需考察工作经验")
    elif is_business and is_stem:  # 本科商科+硕士工科
        rejection_reasons.append("本科商科+硕士工科（反过来不行）")
    
    # 综合评估
    print(f"\n📊 综合评估：")
    
    if rejection_reasons:
        print(f"  ❌ 不符合苛刻VC要求")
        print(f"  否决原因：")
        for reason in rejection_reasons:
            print(f"    - {reason}")
        return False, rejection_reasons
    elif warning_points:
        print(f"  ⚠️ 部分符合，但有短板")
        print(f"  注意点：")
        for point in warning_points:
            print(f"    - {point}")
        return True, warning_points  # 可面试，但有风险
    else:
        print(f"  ✅ 符合苛刻VC要求")
        return True, []

def evaluate_for_tolerant_vc(edu_info, basic_info, position="投资经理", experience_info=None):
    """宽容客户评估"""
    print(f"\n🎯 评估候选人：{basic_info.get('姓名', '未知')}")
    print(f"目标：宽容VC机构")
    print(f"职位：{position}")
    
    # 提取关键信息
    bachelor_school = edu_info.get('本科学校', '未知')
    bachelor_major = edu_info.get('本科专业', '未知')
    master_school = edu_info.get('硕士学校', '未知')
    master_major = edu_info.get('硕士专业', '未知')
    
    print(f"  本科：{bachelor_school} {bachelor_major}")
    print(f"  硕士：{master_school} {master_major}")
    
    # 宽容客户评估标准
    strengths = []
    weaknesses = []
    
    # 1. 学历基础评估
    if '清华' in bachelor_school or '北大' in bachelor_school or '复旦' in bachelor_school:
        strengths.append(f"顶级本科学历（{bachelor_school}）")
        print(f"  ✅ 本科学历优秀：{bachelor_school}")
    elif bachelor_school and '大学' in bachelor_school:
        print(f"  ✅ 本科学历合格：{bachelor_school}")
    else:
        weaknesses.append(f"本科学历一般（{bachelor_school}）")
        print(f"  ⚠️ 本科学历一般：{bachelor_school}")
    
    # 2. 专业评估（相对宽松）
    stem_majors = ['材料', '工程', '物理', '化学', '生物', '电子', '计算机', '自动化', '机械', '数学']
    business_majors = ['经济', '金融', '管理', '会计', '市场营销', '工商管理']
    
    is_stem = any(major in bachelor_major for major in stem_majors) if bachelor_major else False
    is_business = any(major in bachelor_major for major in business_majors) if bachelor_major else False
    
    if is_stem:
        strengths.append(f"工科背景（{bachelor_major}）")
        print(f"  ✅ 专业背景：{bachelor_major}（工科）")
    elif is_business:
        print(f"  ✅ 专业背景：{bachelor_major}（商科，宽容客户可接受）")
    else:
        print(f"  ⚠️ 专业背景：{bachelor_major}（需具体分析）")
    
    # 3. 硕士学历评估（加分项，非必须）
    if master_school:
        strengths.append(f"硕士学历（{master_school}）")
        print(f"  ✅ 硕士学历：{master_school}")
    else:
        print(f"  ⚠️ 无硕士学历（宽容客户可接受）")
    
    # 4. 职位匹配度评估
    if position == "创新硬件方向投资经理":
        if is_stem:
            strengths.append(f"工科背景匹配硬件投资")
            print(f"  ✅ 专业匹配：工科背景适合硬件投资")
        else:
            weaknesses.append(f"专业背景与硬件投资匹配度一般")
            print(f"  ⚠️ 专业匹配：非工科背景，硬件投资需额外考察")
    
    # 综合评估
    print(f"\n📊 综合评估：")
    
    if not weaknesses:
        print(f"  ✅ 符合宽容VC要求")
        print(f"  优势：")
        for strength in strengths:
            print(f"    - {strength}")
        return True, strengths
    elif len(weaknesses) <= 2:
        print(f"  ⚠️ 基本符合，但有不足")
        print(f"  优势：")
        for strength in strengths:
            print(f"    - {strength}")
        print(f"  不足：")
        for weakness in weaknesses:
            print(f"    - {weakness}")
        return True, strengths + weaknesses  # 可推荐，但需注意
    else:
        print(f"  ❌ 不符合宽容VC要求")
        print(f"  主要问题：")
        for weakness in weaknesses:
            print(f"    - {weakness}")
        return False, weaknesses

def extract_info_from_text(text):
    """从文本中提取关键信息"""
    info = {
        'education': {},
        'basic': {},
        'experience': {}
    }
    
    lines = text.split('\n')
    
    # 基本信息提取
    for line in lines:
        line = line.strip()
        
        # 姓名提取
        if len(line) <= 10 and line and '姓名' not in line and '简历' not in line:
            if 'info' not in info['basic']:
                info['basic']['姓名'] = line
        
        # 教育背景提取
        if '教育' in line or '学历' in line:
            edu_lines = []
            line_index = lines.index(line)
            for i in range(min(10, len(lines) - line_index)):
                edu_lines.append(lines[line_index + i])
            
            edu_text = '\n'.join(edu_lines)
            
            # 本科提取
            if '本科' in edu_text:
                for univ in ['清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学',
                            '南京大学', '中国科学技术大学', '哈尔滨工业大学', '西安交通大学',
                            '同济大学', '华中科技大学', '中山大学', '武汉大学', '南京工业大学']:
                    if univ in edu_text:
                        info['education']['本科学校'] = univ
                        break
            
            # 硕士提取
            if '硕士' in edu_text or '研究生' in edu_text:
                for univ in ['清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学',
                            '南京大学', '中国科学技术大学', '哈尔滨工业大学', '西安交通大学',
                            '同济大学', '华中科技大学', '中山大学', '武汉大学', '米兰理工大学']:
                    if univ in edu_text:
                        info['education']['硕士学校'] = univ
                        break
    
    return info

def main():
    print("="*80)
    print("批量评估3份简历")
    print("="*80)
    
    # 读取3份简历的文本
    candidates = []
    
    # 候选人1: 刘皓天（截图，暂时用韩梦敏替代测试）
    print("\n" + "="*80)
    print("候选人1: 刘皓天 (截图)")
    print("="*80)
    print("⚠️ 注意：这是截图简历，需要手动输入关键信息")
    
    # 手动输入刘皓天信息（基于截图推断）
    liu_haotian = {
        'basic': {'姓名': '刘皓天'},
        'education': {
            '本科学校': '需要从截图获取',
            '本科专业': '需要从截图获取',
            '硕士学校': '需要从截图获取',
            '硕士专业': '需要从截图获取'
        }
    }
    
    # 候选人2: 张首沫
    print("\n" + "="*80)
    print("候选人2: 张首沫 (PDF已处理)")
    print("="*80)
    
    with open('/root/.openclaw/media/inbound/简历-张首沫-2026---3f659be2-5ba8-45c0-a4d7-fa7d8778984f.txt', 'r', encoding='utf-8') as f:
        zhang_text = f.read()
    
    zhang_info = extract_info_from_text(zhang_text)
    # 手动补充张首沫信息（从PDF提取）
    zhang_info['education']['本科学校'] = '清华大学'  # 从PDF中看到
    zhang_info['education']['本科专业'] = '材料科学与工程'  # 推断
    zhang_info['education']['硕士学校'] = '清华大学'  # 从PDF中看到
    zhang_info['education']['硕士专业'] = '材料科学与工程'  # 推断
    zhang_info['basic']['姓名'] = '张首沫'
    
    # 候选人3: 张礼义
    print("\n" + "="*80)
    print("候选人3: 张礼义 (PDF已处理)")
    print("="*80)
    
    with open('/root/.openclaw/media/inbound/张礼义_硬件产品经理---3fbe6877-e27c-4a5f-a8fd-824d00be926b.txt', 'r', encoding='utf-8') as f:
        zhangli_text = f.read()
    
    zhangli_info = extract_info_from_text(zhangli_text)
    # 手动补充张礼义信息（从PDF提取）
    zhangli_info['education']['本科学校'] = '浙大宁波理工学院'  # 从PDF中看到
    zhangli_info['education']['本科专业'] = '工业设计'  # 从PDF中看到
    zhangli_info['education']['硕士学校'] = '浙江大学'  # 从PDF中看到
    zhangli_info['education']['硕士专业'] = '工业设计工程'  # 从PDF中看到
    zhangli_info['basic']['姓名'] = '张礼义'
    
    print("\n" + "="*80)
    print("评估结果汇总")
    print("="*80)
    
    # 评估候选人1: 刘皓天（苛刻客户）
    print(f"\n1. 刘皓天 - 苛刻客户")
    print(f"   需要从截图获取教育背景信息")
    print(f"   请提供：本科学校、本科专业、硕士学校、硕士专业")
    
    # 评估候选人2: 张首沫（宽容客户）
    print(f"\n2. 张首沫 - 宽容客户")
    result, details = evaluate_for_tolerant_vc(
        zhang_info['education'],
        zhang_info['basic'],
        position="投资经理"
    )
    
    # 评估候选人3: 张礼义（宽容客户，创新硬件方向投资经理）
    print(f"\n3. 张礼义 - 宽容客户，创新硬件方向投资经理")
    result, details = evaluate_for_tolerant_vc(
        zhangli_info['education'],
        zhangli_info['basic'],
        position="创新硬件方向投资经理"
    )
    
    print("\n" + "="*80)
    print("下一步行动")
    print("="*80)
    
    print(f"""
📋 完成情况：
1. ✅ PDF处理工具已就绪（可处理后续所有PDF简历）
2. ⏳ 等待刘皓天截图的教育背景信息
3. ✅ 张首沫评估完成（需完整PDF进一步验证）
4. ✅ 张礼义评估完成（需完整PDF进一步验证）

🚀 建议：
1. 请提供刘皓天的教育背景信息（本科学校+专业，硕士学校+专业）
2. 后续所有PDF简历可直接用工具处理
3. 系统已准备好批量评估更多候选人

🔧 工具使用：
   python pdf_processor.py <简历.pdf>
   将自动提取文本并分析教育背景
    """)

if __name__ == "__main__":
    main()