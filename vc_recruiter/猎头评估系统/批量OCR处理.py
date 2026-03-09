#!/usr/bin/env python3
"""
批量OCR处理10张截图 - 100%基于事实
"""

import subprocess
import os
import glob
import time

def run_ocr_on_all_images():
    """批量运行OCR并保存结果"""
    print("="*80)
    print("批量OCR处理10张截图 - 真实识别")
    print("="*80)
    
    # 列出所有图片
    image_dir = "/root/.openclaw/media/inbound/"
    image_files = glob.glob(os.path.join(image_dir, "*.jpg"))
    
    print(f"找到 {len(image_files)} 张截图")
    
    results = []
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n{'='*40}")
        print(f"处理截图 {i}/{len(image_files)}: {os.path.basename(image_path)}")
        print(f"{'='*40}")
        
        try:
            # 运行OCR
            start_time = time.time()
            result = subprocess.run(
                ['tesseract', image_path, 'stdout', '-l', 'chi_sim+eng'],
                capture_output=True,
                text=True,
                timeout=30
            )
            elapsed = time.time() - start_time
            
            if result.stdout:
                text = result.stdout.strip()
                print(f"✅ OCR成功 ({elapsed:.1f}s)")
                print(f"   文本长度: {len(text)} 字符")
                
                # 提取关键信息预览
                lines = text.split('\n')
                print(f"   总行数: {len(lines)}")
                
                # 显示前5行有意义的内容
                print(f"   预览（前5行）:")
                for j, line in enumerate(lines[:5]):
                    if line.strip():
                        print(f"     {j+1}. {line[:80]}...")
                
                results.append({
                    'file': os.path.basename(image_path),
                    'text': text,
                    'lines': len(lines),
                    'success': True
                })
            else:
                print(f"⚠️  OCR返回空文本")
                results.append({
                    'file': os.path.basename(image_path),
                    'text': '',
                    'lines': 0,
                    'success': False,
                    'error': '空文本'
                })
                
        except subprocess.TimeoutExpired:
            print(f"❌ OCR超时 (30秒)")
            results.append({
                'file': os.path.basename(image_path),
                'text': '',
                'lines': 0,
                'success': False,
                'error': '超时'
            })
        except Exception as e:
            print(f"❌ OCR失败: {e}")
            results.append({
                'file': os.path.basename(image_path),
                'text': '',
                'lines': 0,
                'success': False,
                'error': str(e)
            })
    
    # 保存结果
    output_dir = "/root/.openclaw/workspace/vc_recruiter/猎头评估系统/OCR真实结果/"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存详细结果
    detail_file = os.path.join(output_dir, "OCR详细结果.txt")
    with open(detail_file, 'w', encoding='utf-8') as f:
        f.write("猎聘网截图OCR真实识别结果\n")
        f.write("="*80 + "\n")
        f.write(f"处理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总截图数: {len(image_files)}\n")
        f.write(f"成功识别: {sum(1 for r in results if r['success'])}\n")
        f.write(f"识别失败: {sum(1 for r in results if not r['success'])}\n")
        f.write("\n" + "="*80 + "\n\n")
        
        for result in results:
            f.write(f"文件: {result['file']}\n")
            f.write(f"状态: {'✅ 成功' if result['success'] else '❌ 失败'}\n")
            if result.get('error'):
                f.write(f"错误: {result['error']}\n")
            if result['success']:
                f.write(f"文本长度: {result['lines']} 行\n")
                f.write("OCR文本:\n")
                f.write(result['text'])
                f.write("\n")
            f.write("\n" + "-"*80 + "\n\n")
    
    # 保存摘要
    summary_file = os.path.join(output_dir, "OCR结果摘要.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("OCR结果摘要 - 关键信息提取\n")
        f.write("="*80 + "\n\n")
        
        for i, result in enumerate(results, 1):
            if result['success']:
                f.write(f"候选人 {i} ({result['file']}):\n")
                
                # 提取关键信息
                text = result['text']
                
                # 查找姓名
                name_candidates = []
                lines = text.split('\n')
                for line in lines[:10]:
                    line = line.strip()
                    if line and len(line) <= 4 and '先生' not in line and '女士' not in line:
                        name_candidates.append(line)
                
                if name_candidates:
                    f.write(f"  可能姓名: {name_candidates[0]}\n")
                
                # 查找教育背景
                edu_keywords = ['硕士', '博士', '本科', '大学', '学院', 'top', '985', '211']
                edu_lines = []
                for line in lines:
                    if any(keyword in line for keyword in edu_keywords):
                        edu_lines.append(line.strip())
                
                if edu_lines:
                    f.write(f"  教育背景: {edu_lines[0][:100]}...\n")
                
                # 查找工作经验
                exp_keywords = ['年经验', '年工作', '工作经历', '投资经验']
                exp_lines = []
                for line in lines:
                    if any(keyword in line for keyword in exp_keywords):
                        exp_lines.append(line.strip())
                
                if exp_lines:
                    f.write(f"  工作经验: {exp_lines[0][:100]}...\n")
                
                # 查找当前职位
                position_keywords = ['投资经理', '投资总监', '高级经理', '副总裁']
                for line in lines:
                    if any(keyword in line for keyword in position_keywords):
                        f.write(f"  当前职位: {line.strip()[:100]}...\n")
                        break
                
                f.write("\n")
    
    print(f"\n{'='*80}")
    print("OCR处理完成")
    print(f"{'='*80}")
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\n📊 统计:")
    print(f"  总截图: {len(image_files)}")
    print(f"  成功识别: {success_count}")
    print(f"  失败: {len(image_files) - success_count}")
    
    print(f"\n💾 结果已保存:")
    print(f"  详细结果: {detail_file}")
    print(f"  结果摘要: {summary_file}")
    
    return results

def main():
    results = run_ocr_on_all_images()
    
    # 读取并显示摘要
    summary_file = "/root/.openclaw/workspace/vc_recruiter/猎头评估系统/OCR真实结果/OCR结果摘要.txt"
    if os.path.exists(summary_file):
        print(f"\n{'='*80}")
        print("OCR结果摘要:")
        print(f"{'='*80}")
        with open(summary_file, 'r', encoding='utf-8') as f:
            print(f.read())

if __name__ == "__main__":
    main()