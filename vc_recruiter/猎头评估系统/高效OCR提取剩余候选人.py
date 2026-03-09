#!/usr/bin/env python3
"""
高效提取剩余8位候选人的关键信息
专注于提取岗位匹配所需的核心信息
"""

import subprocess
import os
import glob

def extract_key_info_from_image(image_path, candidate_num):
    """从图片中提取关键信息"""
    print(f"\n提取候选人{candidate_num}: {os.path.basename(image_path)}")
    
    try:
        # 运行OCR
        result = subprocess.run(
            ['tesseract', image_path, 'stdout', '-l', 'chi_sim+eng'],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        if not result.stdout:
            return {'状态': 'OCR失败'}
        
        text = result.stdout
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        info = {
            '编号': candidate_num,
            '文件名': os.path.basename(image_path),
            '原始行数': len(lines),
            '状态': '成功'
        }
        
        # 提取姓名（前5行中寻找）
        for line in lines[:5]:
            if '先生' in line:
                info['姓名'] = line.replace('先生', '先生').strip()
                break
            elif '女士' in line:
                info['姓名'] = line.replace('女士', '女士').strip()
                break
            elif line and len(line) <= 4 and not any(char.isdigit() for char in line):
                info['姓名'] = line + '先生'  # 假设为男性
                break
        
        # 提取教育信息
        edu_lines = []
        for line in lines:
            if '大学' in line or '学院' in line or '硕士' in line or '博士' in line or '本科' in line:
                if len(line) < 100:  # 避免过长的行
                    edu_lines.append(line)
                    if len(edu_lines) >= 2:
                        break
        
        if edu_lines:
            info['教育'] = ' | '.join(edu_lines[:2])
        
        # 提取工作经验
        exp_keywords = ['年经验', '年工作', '工作经历', '工作', '经验']
        for line in lines:
            if any(keyword in line for keyword in exp_keywords):
                info['工作经验'] = line[:80]
                break
        
        # 提取投资经验
        inv_keywords = ['投资经验', 'PE', 'VC', '投资经理', '投资总监']
        for line in lines:
            if any(keyword in line for keyword in inv_keywords):
                if '投资经验' not in info:
                    info['投资经验'] = line[:80]
                break
        
        # 提取当前职位
        position_keywords = ['投资经理', '投资总监', '副总裁', '高投', '高级经理']
        for line in lines:
            if any(keyword in line for keyword in position_keywords):
                info['当前职位'] = line[:60]
                break
        
        # 提取领域信息
        domain_keywords = ['AI', '人工智能', '低空', '航天', '商业航天', '半导体', '新能源', '硬科技']
        domains_found = []
        for line in lines:
            for keyword in domain_keywords:
                if keyword in line and keyword not in domains_found:
                    domains_found.append(keyword)
                    if len(domains_found) >= 3:
                        break
        
        if domains_found:
            info['领域'] = ', '.join(domains_found)
        
        # 提取薪资期望
        salary_keywords = ['k', 'K', '薪', '薪资', '期望']
        for line in lines:
            if any(keyword in line for keyword in salary_keywords) and ('k' in line or 'K' in line):
                info['薪资期望'] = line[:50]
                break
        
        print(f"  提取到: {info.get('姓名', '未知')}")
        if '教育' in info:
            print(f"  教育: {info['教育'][:60]}...")
        if '当前职位' in info:
            print(f"  职位: {info['当前职位']}")
        
        return info
        
    except Exception as e:
        print(f"  提取失败: {e}")
        return {'编号': candidate_num, '状态': f'失败: {e}'}

def main():
    print("="*80)
    print("高效提取剩余8位候选人关键信息")
    print("="*80)
    
    # 获取所有截图
    image_dir = "/root/.openclaw/media/inbound/"
    image_files = sorted(glob.glob(os.path.join(image_dir, "*.jpg")))
    
    print(f"找到 {len(image_files)} 张截图")
    print(f"已分析: 截图1-2")
    print(f"待分析: 截图3-{len(image_files)}")
    
    # 分析剩余截图（3-10）
    all_candidates = []
    
    # 候选人1-2（已确认）
    all_candidates.append({
        '编号': 1,
        '姓名': '林先生',
        '教育': '清华大学硕士+本科（电气工程）',
        '工作经验': '工作5年以上',
        '投资经验': '一级投资3年',
        '当前职位': '某并购基金高投',
        '领域': '新能源、半导体、AI',
        '薪资期望': '35-45kx16薪',
        '状态': '已确认'
    })
    
    all_candidates.append({
        '编号': 2,
        '姓名': '待确认（南京大学+伯克利背景）',
        '教育': '南京大学本科（微电子）+加州大学伯克利分校硕士',
        '工作经验': '工作8年以上',
        '投资经验': '4年8个月投资经验',
        '当前职位': '国资私募股权投资机构投资经理',
        '领域': 'AI基础设施、AI模型、智能制造、量子计算',
        '薪资期望': '40-60kx14薪',
        '状态': '已确认'
    })
    
    # 提取剩余候选人（3-10）
    for i in range(3, len(image_files) + 1):
        image_path = image_files[i-1]  # 索引从0开始
        candidate_info = extract_key_info_from_image(image_path, i)
        all_candidates.append(candidate_info)
    
    # 输出汇总
    print(f"\n{'='*80}")
    print("所有候选人信息汇总")
    print(f"{'='*80}")
    
    print(f"\n📊 统计:")
    success_count = sum(1 for c in all_candidates if c.get('状态') in ['成功', '已确认'])
    print(f"  总候选人: {len(all_candidates)}")
    print(f"  成功提取: {success_count}")
    print(f"  失败: {len(all_candidates) - success_count}")
    
    # 显示所有候选人摘要
    print(f"\n📋 候选人摘要:")
    for candidate in all_candidates:
        print(f"\n候选人{candidate['编号']}: {candidate.get('姓名', '待确认')}")
        if candidate.get('状态') == '已确认':
            print(f"  ✅ 已确认信息")
        elif candidate.get('状态') == '成功':
            print(f"  📝 OCR提取信息")
        else:
            print(f"  ❌ {candidate.get('状态', '提取失败')}")
            continue
        
        if '教育' in candidate:
            print(f"  教育: {candidate['教育'][:80]}...")
        if '当前职位' in candidate:
            print(f"  职位: {candidate['当前职位']}")
        if '领域' in candidate:
            print(f"  领域: {candidate['领域']}")
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/vc_recruiter/猎头评估系统/所有候选人信息汇总.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("猎聘网10位候选人信息汇总\n")
        f.write("="*80 + "\n")
        f.write(f"提取时间: 2026-03-07\n")
        f.write(f"总候选人: {len(all_candidates)}\n")
        f.write(f"成功提取: {success_count}\n")
        f.write(f"失败: {len(all_candidates) - success_count}\n\n")
        
        for candidate in all_candidates:
            f.write(f"\n候选人 {candidate['编号']}\n")
            f.write(f"姓名: {candidate.get('姓名', '待确认')}\n")
            f.write(f"状态: {candidate.get('状态', '未知')}\n")
            
            for key in ['教育', '工作经验', '投资经验', '当前职位', '领域', '薪资期望']:
                if key in candidate:
                    f.write(f"{key}: {candidate[key]}\n")
            
            f.write("-" * 40 + "\n")
    
    print(f"\n💾 所有信息已保存到: {output_file}")
    
    # 下一步建议
    print(f"\n{'='*80}")
    print("下一步建议")
    print(f"{'='*80}")
    
    print(f"\n🚀 立即行动:")
    print(f"  1. 人工验证: 候选人3-10的OCR提取信息")
    print(f"  2. 优先联系: 候选人1和2（已确认优秀）")
    print(f"  3. 初步筛选: 基于提取信息快速筛选候选人3-10")
    
    print(f"\n🔧 系统改进:")
    print(f"  1. 图像预处理: 提高OCR识别准确率")
    print(f"  2. 信息提取模板: 标准化简历解析")
    print(f"  3. 批量处理优化: 并行处理多个截图")

if __name__ == "__main__":
    main()