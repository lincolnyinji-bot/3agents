#!/usr/bin/env python3
"""
简易猎头Agent - 无外部依赖版本
每天运行一次，处理收件箱中的简历
"""

import os
import sys
import json
import glob
import time
import subprocess
from datetime import datetime
from typing import List, Dict

def setup_environment():
    """设置工作环境"""
    workspace = "/root/.openclaw/workspace/vc_recruiter/猎头评估系统"
    
    directories = [
        "岗位模板",
        "评估结果",
        "简历输入/收件箱",
        "简历输入/已处理",
        "简历输入/存档"
    ]
    
    for directory in directories:
        full_path = os.path.join(workspace, directory)
        os.makedirs(full_path, exist_ok=True)
    
    return workspace

def load_templates(workspace: str) -> Dict:
    """加载岗位模板"""
    templates_dir = os.path.join(workspace, "岗位模板")
    templates = {}
    
    # 如果模板目录为空，创建默认模板
    if not os.listdir(templates_dir):
        create_default_templates(templates_dir)
    
    # 加载YAML模板
    template_files = glob.glob(os.path.join(templates_dir, "*.yaml"))
    
    for template_file in template_files:
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单解析（实际应该用yaml库）
                lines = content.split('\n')
                template_name = lines[0].replace('岗位名称:', '').strip()
                templates[template_name] = content
        except Exception as e:
            print(f"加载模板失败 {template_file}: {e}")
    
    return templates

def create_default_templates(templates_dir: str):
    """创建默认模板"""
    default_templates = {
        "泛硬科技投资总监.yaml": """岗位名称: 泛硬科技投资总监
岗位描述: 硬科技领域投资总监，专注AI、半导体、新能源、商业航天等方向
否决标准:
  学历: 硕士及以上学历，理工科背景
  经验: 5年以上硬科技产业或投资经验
  投资经验: 3年以上PE/VC投资经验
评估权重:
  教育背景: 25
  工作经验: 25
  投资经验: 30
  领域匹配: 20
领域专注: AI/半导体/新能源/商业航天/低空经济
薪资范围: 80-200万
级别要求: 总监/副总裁级别
创建时间: 2026-03-07""",
        
        "AI投资经理.yaml": """岗位名称: AI投资经理
岗位描述: 人工智能方向投资经理，专注大模型、AI应用、AI基础设施
否决标准:
  学历: 硕士及以上学历，计算机/电子相关专业
  经验: 3年以上AI相关经验
  投资经验: 2年以上投资经验
评估权重:
  教育背景: 20
  工作经验: 25
  投资经验: 25
  AI经验: 30
领域专注: 大模型/AI应用/AI基础设施/具身智能
薪资范围: 50-120万
级别要求: 经理/高级经理
创建时间: 2026-03-07"""
    }
    
    for filename, content in default_templates.items():
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"创建默认模板: {filename}")

def run_ocr(image_path: str) -> Dict:
    """运行OCR识别"""
    try:
        print(f"OCR处理: {os.path.basename(image_path)}")
        
        cmd = ['tesseract', image_path, 'stdout', '-l', 'chi_sim+eng']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            text = result.stdout.strip()
            
            # 提取关键信息
            candidate_info = extract_candidate_info(text)
            candidate_info['来源文件'] = os.path.basename(image_path)
            candidate_info['OCR时间'] = datetime.now().strftime('%H:%M:%S')
            
            return candidate_info
        else:
            return {"状态": "OCR失败", "文件": os.path.basename(image_path)}
            
    except Exception as e:
        return {"状态": f"OCR失败: {str(e)}", "文件": os.path.basename(image_path)}

def extract_candidate_info(ocr_text: str) -> Dict:
    """从OCR文本提取候选人信息"""
    info = {
        "姓名": "待确认",
        "教育": "",
        "工作经验": "",
        "投资经验": "",
        "领域": "",
        "OCR摘要": ocr_text[:300] + "..." if len(ocr_text) > 300 else ocr_text
    }
    
    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
    
    # 提取姓名
    for line in lines[:5]:
        if '先生' in line:
            info['姓名'] = line
            break
        elif '女士' in line:
            info['姓名'] = line
            break
    
    # 提取教育
    for line in lines:
        if '大学' in line or '学院' in line or '硕士' in line or '博士' in line:
            info['教育'] = line[:100]
            break
    
    # 提取工作经验
    for line in lines:
        if '年经验' in line or '年工作' in line or '工作经历' in line:
            info['工作经验'] = line[:80]
            break
    
    # 提取投资经验
    for line in lines:
        if '投资经验' in line or 'PE' in line or 'VC' in line:
            info['投资经验'] = line[:80]
            break
    
    # 提取领域
    domains = []
    domain_keywords = ['AI', '人工智能', '低空', '航天', '半导体', '新能源']
    for line in lines:
        for keyword in domain_keywords:
            if keyword in line and keyword not in domains:
                domains.append(keyword)
                if len(domains) >= 3:
                    break
    
    if domains:
        info['领域'] = ', '.join(domains)
    
    return info

def evaluate_candidate(candidate: Dict, template_name: str) -> Dict:
    """评估候选人"""
    score = 0
    
    # 学历评分
    if candidate.get('教育'):
        edu = candidate['教育']
        if '清华' in edu or '北大' in edu:
            score += 25
        elif '985' in edu or '211' in edu:
            score += 20
        elif '硕士' in edu or '博士' in edu:
            score += 15
    
    # 经验评分
    if candidate.get('工作经验'):
        exp = candidate['工作经验']
        if '5年' in exp or '6年' in exp:
            score += 25
        elif '7年' in exp or '8年' in exp:
            score += 30
        elif '3年' in exp or '4年' in exp:
            score += 20
    
    # 投资经验评分
    if candidate.get('投资经验'):
        inv = candidate['投资经验']
        if '3年' in inv or '4年' in inv:
            score += 30
        elif '5年' in inv or '6年' in inv:
            score += 35
        elif '2年' in inv:
            score += 25
    
    # 确定结果
    if score >= 80:
        result = "强烈推荐"
    elif score >= 70:
        result = "推荐"
    elif score >= 50:
        result = "可考虑"
    else:
        result = "不推荐"
    
    return {
        "候选人": candidate,
        "匹配分数": score,
        "评估结果": result,
        "评估时间": datetime.now().strftime('%H:%M:%S')
    }

def process_inbox(workspace: str) -> List[Dict]:
    """处理收件箱中的简历"""
    inbox_dir = os.path.join(workspace, "简历输入/收件箱")
    processed_dir = os.path.join(workspace, "简历输入/已处理")
    
    # 支持的图片格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    
    candidates = []
    
    for ext in image_extensions:
        image_files = glob.glob(os.path.join(inbox_dir, f"*{ext}"))
        
        for image_file in image_files:
            print(f"处理简历: {os.path.basename(image_file)}")
            
            # OCR识别
            candidate_info = run_ocr(image_file)
            
            if candidate_info.get('状态') == 'OCR失败':
                print(f"  ⚠️ OCR失败: {candidate_info.get('文件')}")
            else:
                candidates.append(candidate_info)
                print(f"  ✅ 提取信息: {candidate_info.get('姓名')}")
            
            # 移动文件
            processed_path = os.path.join(processed_dir, os.path.basename(image_file))
            os.rename(image_file, processed_path)
    
    return candidates

def generate_report(workspace: str, candidates: List[Dict], evaluations: List[Dict]):
    """生成评估报告"""
    results_dir = os.path.join(workspace, "评估结果")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(results_dir, f"评估报告_{timestamp}.md")
    
    # 统计
    total = len(evaluations)
    recommended = sum(1 for e in evaluations if e['评估结果'] in ['强烈推荐', '推荐'])
    
    # 生成报告内容
    report_lines = []
    
    # 标题
    report_lines.append(f"# 🎯 猎头Agent评估报告")
    report_lines.append(f"## 报告时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    report_lines.append("")
    
    # 统计摘要
    report_lines.append("## 📊 统计摘要")
    report_lines.append(f"- 处理时间: {datetime.now().strftime('%H:%M:%S')}")
    report_lines.append(f"- 处理简历: {total}份")
    report_lines.append(f"- 推荐候选人: {recommended}人")
    report_lines.append(f"- 岗位模板: 泛硬科技投资总监")
    report_lines.append("")
    
    # 推荐名单
    if recommended > 0:
        report_lines.append("## 🚀 推荐候选人名单")
        
        for i, eval_item in enumerate(evaluations, 1):
            if eval_item['评估结果'] in ['强烈推荐', '推荐']:
                candidate = eval_item['候选人']
                report_lines.append(f"### {i}. {candidate.get('姓名', '未知')}")
                report_lines.append(f"- 匹配分数: {eval_item['匹配分数']}分")
                report_lines.append(f"- 评估结果: {eval_item['评估结果']}")
                
                if candidate.get('教育'):
                    report_lines.append(f"- 教育背景: {candidate['教育']}")
                if candidate.get('工作经验'):
                    report_lines.append(f"- 工作经验: {candidate['工作经验']}")
                if candidate.get('投资经验'):
                    report_lines.append(f"- 投资经验: {candidate['投资经验']}")
                if candidate.get('领域'):
                    report_lines.append(f"- 专注领域: {candidate['领域']}")
                
                report_lines.append("")
    else:
        report_lines.append("## ℹ️ 今日无推荐候选人")
        report_lines.append("今日处理的简历中未发现符合条件的候选人。")
        report_lines.append("")
    
    # 处理详情
    report_lines.append("## 📝 处理详情")
    report_lines.append(f"- 输入文件夹: {os.path.join(workspace, '简历输入/收件箱')}")
    report_lines.append(f"- 已处理文件夹: {os.path.join(workspace, '简历输入/已处理')}")
    report_lines.append(f"- 报告文件: {report_file}")
    report_lines.append("")
    
    report_lines.append("---")
    report_lines.append("**生成系统**: 自动化猎头Agent")
    report_lines.append("**版本**: 简易版")
    
    # 写入文件
    report_content = "\n".join(report_lines)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📄 报告已生成: {report_file}")
    return report_file

def main():
    """主函数"""
    print("="*60)
    print("🤖 自动化猎头Agent - 简易版")
    print("="*60)
    
    # 设置环境
    workspace = setup_environment()
    
    # 处理时间
    start_time = datetime.now()
    print(f"开始时间: {start_time.strftime('%H:%M:%S')}")
    print(f"工作目录: {workspace}")
    print()
    
    # 1. 处理收件箱
    print("📥 检查收件箱...")
    candidates = process_inbox(workspace)
    
    if not candidates:
        print("✅ 收件箱为空，无新简历需要处理")
        return
    
    print(f"✅ 发现 {len(candidates)} 份新简历")
    print()
    
    # 2. 评估候选人
    print("📊 评估候选人...")
    evaluations = []
    
    for candidate in candidates:
        evaluation = evaluate_candidate(candidate, "泛硬科技投资总监")
        evaluations.append(evaluation)
        
        name = candidate.get('姓名', '未知')
        score = evaluation['匹配分数']
        result = evaluation['评估结果']
        
        print(f"  {name}: {score}分 - {result}")
    
    # 按分数排序
    evaluations.sort(key=lambda x: x['匹配分数'], reverse=True)
    print()
    
    # 3. 生成报告
    print("📄 生成评估报告...")
    report_file = generate_report(workspace, candidates, evaluations)
    
    # 4. 输出摘要
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    recommended = sum(1 for e in evaluations if e['评估结果'] in ['强烈推荐', '推荐'])
    
    print("\n" + "="*60)
    print("🎯 处理完成！")
    print("="*60)
    print(f"📊 统计:")
    print(f"  总简历数: {len(candidates)}")
    print(f"  推荐人数: {recommended}")
    print(f"  处理时间: {duration:.1f}秒")
    print(f"  报告文件: {report_file}")
    
    if recommended > 0:
        print(f"\n🚀 推荐候选人:")
        for i, eval_item in enumerate(evaluations[:5], 1):
            if eval_item['评估结果'] in ['强烈推荐', '推荐']:
                candidate = eval_item['候选人']
                name = candidate.get('姓名', '未知')
                score = eval_item['匹配分数']
                print(f"  {i}. {name} - {score}分")
    
    print("="*60)

if __name__ == "__main__":
    # 如果指定了文件夹参数，处理指定文件夹
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        if os.path.exists(folder_path):
            print(f"处理指定文件夹: {folder_path}")
            # 这里可以添加处理指定文件夹的逻辑
        else:
            print(f"文件夹不存在: {folder_path}")
    else:
        # 正常运行
        main()